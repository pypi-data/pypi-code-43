import os
import glob
import platform

from xml.etree import ElementTree as ET

from mcutk.apps.decorators import build
from mcutk.apps.idebase import IDEBase, BuildResult, DEFAULT_MCUTK_WORKSPACE
from mcutk.apps import eclipse
from mcutk.util import run_command
from mcutk.elftool import transform_elf_basic


class APP(IDEBase):
    """Represent MCUXpressoIDE.
    """


    """
    MCUXpressoIDE exitcode Definition:
    --------------
        - 0 - no errors
        - 1 - no application has been found (i.e. -run option is wrong)
        - 2 - a hard internal error has occurred
        - 3 - the command line -run option returned with errors (e.g., validation, project creation, project build, etc...)
        - 4 - the command line -run option returned with warnings (e.g., validation, compile, link, etc...)
    """
    EXITCODE = {
        0 : 'PASS',
        1 : 'APP Error',
        2 : 'Internal Errors' ,
        3 : 'Errors',
        4 : 'Warnings'
    }


    OSLIST = ['Windows', "Linux", "Darwin"]


    def __init__(self, path, *args, **kwargs):
        super(APP, self).__init__("mcux", path, *args, **kwargs)
        self.builder = get_executable(self.path)



    @property
    def is_ready(self):
        return os.path.exists(self.builder)



    @build
    def build_project(self, project, target, logfile, **kwargs):
        """Return a string about the build command line.

        Arguments:
            project {mcux.Project} -- mcux project object
            target {str} -- target name
            logfile {str} -- log file path
            workspace {str} -- workspace directory

        Returns:
            string -- build commandline


        MCUXpressoIDE command line:

        - SDK Packages mode:

        Usage: <install path>/mcuxpressoide
            -application com.nxp.mcuxpresso.headless.application
            -consoleLog -noSplash
            -data             <path/to/your/workspace/folder/to/use>
            [-run  <command>  <path/to/your/build.properties> | -help <command>]

            Available commands:
                sdk.validate            Validate content of SDK(s)
                partsupport.install     Install part support from one or more SDK.
                toolchain.options       Show the supported options in the MCUXpressoIDE toolchains
                example.build           Create/build examples from one or more SDK or an examples XML definition file.
                list.probes             List all supported probes
                project.build           Create/build projects from one or more SDK.
                example.options         Check examples options.
                list.parts              List all installed MCUs

        - Eclipse mode
        """
        workspace = kwargs.get('workspace')

        if not os.path.exists(workspace):
            os.makedirs(workspace)

        file_dir = None

        # SDK package
        if project.is_package:
            # if workspace is default, properties file will save to system temps.
            # otherwise store the properties file to user's workspace
            if DEFAULT_MCUTK_WORKSPACE not in workspace:
                file_dir = workspace

            properties_file = project.gen_properties(target, file_dir)
            buildcmd = [
                self.builder,
                "--launcher.suppressErrors",
                "-noSplash",
                "-consoleLog",
                "-application",
                "\"com.nxp.mcuxpresso.headless.application\"",
                "-data",
                workspace,
                "-run",
                "example.build",
                properties_file
            ]

        # eclipse project
        else:
            buildcmd = eclipse.generate_build_cmdline(
                self.builder,
                workspace,
                project.prjdir,
                project.name,
                target,
                cleanbuild=False)

        if logfile:
            buildcmd.append('>> "{}" 2>&1'.format(logfile))

        return " ".join(buildcmd)




    def programming(self, board, prjdir, target, file, **kwargs):
        """MCUXPressoIDE programming file to board.

        User must prepare a folder to involve the flash driver and device parts xml.
        """
        from mcutk.debugger.redlink import RedLink

        gdbpath = kwargs.get('gdbpath')
        redlink = RedLink(self.path + '/ide', version=self.version)
        redlink.gdbpath = gdbpath
        redlink.template_root = prjdir
        redlink.set_board(board)
        return redlink.flash(file)



    def elftool(self, type, in_file, out_file):
        """Call <mcuxpressoide>/ide/tools/bin/arm-none-eabi-objcopy to convert."""

        objcopy_exe = os.path.join(self.path, 'ide/tools/bin/arm-none-eabi-objcopy')
        if os.name == 'nt':
            objcopy_exe += '.exe'

        return transform_elf_basic(type, in_file, out_file, objcopy_exe)




    @staticmethod
    def default_install_directory():
        """MCUXpressoIDE default installation directory"""

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
            <mcux.APP object>
        """
        version, path = get_latest()
        if path:
            return APP(path, version=version)
        else:
            return None



    @staticmethod
    def verify(path):
        """Check the mcux installation path if it is valid!"""

        executable = get_executable(path)
        return os.path.exists(executable)







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






def get_executable(path):
    """Return mcuxpresso executable"""

    osname = platform.system()

    if osname == "Windows":
        return  os.path.join(path, "ide/mcuxpressoidec.exe").replace("\\", "/")

    elif osname == "Linux":
        return os.path.join(path , "ide/mcuxpressoide")

    elif osname == "Darwin":
        return os.path.join(path , "ide/MCUXpressoIDE.app/Contents/MacOS/mcuxpressoide")








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
        mcux_pool = [dir for dir in os.listdir(parent_dir) if "MCUXpressoIDE" in dir]
        if not mcux_pool:
            return None, None

        mcux_pool.sort()
        foldername = mcux_pool[-1]
        version = foldername.replace("MCUXpressoIDE_", "")
        path = parent_dir + foldername
        return version, path

    #==============================================================
    elif osname == "Linux":
        dirlist = os.listdir("/usr/local/")
        mcux_pool = [edir for edir in dirlist if "mcuxpressoide" in edir]
        if not mcux_pool:
            return None, None
        maxversion = max(mcux_pool)
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
