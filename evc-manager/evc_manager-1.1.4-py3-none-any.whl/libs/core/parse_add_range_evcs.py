""" Module created to handle requests for VLAN ranges """


from copy import deepcopy


def check_consistency_single_evc(evc):
    """ Check consistency for one EVC"""

    values = list()
    for uni in evc["unis"]:

        if not isinstance(uni["tag"]["value"], list):
            raise ValueError("Incorrect range format. Must be a list")
        if len(uni["tag"]["value"]) != 2:
            raise ValueError("Incorrect range format. Must have two values")

        first = uni["tag"]["value"][0]
        last = uni["tag"]["value"][1]
        values.append(last - first)

    first = values[0]
    for i in range(len(values)):
        if first != values[i]:
            raise ValueError("UNIs need range with the same number of VLANs")
    del values


def check_consistency(evcs):
    """ Check consistency for all EVCs"""
    for evc in evcs:
        check_consistency_single_evc(evc)


def create_evcs_from_range(evc):
    """ Create individual EVCs from a single EVC range.
    We create a template because we will only change the name and the value.
    """
    template = deepcopy(evc)
    evc_list = list()
    first = evc["unis"][0]["tag"]["value"][0]
    last = evc["unis"][0]["tag"]["value"][1]
    num_new_evcs = last - first + 1
    num_unis = len(evc["unis"])
    for i in range(num_new_evcs):
        new_evc = deepcopy(template)
        new_evc["name"] = "%s_%s" % (template["name"], i)
        for j in range(num_unis):
            new_value = template["unis"][j]["tag"]["value"][0] + i
            new_evc["unis"][j]["tag"]["value"] = new_value
        evc_list.append(new_evc)
        del new_evc

    return evc_list


def process_add_range(original_evcs):
    """ Create all EVC ranges. A YAML file might have more than
    just one EVC range """

    check_consistency(original_evcs)

    new_evcs = list()
    for evc in original_evcs:
        new_evcs += create_evcs_from_range(evc)

    return new_evcs
