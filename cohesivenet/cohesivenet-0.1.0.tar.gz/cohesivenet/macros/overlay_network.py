from cohesivenet import util


def segment_overlay_clients(client, groups=None, number_groups=None, group_ratios=None):
    """[summary]

    Arguments:
        client {[type]} -- [description]
        local_cidr {[type]} -- [description]

    Keyword Arguments:
        gateway {[type]} -- [description] (default: {None})

    Returns:
        Dict - {
            '[group-name-1]': [],
            '[group-name-2]': ['107']
        }
    """
    assert (
        groups or number_groups or group_ratios
    ), "groups (List[str]) or number_groups (int) or group_ratios (Dict[str, flaot]) must be provided"
    license_data = client.licensing.get_license().response
    clients = [client.ip_address for client in license_data.topology.clients]

    if groups:
        partitions = util.partition_list_groups(clients, len(groups))
        return {group_name: partitions[i] for i, group_name in enumerate(groups)}
    elif number_groups:
        partitions = util.partition_list_groups(clients, number_groups)
        return {
            "group_%d" % (i + 1): partitions[i]
            for i, partition in enumerate(partitions)
        }
    else:
        ratios = list(group_ratios.values())
        partitions = util.partition_list_ratios(clients, ratios)
        return {group: partitions[str(ratio)] for group, ratio in group_ratios.items()}
