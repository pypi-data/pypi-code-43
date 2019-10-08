"""
Summary:
    libtools Project-level Defaults and Settings

    - **Local Default Settings**: Local defaults for your specific installation are derived from settings found in:

Module Attributes:
    - user_home (TYPE str):
        $HOME environment variable, present for most Unix and Unix-like POSIX systems
    - config_dir (TYPE str):
        directory name default for stsaval config files (.stsaval)
    - config_path (TYPE str):
        default for stsaval config files, includes config_dir (~/.stsaval)
"""

import os
import inspect
import platform
import logging
from libtools._version import __version__

logger = logging.getLogger(__version__)
logger.setLevel(logging.INFO)


# --  project-level DEFAULTS  ------------------------------------------------


def os_parityPath(path):
    """
    Converts unix paths to correct windows equivalents.
    Unix native paths remain unchanged (no effect)
    """
    path = os.path.normpath(os.path.expanduser(path))
    if path.startswith('\\'):
        return 'C:' + path
    return path


def _userhome():
    """Returns os specific home dir for current user"""
    try:
        if platform.system() == 'Linux':
            return os.path.expanduser('~')

        elif platform.system() == 'Windows':
            username = os.getenv('username')
            return 'C:\\Users\\' + username

        elif platform.system() == 'Java':
            print('Unable to determine home dir, unsupported os type')
            sys.exit(1)
    except OSError as e:
        raise e

try:

    user_home = _userhome()

    if user_home is None:
        user_home = '/tmp'

except KeyError as e:
    logger.critical(
        '%s: %s variable is required and not found in the environment' %
        (inspect.stack()[0][3], str(e)))
    raise e

else:
    # project
    PACKAGE = 'libtools'
    LICENSE = 'GPL v3'
    LICENSE_DESC = 'General Public License v3'

    # logging parameters
    enable_logging = False
    log_mode = 'FILE'
    log_filename = PACKAGE + '.log'
    log_dir = os_parityPath(os.path.join(user_home, 'logs'))
    log_path = os_parityPath(os.path.join(log_dir, log_filename))

    if not os.path.exists(log_dir):
        os.makedirs(log_dir)

    local_config = {
        "PROJECT": {
            "PACKAGE": PACKAGE,
            "CONFIG_VERSION": __version__,
            "HOME": user_home,

        },
        "LOGGING": {
            "ENABLE_LOGGING": enable_logging,
            "LOG_FILENAME": log_filename,
            "LOG_DIR": log_dir,
            "LOG_PATH": log_path,
            "LOG_MODE": log_mode,
            "SYSLOG_FILE": False
        }
    }
