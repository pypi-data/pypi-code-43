import os
import glob
import platform

from xml.etree import ElementTree as ET

from mcutk.apps.decorators import build
from mcutk.apps.idebase import IDEBase, BuildResult
from mcutk.apps.eclipse import generate_build_cmdline
from mcutk.debugger.redlink import RedLink



class APP(IDEBase):
    """LPCxpresso IDE for pymcutk."""

    EXITCODE = {
        0 : 'PASS',
        1 : 'APP Error',
        2 : 'Internal Errors' ,
        3 : 'Errors',
        4 : 'Warnings'
    }

    OSLIST = ['Windows', "Linux", "Darwin"]

    def __init__(self, path, *args, **kwargs):
        super(APP, self).__init__("lpcx", path, *args, **kwargs)
        self.builder = self.__builder_init()

    def __builder_init(self):
        """set self.builder value"""
        osname = platform.system()
        builder = ""
        if osname == "Windows":
            builder =  os.path.join(self._path, "ide", "mcuxpressoidec.exe").replace("\\", "/")
        elif osname == "Linux":
            builder = os.path.join(self._path , "ide", "mcuxpressoide")
        elif osname == "Darwin":
            builder = os.path.join(self._path , "ide", "MCUXpressoIDE.app", "Contents", "MacOS", "mcuxpressoide")

        if not os.path.exists(builder):
            if osname == "Windows":
                builder = os.path.join(self._path, "ide", "lpcxpressoidec.exe").replace("\\", "/")
            elif osname == "Linux":
                builder = os.path.join(self._path , "ide", "lpcxpressoide")
            elif osname == "Darwin":
                builder = os.path.join(self._path , "ide", "MCUXpressoIDE.app", "Contents", "MacOS", "lpcxpressoide")

        return builder

    @property
    def is_ready(self):
        return os.path.exists(self.builder)

    @build
    def build_project(self, project, target, logfile, **kwagrs):
        """Return a string about the build command line.

        Arguments:
            project {lpcx.Project} -- lpcx project object
            target {str} -- target name
            logfile {str} -- log file path
            workspace {str} -- default is ~/lpcx_mcutk

        Returns:
            string -- build commandline
        """
        workspace = kwagrs.get("workspace")
        # self.builder = self.builder.replace('\\', '\\\\').replace('/', '\\\\')
        buildcmd = generate_build_cmdline(self.builder, workspace, project.prjdir, project.name, target)

        if logfile:
            buildcmd.append('>> "{}" 2>&1'.format(logfile))

        return " ".join(buildcmd)


    @staticmethod
    def default_install_directory():
        """
        get default installation directory for mcux
        """
        installation_table = {
            "Windows": "C:/nxp/",
            "Linux": "/usr/local/",
            "Darwin": "/Applications",
        }
        osname = platform.system()
        return installation_table[osname]

    @staticmethod
    def get_latest():
        """Search and return a latest IAR instance in system

        Returns:
            <iar.APP object>
        """
        version, path = get_latest()
        if path:
            return APP(path, version=version)
        else:
            return None

    @staticmethod
    def verify(path):
        """
        check the mcux installation path if it is valid!
        """
        osname = platform.system()

        if osname == "Windows":
            return  os.path.join(path, "ide", "mcuxpressoidec.exe").replace("\\", "/")

        elif osname == "Linux":
            return os.path.join(path , "ide", "mcuxpressoide")

        elif osname == "Darwin":
            return os.path.join(path , "ide", "MCUXpressoIDE.app", "Contents", "MacOS", "mcuxpressoide")


    @staticmethod
    def parse_build_result(exitcode, logfile=None):
        """Parse mcuxpressoide build result

        Arguments:
            exitcode {int} -- the exit code of mcuxpressoide process
            logfile {string} -- a file contains the output from mcuxpressoide.

        Returns:
            <BuildResult object> -- the build result

        Notes:
        ---------------------
        mcuxpressoide exit code
            noerror warnnings: 0
            erros: none-zero

        Parser the log file by search the keyword: "Total number of warnings: <>".
        """
        status = APP.EXITCODE.get(exitcode, "Errors")
        return BuildResult.map(status)



def get_latest():
    """Find the latest installation of mcux in system.

    Windows:
        Installed at: in C:/nxp
    Linux:
        Installed at: /usr/local/
        Use Following command:
        >>> dpkg -L mcuxpressoide | grep /usr/local/mcuxpressoide | head -1
        >>> /usr/local/mcuxpressoide-1.0.0.277

    MAC:
        Installed at: /Applications
    """
    osname = platform.system()
    path, version = None, None

    if osname == "Windows":
        parent_dir = APP.default_install_directory()
        if not os.path.exists(parent_dir):
            return None, None

        installations_list = [dir for dir in os.listdir(parent_dir) if "MCUXpressoIDE" in dir]
        if not installations_list:
            return None, None

        installations_list.sort()
        foldername = installations_list[-1]
        version = foldername.replace("MCUXpressoIDE_", "")
        path = parent_dir+foldername
        return version, path

    #==============================================================
    elif osname == "Linux":
        dirlist = os.listdir("/usr/local/")
        verlist = [edir for edir in dirlist if "mcuxpressoide" in edir]
        if not verlist:
            return None, None
        maxversion = max(verlist)
        version = maxversion.replace("mcuxpressoide-", "")
        path = "/usr/local/" + maxversion
        return version, path

    #==============================================================
    elif osname == "Darwin":
        dirlist = os.listdir("/Applications")
        mcux_pool = [dirname for dirname in dirlist if "MCUXpressoIDE" in dirname]
        if not mcux_pool:
            return None, None

        mcux_pool.sort()
        latest_installation_dirname = mcux_pool[-1]
        path = "/Applications/%s"%latest_installation_dirname
        version = latest_installation_dirname.replace("MCUXpressoIDE_", "")
        return version, path
