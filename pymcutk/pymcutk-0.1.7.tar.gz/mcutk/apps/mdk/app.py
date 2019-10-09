import os
import re
import glob
import time
import zipfile
import logging
import platform
import subprocess
import os.path as Path
try:
    import ConfigParser
except ImportError:
    import configparser as ConfigParser

from mcutk.apps.decorators import build
from mcutk.apps.idebase import IDEBase, BuildResult
from mcutk.apps.mdk.project import Project
from mcutk.util import copydir, run_command


class APP(IDEBase):
    """This class wrap ARM-MDK to provide ease-to-use interface for outside.

    """
    OSLIST = ['Windows']


    EXITCODE = {
        0:	"PASS",
        1:	"Warnings",
        2:	"Errors",
        3:	"Fatal Errors",
        11:	"Cannot open project file for writing",
        12:	"Device with given name in not found in database",
        13:	"Error writing project file",
        15:	"Error reading import XML file",
    }


    @staticmethod
    def get_latest():
        """Return an instance by latest version"""

        if os.name == 'nt':
            path, version = get_latest()
            if path:
                return APP(path, version=version)
        return None




    @staticmethod
    def parse_build_result(exitcode, logfile=None):
        """Parse the build result form exitcode & logfile

        Arguments:
            exitcode {int} -- build process exit code
            logfile {int} -- build log file

        Returns:
            BuildResult object
        """
        status = APP.EXITCODE.get(exitcode, "Errors")
        return BuildResult.map(status)



    @staticmethod
    def verify(path):
        osname = platform.system()
        if osname == "Windows":
            return os.path.exists(path + "/UV4/UV4.exe")

        elif osname in ["Linux", "Darwin"]:
            raise OSError("Not Defined")




    def __init__(self, *args, **kwargs):
        super(APP, self).__init__("mdk", *args, **kwargs)
        self.builder = os.path.join(self.path, "UV4", "UV4.exe").replace('\\', '/')




    @property
    def is_ready(self):
        return os.path.exists(self.builder)



    @build
    def build_project(self, project, target, logfile=None, **kwargs):
        """
        Generate build commands.

        Arguments:
            project: uv4 Project object.
            target: target name.
            logfile: path to log file.

        Returns:
            string -- build commands line

        """
        target = project.map_target(target)
        project.set_build_options()
        buildcmd = '{0} -r {1} -q -j0 -t "{2}"'.format(
            self.builder,
            project.prjpath,
            target)

        if logfile:
            buildcmd += ' -o %s'%logfile
        return buildcmd



    # def create_project(self):
    #     buildcmd = '{0} -r "{1}" -j0 -o "{2}" -t "{3}"'.format(
    #         self.builder,
    #         projpath, buildlog, target)




    def install_pack(self, packpath):
        """Install cmsis pack by PackUnzip.exe
        """
        packTool = self.path + "/PackUnzip.exe"
        if os.path.exists(packTool) is False:
            raise IOError("No such file: %s"%packTool)
        ret = os.system("{0} -i {1} --skip-check --no-gui".format(packTool, packpath))
        if ret:
            print("Exit Code: %s"%ret)
            os._exit(ret)
        else:
            print("Successfully")





    def enable_license(self, license):
        """Enable uv4 flex license."""
        cf = ConfigParser.ConfigParser()
        tools_ini = os.path.dirname(self.path)+"/TOOLS.ini"
        cf.read(tools_ini)
        cf.set("UV2", "FLEX", license)
        cf.write(open(tools_ini, "w"))



    def transform_elf(self, type, in_file, out_file):
        """Call <keil_root>/ARM/ARMCC/bin/fromelf.exe."""

        supported_types = {
            'bin': '--bin',
            'srec': '--m32combined',
            'ihex': '--i32',
        }

        if type not in supported_types:
            raise ValueError('unsupported type')

        type_option = supported_types.get(type)

        fromelf_tool = Path.join(self.path, 'ARM/ARMCC/bin/fromelf.exe')
        fromelf_command = [
            fromelf_tool,
            type_option,
            '--output',
            out_file,
            in_file
        ]
        return subprocess.call(fromelf_command) == 0






    def programming(self, board, prjdir, target, file, action='program', **kwargs):
        """MDK programming.

        Arguments:
            prjdir {str} -- project directory
            usbid {str} -- usbid
            target {str} -- app target
            file {str} -- file path
            action {str}  -- program/erase
            timeout {int}  -- timeout for action
        Returns:
            Tuple -- (returncode, output)
        """
        timeout = kwargs.get('timeout', 120)
        # is_to_flash = kwargs.get('flash', True)
        project = Project.frompath(prjdir)

        if action == "erase":
            for t in project.targets:
                if 'flexspi_nor' in t:
                    target = t
                    break

        target = project.map_target(target)
        is_debug_mode = project.set_debugging_options(target, sn=board.usbid, debugfile=file, action=action)

        if not is_debug_mode:
            cmd = '{0} -f {1} -t "{2}"'.format(self.builder, project.prjpath, target)
        else:
            cmd = '{0} -d {1} -t "{2}"'.format(self.builder, project.prjpath, target)
        return run_command(cmd, timeout=timeout)




def get_latest():
    osname = platform.system()
    if osname == "Windows":
        try:
            import _winreg as winreg
        except ImportError:
            import winreg

        root_key_path = r"SOFTWARE\Wow6432Node\Keil\Products\MDK"
        try:
            key_object = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, root_key_path, 0, winreg.KEY_READ)
            path = winreg.QueryValueEx(key_object, "Path")[0].replace('\\', '/')
            keilroot = os.path.dirname(path)
            path = keilroot
            version = winreg.QueryValueEx(key_object, "Version")[0]
            winreg.CloseKey(key_object)

            cf = ConfigParser.ConfigParser()
            cf.read(keilroot + "/TOOLS.ini")
            ver = cf.get("ARM", "VERSION")
            if ver not in version:
                logging.debug("Registry record is: %s, but actually it is: %s", version, ver)

            return path, ver

        except Exception as e:
            logging.debug("could not found Keil installation in windows register!")

        keilroot = "C:/Keil_v5"
        tools_ini = keilroot+"/TOOLS.ini"
        if not os.path.exists(tools_ini):
            return None, None

        cf = ConfigParser.ConfigParser()
        cf.read(tools_ini)
        version = cf.get("ARM", "VERSION")
        path = keilroot

        return path, version

    else:
        raise OSError("ARM MDK(Keil) is unavaliable on such os!")

