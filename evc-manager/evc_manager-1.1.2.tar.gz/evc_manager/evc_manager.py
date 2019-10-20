"""
    SDN EVC manager
    Main module
"""

from libs.core.cli import CliOptions
from libs.core.log import info
from libs.core.log import warn
from libs.core.log import process_result
from libs.core.import_evc import import_evcs
from libs.core.parse_add_range_evcs import process_add_range
from libs.core.evc_list import EvcsList
from libs.outputs.printing import print_evcs
from backends.kytos_eline import KytosEline
from backends.oess import Oess


class EvcManager(object):
    """ EVC Manager Class """

    def __init__(self, cli_option=None):
        self.cli_options = CliOptions() if not cli_option else cli_option
        self.backend = Oess() if self.cli_options.is_oess else KytosEline()
        self.backend.authenticate()
        # We are always required to know the existing EVCs
        self.current_evcs = EvcsList(evc_list=self.backend.get_evcs())

    def list_evcs(self):
        """ List EVCs (CLI option -L) """
        return self.current_evcs.to_dict()

    def add_evc(self, new_evc):
        """ Add an EVC """
        found_evc = self.current_evcs.find(new_evc)
        if not found_evc:
            info('Creating EVC %s...' % new_evc.name)
            return self.backend.add_evc(new_evc)
        else:
            return {'result': 'error',
                    'msg': 'EVC %s already exists.' % new_evc.name}

    def add_evcs(self, new_evcs=None):
        """ Add EVCs (CLI option -A) """
        if not new_evcs:
            new_evcs = import_evcs(source_file=CliOptions().file_content)
        results = []
        for new_evc in new_evcs:
            results.append(self.add_evc(new_evc))
        return process_result(results)

    def add_evcs_range(self):
        """ Add range of EVCs (CLI option -R) """
        file_content = process_add_range(CliOptions().file_content)
        new_evcs = import_evcs(source_file=file_content)
        self.add_evcs(new_evcs=new_evcs)

    def change_evcs(self):
        """ TODO: Change EVCs (CLI option -C) """
        evcs_to_change = import_evcs(source_file=CliOptions().file_content)

        results = list()
        for evc_to_change in evcs_to_change:
            found_evc = self.current_evcs.find(evc_to_change)
            if not found_evc:
                info('EVC %s not found' % evc_to_change.name)
            else:
                warn('Creating EVC %s' % evc_to_change.name)
            results.append(self.backend.add_evc(evc_to_change))
        return process_result(msg=results)

    def delete_evc(self, evc_to_delete):
        """ Delete an EVC """
        found_evc = self.current_evcs.find(evc_to_delete)
        if found_evc:
            return self.backend.delete_evc(found_evc)
        else:
            return {'result': 'error',
                    'msg': 'EVC %s not found/deleted.' % evc_to_delete.name}

    def delete_evcs(self):
        """ Delete EVCs (CLI option -D) """

        if not CliOptions().is_delete:
            msg = {'result': 'error', 'msg': 'No EVCs found to delete.'}
            return process_result(msg)

        evcs_to_delete = import_evcs(source_file=CliOptions().file_content)

        results = []
        for evc_to_delete in evcs_to_delete:
            results.append(self.delete_evc(evc_to_delete))
        return process_result(results)

    def move_evcs(self):
        """ Move EVCs (CLI option -O) """
        self.backend.move_evcs()

    def run(self):
        """ Run """
        if self.cli_options.is_list:
            return self.list_evcs()
        elif self.cli_options.is_add:
            return self.add_evcs()
        elif self.cli_options.is_add_range:
            return self.add_evcs_range()
        elif self.cli_options.is_change:
            return self.change_evcs()
        elif self.cli_options.is_delete:
            return self.delete_evcs()
        elif self.cli_options.is_move:
            return self.move_evcs()

        return process_result(msg='Invalid CLI option selected.')


if __name__ == '__main__':
    evc_manager = EvcManager()
    final_result = evc_manager.run()
    if evc_manager.cli_options.is_list:
        print_evcs(final_result)
    elif evc_manager.cli_options.is_add:
        for result in final_result['results']['msgs']:
            info(result['msg'])
    elif evc_manager.cli_options.is_change:
        for result in final_result['results']['msgs']:
            info(result['msg'])
    elif evc_manager.cli_options.is_delete:
        for result in final_result['results']['msgs']:
            info(result['msg'])
    elif evc_manager.cli_options.is_move:
        for result in final_result['results']['msgs']:
            info(result['msg'])
