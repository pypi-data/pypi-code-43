

import os
import re
import glob
import logging
import platform
import subprocess

from distutils.version import LooseVersion
from mcutk.apps.decorators import build
from mcutk.apps.idebase import IDEBase, BuildResult
from mcutk.elftool import transform_elf_basic
from mcutk.apps.cmake import generate_build_cmdline


class APP(IDEBase):
    """GNU ARM GCC compiler.

    CMake and ARM-GCC build explanation:
        - Generate Makefile:
        >>> cmake -DCMAKE_TOOLCHAIN_FILE={path}/armgcc.cmake -G "{MinGW|Unix} Makefiles" -DCMAKE_BUILD_TYPE=debug

        - Start build with make tool or mingw32-make:
        >>> make -C "<path-to-makefile-directory>" -j4
        >>> mingw32-make -C "<path-to-makefile-directory>" -j4

        - Compile. Armgcc compiler will be called to compile in makefile.

    CMake is a cross-platform build system generator. Projects specify their build
    process with platform-independent CMake listfiles included in each directory
    of a source tree with the name CMakeLists.txt. Users build a project by using
    CMake to generate a build system for a native tool on their platform.

    GNU Make is a tool which controls the generation of executables and other non-source
    files of a program from the program's source files. Make gets its knowledge of how to
    build your program from a file called the makefile, which lists each of the non-source
    files and how to compute it from other files. When you write a program, you should
    write a makefile for it, so that it is possible to use Make to build and install the
    program.


    """
    OSLIST = ["Windows","Linux","Darwin"]


    def __init__(self, path, *args, **kwargs):
        super(APP, self).__init__("armgcc", path, *args, **kwargs)


    @property
    def is_ready(self):
        return os.path.exists(self.path)



    @build
    def build_project(self, project, target, logfile, **kwargs):
        """Return a command line string for armgcc. The build commands
        are packaging into a shell/bat script.

        Arguments:
            project {armgcc.Project} -- armgcc project object
            target {string} -- target name
            logfile {string} -- log file path

        Returns:
            string -- commandline string.
        """
        os.environ["ARMGCC_DIR"] = self.path
        return generate_build_cmdline(project, target, logfile)



    def transform_elf(self, type, in_file, out_file):
        """Convert ELF to specific type.
        Called <mcutk>/bin/arm-none-eabi-objcopy to do the job.

        Supported types: bin, ihex, srec.

        Arguments:
            in_file {str} -- path to elf file.
            out_file {str} -- output file
            type {str} -- which type you want to convert.

        Raises:
            ReadElfError -- Unknown elf format will raise such error
            Exception -- Convert failed will raise exception

        Returns:
            bool
        """
        executor = os.path.join(self.path, 'bin/arm-none-eabi-objcopy')
        if os.name == 'nt':
            executor += '.exe'

        return transform_elf_basic(type, in_file, out_file, executor)



    @staticmethod
    def verify(path):
        '''
        verify the path of compiler is avaliable
        '''
        return os.path.exists(path)



    @staticmethod
    def get_latest():
        """Search and return a latest armgcc instance from system.

        Returns:
            <armgcc.APP object>
        """
        path, version = get_armgcc_latest()
        if path:
            return APP(path, version=version)
        else:
            return None


    @staticmethod
    def parse_build_result(exitcode, logfile):
        """GNU make exits with a status of zero if all makefiles were successfully
        parsed and no targets that were built failed. A status of one will be
        returned if the -q flag was used and  make  determines  that a target
        needs to be rebuilt. A status of two will be returned if any errors
        were encountered.
        """

        if exitcode != 0:
            return BuildResult.map("error")

        if not logfile:
            return BuildResult.map("pass")

        p = re.compile(r'warning:', re.I)

        with open(logfile) as f:
            for line in f:
                if p.search(line) != None:
                    return BuildResult.map("warning")

        return BuildResult.map("pass")


    @staticmethod
    def default_install_path():
        default_path_table = {
            "Windows": "C:/Program Files (x86)/GNU Tools ARM Embedded",
            "Linux": "/usr/local",
            "Darwin": "/usr/local",
        }
        osname = platform.system()
        return default_path_table[osname]




def _scan_windows_register():
    try:
        import _winreg as winreg
    except ImportError:
        import winreg

    root_key_path = r"SOFTWARE\Wow6432Node\ARM\GNU Tools for ARM Embedded Processors"
    try:
        key_object = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, root_key_path)
        path = winreg.QueryValueEx(key_object, "InstallFolder")[0].replace('\\', '/')
        version = path.split("/")[-1].replace(" ", "-")
        winreg.CloseKey(key_object)
        return path, version
    except WindowsError:
        pass

    return None, None




def get_armgcc_latest():
    """Get the latest armgcc version

    Returns:
        tuple -- (path, version)
    """
    path, version = None, None
    osname = platform.system()

    if osname == "Windows":
        path, version = _scan_windows_register()
        if path:
            return path, version

        logging.debug("Could not found ARM GCC installation in windows register!"\
        "Trying to scan in default installation directory!")

    root_path = APP.default_install_path()
    if not os.path.exists(root_path):
        return None, None

    if osname == "Windows" and not os.path.exists(root_path):
        root_path = "C:/Program Files/GNU Tools ARM Embedded"

    return get_armgcc_latest_version(root_path)



def get_armgcc_latest_version(rootpath):
    osname = platform.system()
    versions_dict = {}
    armgcc_rootfolders = []

    if "Windows" == osname:
        armgcc_rootfolders = os.listdir(rootpath)
    else:
        try:
            s = subprocess.check_output("ls {0} | grep gcc-arm-none-eabi".format(rootpath), shell=True)
            armgcc_rootfolders = s.split('\n')
        except subprocess.CalledProcessError:
            return None, None

    for per_folder in armgcc_rootfolders:
        if not os.path.isdir(os.path.join(rootpath, per_folder)) or '' == per_folder:
            continue

        version_content = os.popen("\"{}\" --version".format(os.path.join(rootpath, per_folder, "bin", "arm-none-eabi-gcc"))).read()
        ret = re.search("\d\.\d\.\d", version_content)
        if None != ret:
            versions_dict[ret.group()] = os.path.join(rootpath, per_folder)

    latest_v = sorted(versions_dict.keys(), key=lambda v:LooseVersion(v))[-1]
    return versions_dict[latest_v], latest_v



