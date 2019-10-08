"""
Summary.

    Text file object detection using Linux binary dependency

Use:

    Not working
"""
from shutil import which
from libtools import logger


def is_text(path):
    """
        Checks filesystem object using *nix file application provided
        with most modern Unix and Linux systems.  Returns False if
        file object cannot be read

    Args:
        :path (str): filesystem path ending in a file object
            Example:  '/usr/bin/python3.6' or '/home/joeuser/image.png'

    Returns:
        - True || False, TYPE: bool
        - Returns None if os binary dependency ('file' program) not found

    """
    if not which('file'):
        logger.warning('required dependency missing: Unix application "file". Exit')
        return None

    try:

        f = os.popen('file -bi ' + path, 'r')
        contents = f.read().strip()

    except Exception:
        return False
    return contents.startswith('text')
