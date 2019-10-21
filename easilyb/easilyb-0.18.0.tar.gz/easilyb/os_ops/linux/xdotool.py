from easilyb.commands import run_command_ex1
import logging
logger = logging.getLogger(__name__)


def get_mouse_location():
    try:
        return_code, output = run_command_ex1(['xdotool', 'getmouselocation', '--shell'])
        if return_code != 0:
            return None
        return {k.split('=')[0]:k.split('=')[1] for k in output.decode(errors='replace').split('\n') if '=' in k}
    except:
        logger.error('Error getting mouse location', exc_info=True)
        return None
