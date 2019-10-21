from .evc_manager import EvcManager
from .libs.outputs.printing import print_evcs
from .libs.core.log import info


if __name__ == "__main__":
    """ """
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
