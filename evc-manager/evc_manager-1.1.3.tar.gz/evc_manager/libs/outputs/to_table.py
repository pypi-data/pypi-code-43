""" Print circuits in a table format. It might filter per link if desired"""


from prettytable import PrettyTable
from ..core.import_evc import import_evcs
from ..core.cli import CliOptions


def get_filters_from_cli():
    """ Query CliOptions and process input filters if any.

    :return: target_nni and filter_per_type
    """

    options = CliOptions().to_table
    filter_per_type = options.split(':')[0].lower()
    target_nni = options.split(':')[1]
    if target_nni.lower() == 'ANY'.lower():
        target_nni = None

    return target_nni, filter_per_type


def filter_per_nni(evc):
    """ Filter per NNI """
    target_nni, filter_per_type = get_filters_from_cli()

    if target_nni:
        if filter_per_type == 'any':
            if CliOptions().verbose not in ['info']:
                print('No filtering for primary or backup paths')
            if target_nni in evc.get_primary_path():
                return True
            elif target_nni in evc.get_backup_path():
                return True

        elif filter_per_type == 'primary' and target_nni in evc.get_primary_path():
            if CliOptions().verbose not in ['info']:
                print('Filtering for primary path only')
            return True

        elif filter_per_type == 'backup' and target_nni in evc.get_backup_path():
            if CliOptions().verbose not in ['info']:
                print('Filtering for backup path only')
            return True

        else:
            return False

    else:
        return True


def print_evcs_table(evcs):
    """ Print circuits in a table format. It might filter per link if desired"""
    evcs_list = import_evcs(from_dict=evcs)
    count = 0

    t = PrettyTable(['Circuit Name', 'Primary Path', 'Backup Path', 'Current Path'])

    for evc in evcs_list:
        if filter_per_nni(evc):
            count += 1
            current_path = 'Primary' if not evc.is_using_backup_path() else 'Backup'
            t.add_row([evc.name, evc.get_primary_path(), evc.get_backup_path(), current_path])

    if count:
        print(t)
    print('Total # of Circuits: %s' % count)
