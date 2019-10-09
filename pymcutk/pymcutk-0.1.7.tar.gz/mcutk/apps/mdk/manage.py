import os
import glob
import platform
import logging
import subprocess
try:
    import ConfigParser
except ImportError:
    import configparser as ConfigParser

from .app import APP, get_latest
from mcutk.cmsispack import install_pack_unzip
from mcutk.apps.decorators import appinstall


@appinstall
def install(installer, license, install_path='C:\Keil_v5'):
    """Install uv4/mdk.

    Arguments:
        installer {string} -- path to installer
        license {[type]} -- network license
        install_path {string} -- path to install location, default is "C:\Keil_v5"

    Returns:
        tuple -- (path, version)
    """
    try:
        _silent_install(installer, license, install_path)
    except subprocess.CalledProcessError:
        logging.error("failed to install %s"%installer)
        return False

    # install the packs under ./ARM/PACK/.Download
    uv4 = APP(install_path, "v")
    prepack = os.path.join(install_path, "ARM/PACK/.Download")
    packages = glob.glob(prepack+"/*.pack")
    for pack in packages:
        uv4.install_pack(pack)

    path, version = get_latest()

    return path, version





def _silent_install(installer, license, install_path='C:\Keil_v5'):
    """silent install MDK

    Arguments:
        installer {string} -- path to installer
        license {string} -- network license
        install_path {string} -- path to install location, default is "C:\Keil_v5"

    Raise Exceptions:
        When the unzip unsuccessful, it will raise an Error

    Automated installation:
        This only support windows, there are three steps in the progress:
            1. unzip installer file.
            2. generate TOOLS.ini by use the template SETUP.ini.
            3. install .pack under ARM/PACK/.DOWNLOADS
    """
    logging.info("install path: %s", install_path)

    uv4_ini = {
        'RTEPATH': install_path + r"\ARM\PACK",
        'TOOL_VARIANT': 'mdk_pro_flex',
        'FLEX': license,
        'FLEX_USE': '1',
        'FLEX_VARIANT':'mdk_pro',
        'LEGACY_CM': '1',
        'ORGANIZATION': "NXP",
        'NAME': '"Test", "Team"',
        'EMAIL': "dapeng@nxp.com"
    }

    osname = platform.system()
    if osname != "Windows":
        raise SystemError("Windows only")

    curdir = os.path.dirname(os.path.abspath(__file__)).replace("\\", "/")
    unzip_tool = os.path.abspath(curdir + "../../bin/7z.exe")

    # unzip uv4 installer.
    subprocess.check_call("{0} x -o{1} -y {2}".format(unzip_tool, install_path, installer))

    # Create and configure the TOOLS.ini from SETUP.ini template
    cf = ConfigParser.ConfigParser()
    cf.read(install_path+"/SETUP.ini")
    for key, v in uv4_ini.items():
        print("set {0} {1}".format(key, v))
        cf.set("UV2", key, v)
    cf.set("ARMADS", "PATH", install_path + "\ARM\\")
    cf.write(open(install_path+"/TOOLS.ini", "w"))

    return 0
