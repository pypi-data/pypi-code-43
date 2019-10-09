from __future__ import print_function
import os
import glob
import shutil
import platform
import logging

from .app import APP
from mcutk.apps.decorators import appinstall
from mcutk.util import run_command


@appinstall
def install(installer, **kwargs):
    """Install mcuxpressoide to system, and verify the installation

    Arguments:
        installer {string} -- path to installer file

    Returns:
        tuple -- (path, version)
    """
    rc = _install(installer)
    print("  Finished run setup.exe, exit code: %s"%rc)
    if rc != 0:
        return None, None

    print("Verify installation...")
    _mcux  = APP.get_latest()

    if _mcux:
        return _mcux.path, _mcux.version

    return None, None









def _install(installer):
    """Silent installation

    Description:
        - Windows:
            MCUXpressoIDE is packed by inno tool, inno silent installation guide:
            >>> setup.exe /SILENT /DIR=<path> /NORESTART /SUPPRESSMSGBOXES /SP-

        - Linux:
            1. Unzip installer:
                >>> **.deb --noexec --target <Uncompress directory>
            2. Assign executable permission.
            3. Use dpkg to install .deb:
                >>> dpkg -i --force-all --force-depends <path to **.deb>

        - Mac:
            >>> installer -store -pkg <path to installer> -target /

    """
    osname = platform.system()
    if osname == "Windows":
        install_cmd = "start /wait {0} /SILENT /NORESTART /SUPPRESSMSGBOXES /SP-".format(installer)
        ret = run_command(install_cmd, timeout=10)[0]

        # Tiemout function only killed the cmd.exe process.
        # If mcux installer is blocked by window prompt, below
        # command will kill the real installer process to make sure it exit.
        os.system('''TASKKILL /F /T /FI" IMAGENAME eq MCUXpressoIDE_*"''')
        return ret


    elif osname == "Linux":
        setupname = os.path.basename(installer)
        # uncompress the .deb.run or .deb.bin to uncompress_dir
        uncompress_dir = os.path.join(os.path.dirname(installer), setupname.replace(".", "_"))

        # check & cretae uncompress directory
        if os.path.exists(uncompress_dir):
            shutil.rmtree(uncompress_dir, ignore_errors=True)
        os.makedirs(uncompress_dir)

        # make sure the installer has execution permission
        os.chmod(installer, 0o777)
        # extract the files from installer
        ret = os.system("{} --noexec --target {}".format(installer, uncompress_dir))
        print("Uncompressing done, exit code: %s\n"%ret)

        # Following code is commented, we will not check the return code from uncompressing.
        # But to check the *.deb file.
        # if ret != 0:
        #     print ("Uncompressing error: %s"%setupfile)
        #     return return_code

        files = glob.glob(uncompress_dir + "/*.deb")
        deb_filpath = files[0] if files else None
        if deb_filpath:
            print("Error: *.deb is not exists, probably the uncompress failed!")
            return 1

        os.chmod(deb_filpath, 0o777)
        ret = os.system("dpkg -i --force-all --force-depends {}".format(deb_filpath))

        if ret != 0:
            print("dpkg install error %s"%deb_filpath)
            return ret

        # delete uncompress directory
        shutil.rmtree(uncompress_dir, ignore_errors=True)

        os.system("apt-get -fy install --force-yes")
        return 0


    elif osname == "Darwin":
        os.chmod(installer, 0o777)
        cmd = "installer -store -pkg {} -target /".format(installer)
        return os.system(cmd)



