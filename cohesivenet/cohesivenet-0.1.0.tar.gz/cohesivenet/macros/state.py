from functools import partial as bind

from cohesivenet import data_types
from cohesivenet.macros import api_operations as api_op


class VNS3Attr(object):
    """State Attributes - more to be added
    """
    primary_private_ip = "primary_private_ip"
    secondary_private_ip = "secondary_private_ip"
    public_ip = "public_ip"
    public_dns = "public_dns"
    peer_id = "peer_id"
    asn = "asn"


def get_primary_private_ip(client, bust_cache=False):
    if not bust_cache:
        val = client.query_state(VNS3Attr.primary_private_ip)
        if val:
            return val

    val = client.config.get_config().response.private_ipaddress
    client.add_to_state(VNS3Attr.primary_private_ip, val)
    return val


def get_asn(client, bust_cache=False):
    if not bust_cache:
        val = client.query_state(VNS3Attr.asn)
        if val:
            return val

    val = client.config.get_config().response.asn
    client.add_to_state(VNS3Attr.asn, val)
    return val


def get_public_ip(client, bust_cache=False):
    if not bust_cache:
        val = client.query_state(VNS3Attr.public_ip)
        if val:
            return val

    val = client.config.get_config().response.public_ipaddress
    client.add_to_state(VNS3Attr.public_ip, val)
    return val


def get_peer_id(client, bust_cache=False):
    if not bust_cache:
        val = client.query_state(VNS3Attr.peer_id)
        if val:
            return val

    val = client.peering.get_peering_status().response.id
    client.add_to_state(VNS3Attr.peer_id, val)
    return val


_StateLibrary = {
    VNS3Attr.primary_private_ip: get_primary_private_ip,
    VNS3Attr.public_ip: get_public_ip,
    VNS3Attr.asn: get_asn,
    VNS3Attr.peer_id: get_peer_id,
}


def attribute_supported(attribute):
    return attribute in _StateLibrary


def fetch_state_attribute(
    clients, attribute, bust_cache=False
) -> data_types.BulkOperationResult:
    """Fetch state attribute for all clients

    Arguments:
        clients {List[VNS3Client]}
        attribute {str}

    Keyword Arguments:
        bust_cache {bool}

    Returns:
        [BulkOperationResult] -- [description]
    """
    assert attribute in _StateLibrary, (
        "Attribute %s not currently supported" % attribute
    )
    fetch_func = _StateLibrary.get(attribute)
    api_calls = [bind(fetch_func, client, bust_cache=bust_cache) for client in clients]
    return api_op.__bulk_call_api(api_calls, parallelize=True)
