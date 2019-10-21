from easilyb.commands import run_command_ex1
import logging
logger = logging.getLogger(__name__)


def get_active_window_id():
    try:
        return_code, output = run_command_ex1(['xprop', '-root', '_NET_ACTIVE_WINDOW'])
        if return_code != 0:
            return None
        return output.decode(errors='replace').split()[4][:-1]
    except:
        logger.error('Error getting active window id', exc_info=True)
        return None


def get_window_title(window_id):
    try:
        return_code, output = run_command_ex1(['xprop', '-id', window_id, '_NET_WM_NAME'])
        if return_code != 0:
            return None
        return output.decode(errors='replace').split('=')[1].strip()[1:-1]
    except:
        logger.error('Error getting window title', exc_info=True)
        return None


def get_window_pid(window_id):
    try:
        return_code, output = run_command_ex1(['xprop', '-id', window_id, '_NET_WM_PID'])
        if return_code != 0:
            return None
        return int(output.decode(errors='replace').split('=')[1].strip())
    except:
        logger.error('Error getting window pid', exc_info=True)
        return None