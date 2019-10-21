""" Print # of evcs per nni in a table format"""

import json
from prettytable import PrettyTable
from ..core.import_evc import import_evcs
from ..core.cli import CliOptions


def get_filters_from_cli():
    """ Query CliOptions and process input filters if any.

    :return: target_nni and filter_per_type
    """

    options = CliOptions().gen_stats_per_nni
    target_nni = options.split(':')[0]
    if target_nni.lower() == 'ANY'.lower():
        target_nni = None

    try:
        to_json = options.split(':')[1]
    except (ValueError, TypeError):
        to_json = False

    return target_nni, to_json


def print_stats_per_nni(evcs):
    """ Print # of evcs per nni """

    target_nni, format_json = get_filters_from_cli()

    evcs_list = import_evcs(from_dict=evcs)
    nnis = dict()

    t = PrettyTable(['NNI Name', '# of EVCs'])

    for evc in evcs_list:
        for paths in evc.paths:
            for nni in paths:
                if not target_nni or (target_nni and target_nni == nni.name):
                    try:
                        nnis[nni.name] += 1
                    except KeyError:
                        nnis[nni.name] = 1

    if format_json:
        print(json.dumps(nnis))
    else:
        for nni in nnis:
            t.add_row([nni, nnis[nni]])

        print(t.get_string(sortby="# of EVCs", reversesort=True))
