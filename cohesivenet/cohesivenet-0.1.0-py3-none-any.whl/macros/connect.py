from typing import List

from cohesivenet import VNS3Client, Configuration, data_types
from cohesivenet.macros import api_operations


def get_client(host, username, password, verify=False):
    """Get VNS3 API Client for host

    Arguments:
        host {str}
        username {str}
        password {str}

    Keyword Arguments:
        verify {bool} -- Verify SSL certificate (default: {False})

    Returns:
        [VNS3Client]
    """
    return VNS3Client(
        Configuration(
            host=host, username=username, password=password, verify_ssl=verify
        )
    )


def get_clients(*hosts):
    """Create VNS3Clients for host information

    Arguments:
        host {Dict} -- {
            host: str,
            username: str,
            password: str,
            verify: bool (Optional)
        }

    Returns:
        [List[VNS3Client]]
    """
    return [get_client(**host_data) for host_data in hosts]


def get_clients_common_creds(hosts, common_username, common_password, verify=False):
    """Construct clients for each host

    Arguments:
        hosts {List[str]} -- list of host strings
        common_username {str}
        common_password {str}

    Keyword Arguments:
        verify {bool} -- verify SSL for client

    Returns:
        [List[VNS3Clients]]
    """
    return [get_client(host, common_username, common_password, verify) for host in hosts]


def verify_client_connectivity(
    clients: List[VNS3Client]
) -> data_types.BulkOperationResult:
    """Verify the connectivty of provided clients by pinging API

    Arguments:
        clients {List[VNS3Client]}

    Returns:
        data_types.BulkOperationResult
    """

    def _ping_api(_client):
        return _client.sys_admin.get_ping_system()

    return api_operations.__bulk_call_client(clients, _ping_api)
