import os
import sys

try:
    input = raw_input
except NameError:
    pass

from serial.tools import list_ports

_VBOOT_TOOL_DIR = '.v_bootstrap'


def get_home_dir():
    """ Detects home dir for current user. """
    return os.path.expanduser("~")


def get_tool_dir():
    """ Returns a working dir. """
    return os.path.join(get_home_dir(), _VBOOT_TOOL_DIR)


def get_serial_devices():
    """ Gathers available devices. """
    return list_ports.comports()


def yes_no(message, answer='yes'):
    """ Shows a confirmation message. """
    yes = True, '[Y/n]'
    no = False, '[y/N]'

    answers = {'yes': yes, 'y': yes, 'no': no, 'n': no}

    if answer not in answers:
        raise ValueError("Invalid answer: {}".format(answer))

    status, prompt = answers[answer]

    while True:
        sys.stdout.write("{} {}: ".format(message, prompt))
        sign = input().lower().strip()

        if sign == '':
            break

        if sign in answers:
            status, prompt = answers[sign]
            break

    return status
