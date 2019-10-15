import os
import time
from typing import Dict

from cohesivenet import (
    VNS3Client,
    data_types,
    CohesiveSDKException,
    ApiException,
    Logger,
    UrlLib3ConnExceptions,
    HTTPStatus,
)
from cohesivenet.macros import api_operations


def fetch_keyset_from_source(client, source, token, wait_timeout=60.0):
    """fetch_keyset_from_source Put keyset by providing source controller to download keyset. This
    contains logic that handles whether or not fetching from the source fails, typically due
    to a firewall or routing issue in the underlay network (e.g. security groups and route tables).

    Pseudo-logic:
        if already in progress or successful new request:
            wait:
                if a new successful put returns: that indicates failure to download from source. return 400
                if timeout: that indicates controller is rebooting, return wait for keyset
        if keyset already exists: return keyset details

    Arguments:
        source {str} - host controller to fetch keyset from
        token {str} - secret token used when generating keyset
        wait_timeout {float} - timeout for waiting for keyset and while polling for download failure (default: 1 min)

    Raises:
        e: [description]
    """
    failure_error_str = (
        "Failed to fetch keyset for source. This typically due to a misconfigured "
        "firewall or routing issue between source and client controllers."
    )

    def is_in_progress_err(r):
        return type(r) is str and "Keyset setup in progress" in r

    def keyset_exists_err(r):
        return type(r) is str and "Keyset already exists" in r

    get_start_time = (
        lambda r: None
        if not type(r) is dict
        else r.get("response", {}).get("started_at_i")
    )

    try:
        put_response = client.config.put_keyset({"source": source, "token": token})
    except UrlLib3ConnExceptions:
        raise ApiException(
            status=HTTPStatus.SERVICE_UNAVAILABLE,
            reason="Controller unavailable. It is likely rebooting. Try client.sys_admin.wait_for_api().",
        )

    if keyset_exists_err(put_response):
        raise ApiException(status=400, reason="Keyset already exists.")

    started_time = get_start_time(put_response)
    already_in_progress = is_in_progress_err(put_response)
    Logger.info(
        message="Keyset downloading from source."
        if not already_in_progress
        else "Keyset download already in progress.",
        start_time=started_time,
    )
    polling_start = time.time()
    while time.time() - polling_start <= wait_timeout:
        try:
            duplicate_call_resp = client.config.put_keyset(
                {"source": source, "token": token}
            )
        except UrlLib3ConnExceptions:
            Logger.info(
                "API call timeout. Controller is likely rebooting. Waiting for keyset.",
                wait_timeout=wait_timeout,
            )
            return client.config.wait_for_keyset(timeout=wait_timeout)

        if keyset_exists_err(duplicate_call_resp):
            keyset_data = client.config.get_keyset()
            if not keyset_data.response:
                Logger.info(
                    "Keyset already exists. Waiting for reboot.",
                    wait_timeout=wait_timeout,
                )
                client.sys_admin.wait_for_api(
                    timeout=wait_timeout, wait_for_reboot=True
                )
                return client.config.wait_for_keyset()
            return keyset_data

        if is_in_progress_err(duplicate_call_resp):
            # this means download is in progress, but might fail. Wait and retry
            time.sleep(2.0)
            continue

        new_start = get_start_time(duplicate_call_resp)
        if (new_start and started_time) and (new_start != started_time):
            Logger.error(failure_error_str, source=source)
            raise ApiException(status=HTTPStatus.BAD_REQUEST, reason=failure_error_str)

    raise CohesiveSDKException(
        "Timeout while waiting for keyset.", host=client.host_uri, source=source
    )


def setup_controller(
    client: VNS3Client,
    topology_name: str,
    license_file: str,
    license_parameters: Dict,
    keyset_parameters: Dict,
    peering_id: int = 1,
    reboot_timeout=120,
    keyset_timeout=120,
):
    """setup_controller Set the topology name, controller license, keyset and peering ID if provided

    Arguments:
        client {VNS3Client}
        topology_name {str}
        keyset_parameters {Dict} -- UpdateKeysetRequest {
            'source': 'str',
            'token': 'str',
            'topology_name': 'str',
            'sealed_network': 'bool'
        }
        peering_id {int} -- ID for this controller in peering mesh

    Returns:
        OperationResult
    """
    current_config = client.config.get_config().response
    Logger.info("Setting topology name", name=topology_name)
    if current_config.topology_name != topology_name:
        client.config.put_config({"topology_name": topology_name})

    if not current_config.licensed:
        if not os.path.isfile(license_file):
            raise CohesiveSDKException("License file does not exist")

        license_file_data = open(license_file).read().strip()
        Logger.info("Uploading license file", path=license_file)
        client.licensing.upload_license(license_file_data)

    accept_license = False
    try:
        current_license = client.licensing.get_license().response
        accept_license = not current_license or not current_license.finalized
    except ApiException as e:
        if e.get_error_message() == "Must be licensed first.":
            accept_license = True
        else:
            raise e

    if accept_license:
        Logger.info("Accepting license", parameters=license_parameters)
        client.licensing.put_set_license_parameters(
            license_parameters
        )
        Logger.info("Waiting for server reboot.")
        client.sys_admin.wait_for_api(timeout=reboot_timeout, wait_for_reboot=True)

    current_keyset = api_operations.retry_call(
        client.config.get_keyset, max_attempts=20
    ).response
    if not current_keyset.keyset_present and not current_keyset.in_progress:
        Logger.info("Generating keyset", parameters=keyset_parameters)
        api_operations.retry_call(
            client.config.put_keyset, args=(keyset_parameters,)
        )
        Logger.info("Waiting for keyset ready")
        client.config.wait_for_keyset(timeout=keyset_timeout)
    elif current_keyset.in_progress:
        client.config.wait_for_keyset(timeout=keyset_timeout)

    current_peering_status = client.peering.get_peering_status().response
    if not current_peering_status.id and peering_id:
        Logger.info("Setting peering id", id=peering_id)
        client.peering.put_self_peering_id({"id": peering_id})
    return client


def license_clients(clients, license_file_path) -> data_types.BulkOperationResult:
    """Upload license file to all clients. These will have DIFFERENT keysets. See keyset operations
       if all controllers are to be in the same clientpack topology

    Arguments:
        clients {List[VNS3Client]}
        license_file_path {str} - full path to license file

    Returns:
        BulkOperationResult
    """
    license_file = open(license_file_path).read().strip()

    def _upload_license(_client):
        return _client.licensing.upload_license(license_file)

    return api_operations.__bulk_call_client(clients, _upload_license)


def accept_clients_license(
    clients, license_parameters
) -> data_types.BulkOperationResult:
    """Accept licenses for all. These will have DIFFERENT keysets. See keyset operations
       if all controllers are to be in the same clientpack topology. Assumes same license
       parameters will be accepted for all clients

    Arguments:
        clients {List[VNS3Client]}
        license_parameters {UpdateLicenseParametersRequest} - dict {
            'subnet': 'str',
            'managers': 'str',
            'asns': 'str',
            'clients': 'str',
            'my_manager_vip': 'str',
            'default': 'bool'
        }

    Returns:
        BulkOperationResult
    """
    def _accept_license(_client):
        return _client.licensing.put_set_license_parameters(license_parameters)

    return api_operations.__bulk_call_client(clients, _accept_license)


def fetch_keysets(clients, root_host, keyset_token, wait_timeout=80.0):
    """fetch_keysets Fetch keysets for all clients from root_host

    Arguments:
        clients {List[VNS3Client]}
        root_host {str}
        keyset_token {str}

    Returns:
        BulkOperationResult
    """

    def _fetch_keyset(_client):
        return fetch_keyset_from_source(
            _client, root_host, keyset_token, wait_timeout=wait_timeout
        )

    return api_operations.__bulk_call_client(clients, _fetch_keyset, parallelize=True)
