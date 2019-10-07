def reduce_lists:
    logger.success("depth: {} | dict in _reduce_lists: {}".format(depth_in_list, sub_dict))
    reduced_dict = dict()
    print("returned:", reduced_dict)
    for sub_key in sub_dict:
        if isinstance(sub_dict[sub_key], list):
            available_keys = dict()
            # print("sub_dict[sub_key]:", sub_dict[sub_key])
            sub_data = dict()
            for sub_element in sub_dict[sub_key]:  # sub_dict[sub_key] : film | sub_element : {title:abc}

                for element_key in sub_element:
                    # if p:
                    #     print("element_key:", element_key)

                    if element_key not in available_keys:
                        available_keys[element_key] = list()

                    if not isinstance(sub_element[element_key], (list, dict, set)):  # sub_element[element_key] : abc
                        available_keys[element_key].append(sub_element[element_key])
                        sub_data[element_key] = sub_element[element_key]

                    elif isinstance(sub_element[element_key], dict):
                        # ToDoo maybe after depth_in_list +1?
                        sub_data[element_key] = _reduce_lists(sub_element[element_key], depth_in_list)
                        if sub_data[element_key] == {'name-#text': {'Lola': {'@typ': 'w'}, 'Manni': {'@typ': 'm'}}}:
                            print("–!-!-!-")
                            print(element_key)
                            print(sub_element[element_key])
                        # logger.error(sub_element[element_key])
                        logger.error("{}, {}".format(element_key, sub_data[element_key]))
                    else:
                        sub_data[element_key] = sub_element[element_key]
                        logger.success(sub_element[element_key])
            keys_for_list_reduction = list()
            for av_key in available_keys:
                if len(available_keys[av_key]) == len(set(available_keys[av_key])):
                    keys_for_list_reduction.append(av_key)

            leading_key = str()
            if keys_for_list_reduction and isinstance(list_for_reduction, list):
                try:
                    leading_key = list_for_reduction[depth_in_list:][
                        min([list_for_reduction[depth_in_list:].index(reduction_key)
                             for reduction_key in keys_for_list_reduction
                             if reduction_key in list_for_reduction[depth_in_list:]])]
                except ValueError:
                    pass

            elif manual_selection and not leading_key:
                raise NotImplemented

            else:
                leading_key = sorted(keys_for_list_reduction)[0]

            # Todo put data together (from sub_data) and combine with list reduction

            if leading_key:
                # for sub_element in sub_data[leading_key]:
                if sub_key + "-" + leading_key not in reduced_dict:
                    reduced_dict[sub_key + "-" + leading_key] = dict()
                #     print(sub_element)
                # raise SystemExit
                print("-------")
                print(sub_dict[sub_key])
                print(sub_data)
                for sub_element in sub_dict[sub_key]:
                    try:
                        reduced_dict[sub_key + "-" + leading_key][sub_element[leading_key]] = {k: v for k, v in
                                                                                               sub_element.items() if
                                                                                               k != leading_key}
                    except AttributeError as err:
                        logger.error("{}: {}".format(err, sub_dict[sub_key]))

                print("reduced_dict:", reduced_dict)
                print("-------")


            else:
                reduced_dict[sub_key] = sub_data[sub_key]

        elif isinstance(sub_dict[sub_key], dict):
            reduced_dict[sub_key] = _reduce_lists(sub_dict[sub_key], depth_in_list)

    return reduced_dict

import configparser
def get_config_from_root(root):
    """Read the project setup.cfg file to determine Versioneer config."""
    # This might raise EnvironmentError (if setup.cfg is missing), or
    # configparser.NoSectionError (if it lacks a [versioneer] section), or
    # configparser.NoOptionError (if it lacks "VCS="). See the docstring at
    # the top of versioneer.py for instructions on writing your setup.cfg .
    setup_cfg = os.path.join(root, "setup.cfg")
    parser = configparser.SafeConfigParser()
    with open(setup_cfg, "r") as f:
        parser.readfp(f)
    VCS = parser.get("versioneer", "VCS")  # mandatory

    def get(parser, name):
        if parser.has_option("versioneer", name):
            return parser.get("versioneer", name)
        return None
    cfg = VersioneerConfig()
    cfg.VCS = VCS
    cfg.style = get(parser, "style") or ""
    cfg.versionfile_source = get(parser, "versionfile_source")
    cfg.versionfile_build = get(parser, "versionfile_build")
    cfg.tag_prefix = get(parser, "tag_prefix")
    if cfg.tag_prefix in ("''", '""'):
        cfg.tag_prefix = ""
    cfg.parentdir_prefix = get(parser, "parentdir_prefix")
    cfg.verbose = get(parser, "verbose")
    return cfg