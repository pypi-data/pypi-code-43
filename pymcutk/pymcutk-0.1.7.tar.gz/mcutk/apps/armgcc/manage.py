from __future__ import print_function
import os
import glob
import logging
import platform


from .app import APP
from mcutk.util import run_command
from mcutk.apps.decorators import appinstall





@appinstall
def install(installer, **kwargs):
    """Install Armgcc to system, and installaton verification.

    Arguments:
        installer {string} -- path to installer file

    Returns:
        tuple -- (path, version)
    """
    if _install(installer) != 0:
        return None, None

    print("Verify installation...")
    _armgcc  = APP.get_latest()
    if _armgcc:
        return _armgcc.path, _armgcc.version

    return None, None





def _install(installer):
    """Install armgcc to system

    Arguments:
        installer {string} -- path to installer file

    Returns:
        tuple -- (path, version)
    """

    default_root = {
            "Windows": "C:/Program Files (x86)/GNU Tools ARM Embedded",
            "Linux": "/usr/local",
            "Darwin": "/usr/local",
        }
    osname = platform.system()
    install_path = default_root.get(osname)

    if osname == "Windows":
        return os.system("start /wait {0} /S /NCRC".format(installer))

    elif osname == "Linux" or osname == "Darwin":
        return os.system("tar -jxvf {1} -C {2}".format( installer, install_path))
