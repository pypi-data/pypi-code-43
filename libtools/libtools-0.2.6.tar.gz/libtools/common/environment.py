"""
Summary.

    Commons Module -- Common Functionality

"""
import os
import sys
import json
import inspect
import logging
import platform
import subprocess
from shutil import which
from pathlib import Path
from libtools._version import __version__
from libtools.variables import *


logger = logging.getLogger(__version__)
logger.setLevel(logging.INFO)


def get_os(detailed=False):
    """
    Summary:
        Retrieve local operating system environment characteristics
    Args:
        :user (str): USERNAME, only required when run on windows os
    Returns:
        TYPE: dict object containing key, value pairs describing
        os information
    """
    try:

        os_type = platform.system()

        if os_type == 'Linux':
            os_detail = platform.platform()
            distribution = platform.linux_distribution()[0]
            HOME = str(Path.home())
            username = os.getenv('USER')
        elif os_type == 'Windows':
            os_detail = platform.platform()
            username = os.getenv('username') or os.getenv('USER')
            HOME = 'C:\\Users\\' + username
        else:
            logger.warning('Unsupported OS. No information')
            os_type = 'Java'
            os_detail = 'unknown'
            HOME = os.getenv('HOME')
            username = os.getenv('USER')

    except OSError as e:
        raise e
    except Exception as e:
        logger.exception(
            '%s: problem determining local os environment %s' %
            (inspect.stack()[0][3], str(e))
            )
    if detailed and os_type == 'Linux':
        return {
                'os_type': os_type,
                'os_detail': os_detail,
                'linux_distribution': distribution,
                'username': username,
                'HOME': HOME
            }
    elif detailed:
        return {
                'os_type': os_type,
                'os_detail': os_detail,
                'username': username,
                'HOME': HOME
            }
    return {'os_type': os_type}


def terminal_size(height=False):
    """
    Summary.

        Returns size of linux terminal rows, columns if
        called with height=True; else only width of terminal
        in columns is returned.

    Returns:
        columns (str, default) || rows, columns, TYPE: tuple

    """
    try:
        rows, columns = os.popen('stty size 2>/dev/null', 'r').read().split()
        if height:
            return rows, columns
        return columns
    except ValueError as e:
        if which('tput'):
            return subprocess.getoutput('tput cols')
        raise e
