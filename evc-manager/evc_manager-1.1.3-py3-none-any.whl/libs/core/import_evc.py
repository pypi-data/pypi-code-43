""" Import EVCs from a YAML file. Returns a list of
EthernetVirtualCircuit() from the file read.
"""


from ..models.evc import EthernetVirtualCircuit
from ..models.nni import NNI


def import_requested_path(requested_paths):
    """ Import requested paths

    Args:
        requested_paths: list with requested_paths.
    Returns:
        list of NNIs
    """
    paths = list()

    for links in requested_paths:
        path = list()
        for span in links:
            link = NNI()
            link.device_a = span['device_a']
            link.interface_a = span['interface_a']
            link.device_z = span['device_z']
            link.interface_z = span['interface_z']
            link.name = span['name']
            path.append(link)
            del link
        paths.append(path)
        del path
    return paths


def create_requested_path(requested_paths):
    """ When user request an EVC to be created, he provides
    only the name of the NNIs. We need to complete for him.

    Preferred_paths is a dict with 'paths'
    Preferred_paths['paths'] is a list of lists

    Args:
        requested_paths: list of NNI names
    """

    paths = list()

    for requested_path in requested_paths:
        path = list()
        for links in requested_path:
            link = NNI()
            link.name = links
            link.device_a = 'Not_Needed'
            link.interface_a = 'Not_Needed'
            link.device_z = 'Not_Needed'
            link.interface_z = 'Not_Needed'
            path.append(link)
            del link
        paths.append(path)
        del path
    return paths


def import_evcs(source_file=None, from_dict=None):
    """ Reads a YAML file or a Dict input and creates
    a list of EthernetVirtualCircuit().

    Args:
        source_file = YAML file
        from_json = JSON/dictionary
    Returns:
        list of EVCs
    """
    if source_file:
        evcs_list = source_file
    else:
        evcs_list = from_dict

    new_evc_list = list()

    for evc_json in evcs_list:

        if 'name' not in evc_json:
            raise ValueError('EVC\' name not provided')
        if 'unis' not in evc_json:
            raise ValueError('EVC\'s UNIs not provided')

        evc = EthernetVirtualCircuit()
        evc.name = evc_json['name']
        evc.import_unis(evc_json['unis'])

        # Optional Attributes:
        if 'provisioning_time' in evc_json:
            evc.provisioning_time = evc_json['provisioning_time']
        if 'decommissioning_time' in evc_json:
            evc.decommissioning_time = evc_json['decommissioning_time']
        if 'tenant' in evc_json:
            evc.tenant = evc_json['tenant']
        if 'priority' in evc_json:
            evc.priority = evc_json['priority']
        if 'external_id' in evc_json:
            evc.external_id = evc_json['external_id']
        if 'paths' in evc_json:
            if from_dict:
                evc.paths = import_requested_path(evc_json['paths'])
            else:
                paths = create_requested_path(evc_json['paths'])
                if paths:
                    evc.paths = paths
        if 'metric' in evc_json:
            evc.metrics.import_json(evc_json['metrics'])
        if 'current_config' in evc_json:
            evc.current_config.import_json(evc_json['current_config'])
        if 'notifications' in evc_json:
            # TODO: notifications
            pass
        if 'monitoring' in evc_json:
            # TODO: monitoring
            pass

        new_evc_list.append(evc)
        del evc

    return new_evc_list
