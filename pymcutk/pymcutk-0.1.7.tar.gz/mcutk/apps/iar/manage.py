from __future__ import print_function
import os
import glob
import logging

from .app import APP, get_latest
from mcutk.apps.decorators import appinstall


@appinstall
def install(installerfile, tmpdir, license):
    """install iar

    Arguments:
        installerfile {string} -- path to installer file
        tmpdir {string} -- path to tmp directory

    Returns:
        tuple -- (path, version)
    """
    rc = _install(installerfile, tmpdir)
    logging.info("finished to install, process exit code: %s", rc)
    if rc != 0:
        logging.error("Error: Installation is abnormal exit!")
        return None

    logging.info("Verify installation...")
    path, version = get_latest()


    if APP.verify(path):
        logging.info("Successfully install")
    else:
        logging.error("Verifcation is failure, probably the installation issue!")
        return None


    logging.info("Enable license...")
    iar = APP(path, version=version)
    if iar.enable_license(license):
        logging.info("Successfully enabled network license")
        return path, version
    else:
        logging.warning("Failed to enable iar license")
        return None




def _install(installerfile, tmpdir):
    '''
    Install iar on windows.

    IAR installer is packed with rar self-extract format. First of all,
    we need to use "UnRAR.exe" to extract the real installer "setup.exe".
    The setup.exe is assembled by installshield.

    Notice:
        1. setup.exe: you'd better not rename this file, if you do that, please
        don't include the number in the name! It will failed when the name
        contain number.

        2. *.iss
        The "*.iss" is a configuration for silent installation progress.
        To generate this file just run below command to record it.
            >> setup.exe /r
        Then the setup.iss will be generated and will be saved in C:/Windows.

    Arguments:
        installerfile: path of installer
        tmpdir: tmp directory

    Returns:
        int --- exit code
    '''
    curdir = os.path.dirname(os.path.abspath(__file__)).replace("\\", "/")
    unrar_tool = os.path.abspath(curdir + "../../bin/UnRAR.exe")

    # Extract setup.exe from installerfile
    cmd = "{0} -y {1} ew {2}".format(unrar_tool, installerfile, tmpdir)
    logging.info(cmd)
    ret = os.system(cmd)
    if ret != 0:
        return ret

    setupfile = os.path.join(tmpdir, "setup.exe")
    if not os.path.exists(setupfile):
        logging.error("Fatal Error. No such file: %s", setupfile)
        return 1


    iss_folder = os.path.join(curdir, "iss")
    # get latest iss template file by modified time
    iss_files = glob.glob(iss_folder+"/*.iss")
    iss_tempalate = max(iss_files, key=os.path.getctime)

    # create iar.iss in tmp dir
    content = None
    tmp_issfile = os.path.dirname(setupfile).replace("\\", "/")+"/iar.iss"

    with open(iss_tempalate, 'r') as fileobj:
        content = fileobj.read()

    with open(tmp_issfile, "w") as issfileobj:
        issfileobj.write(content)

    logging.debug(setupfile)
    logging.debug(tmp_issfile)

    return os.system("start /wait {0} /s /sms /f1{1}".format(setupfile, tmp_issfile))



