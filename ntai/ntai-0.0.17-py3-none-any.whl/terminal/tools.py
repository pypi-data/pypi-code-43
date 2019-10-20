import os, sys, subprocess, uuid
from .utils import variable_name, error_message
from .popen import POPEN_DEFAULTS

def arg(name, val, short=True, equal=False, flag=False):
    dashes = '-' if short else '--'
    sep = '=' if equal else ' '

    arg_str = ''

    if val is not None:
        if not flag:
            arg_str = '{}{}{}{}'.format(dashes, name, sep, val)
        else:
            if val:
                arg_str = '{}{}'.format(dashes, name)

    return arg_str.split(' ') if arg_str != '' else []

def clean_command(command:list):
    cleaned = [
        sub
        for part in command
        for sub in part.split(' ')
        if sub != ''
    ]
    return cleaned



def process(command:list, stdin:str, popen_options={}):
    '''
    Arguments:
        command (list): a list of strings indicating the command and its
            arguments to spawn as a subprocess.

        stdin (str): passed as stdin to the subprocess. Assumed to be utf-8
            encoded.

        popen_options (dict): used to configure the subprocess.Popen command

    Returns:
        stdout, stderr
    '''
    command = clean_command(command)
    popen_config = POPEN_DEFAULTS.copy()
    popen_config.update(popen_options)
    try:
        pid = subprocess.Popen(args = command, **popen_config)
        stdout_data, stderr_data = pid.communicate(stdin)
    except OSError as err:
        error_message(command, err)
        sys.exit(1)
    if pid.returncode != 0:
        error_message(command, 'pid code {}'.format(pid.returncode), stdout_data, stderr_data)
    return stdout_data, stderr_data
