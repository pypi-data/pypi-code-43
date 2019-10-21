from easilyb.commands import run_command_ex1
import logging
logger = logging.getLogger(__name__)


def get_process_cmd(pid):
    try:
        return_code, output = run_command_ex1(['ps', '--no-headers', '-fw', '--pid', str(pid)])
        if return_code != 0:
            return None
        return output.decode(errors='replace').split()[7].strip()
    except:
        logger.error('Error getting process cmd', exc_info=True)
        return None