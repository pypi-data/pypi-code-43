from functools import partial as bind

from cohesivenet import data_types
from cohesivenet.clouds import networkmath
from cohesivenet.macros import api_operations, state


def create_local_gateway_route(client, local_cidr, **route_kwargs):
    """[summary]

    Arguments:
        client {[type]} -- [description]
        local_cidr {[type]} -- [description]

    Keyword Arguments:
        gateway {[type]} -- [description] (default: {None})

    Returns:
        OperationResult
    """
    route = dict(
        **{
            "cidr": local_cidr,
            "description": "Local Underlay Network Routing",
            "interface": "eth0",
            "gateway": networkmath.get_default_gateway(local_cidr),
            "advertise": "False",
            "metric": 0,
        },
        **route_kwargs
    )
    return api_operations.try_api_call(
        client.routing.post_create_route, route, should_raise=True
    )


def create_route_advertisements(
    clients, local_subnets
) -> data_types.BulkOperationResult:
    """create_route_advertisements Create a route advertisement for controllers network

    Arguments:
        clients {List[VNS3Client]}
        local_subnets {List[str]} - order should correspond with clients list

    Returns:
        data_types.BulkOperationResult
    """
    assert len(clients) == len(
        local_subnets
    ), "clients list length must equal local_subnets list length"

    invalid = []
    for index, client in enumerate(clients):
        private_ip = state.get_primary_private_ip(client)
        if not networkmath.subnet_contains_ipv4(private_ip, local_subnets[index]):
            invalid.append("%s not in %s" % (private_ip, local_subnets[index]))

    if len(invalid):
        raise AssertionError(
            "Invalid subnets provided for clients: %s." % ",".join(invalid)
        )

    def _create_route(_client, subnet):
        return _client.routing.post_create_route(
            {
                "cidr": subnet,
                "description": "Local subnet advertisement",
                "advertise": True,
                "gateway": "",
            }
        )

    bound_api_calls = [
        bind(_create_route, client, local_subnets[index])
        for index, client in enumerate(clients)
    ]

    return api_operations.__bulk_call_api(bound_api_calls)
