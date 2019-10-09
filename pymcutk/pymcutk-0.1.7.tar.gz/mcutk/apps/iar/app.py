from __future__ import print_function
import os
import re
import glob
import time
import platform
import zipfile
import subprocess
import logging
import multiprocessing
import os.path as Path
from distutils.version import LooseVersion

from mcutk.apps.decorators import build
from mcutk.apps.idebase import IDEBase, BuildResult
from mcutk.util import copydir, run_command

class APP(IDEBase):
    """
    IAR Workbench interface implementation.
    This class inherit from IDEBase, and it has the ability to build project,
    and parse the build result.

    Create an instance:
        (1) search in windows registry:
            >>> iar = APP.get_latest()
            >>> print iar.version

        (2) from api
            >>> iar = APP("C:/Program Files(x86)/IAR systems/IAR Workbench-8.11/", version="8.11")
            >>> print iar.version

    """

    OSLIST = ["Windows"]


    EXITCODE = {
        0:	"PASS",
        1:	"Warnings",
        2:	"Errors",
        3:	"Fatal Errors",
    }



    @staticmethod
    def get_latest():
        """Search and return a latest IAR instance in system

        Returns:
            <iar.APP object>
        """
        if os.name == 'nt':
            path, version = get_latest()
            if path:
                return APP(path, version=str(version))
        return None


    @staticmethod
    def parse_build_result(exitcode, logfile):
        """Parse iar build result

        Arguments:
            exitcode {int} -- the exit code of iarbuild process
            logfile {string} -- a file contains the output from iarbuild.

        Returns:
            <BuildResult object> -- the build result


        Notes:
        ---------------------
        iarbuild.exe exit code
            noerror warnnings: 0
            erros: none-zero

        Parser the log file by search the keyword: "Total number of warnings: <>".
        """
        result = "error"
        error_pattern = r'Total number of errors:\s*[1-9]+'
        warning_pattern = r'Total number of warnings:\s*[1-9]+'

        if exitcode == 0:
            result = "pass"

        # parse result from log file when it is available
        # because exit code sometimes is not the real result
        if logfile:
            with open(logfile, "r") as fobj:
                content = fobj.read()

            if re.compile(error_pattern).search(content):
                result = 'error'
            elif re.compile(warning_pattern).search(content):
                result = 'warning'
            else:
                result = 'pass'

        return BuildResult.map(result)





    @staticmethod
    def verify(path):
        '''
        verify the path of compiler is avaliable
        '''
        return Path.exists(path+"/common/bin/IarIdePm.exe")





    def __init__(self, *args, **kwargs):
        super(APP, self).__init__("iar", *args, **kwargs)
        self.builder = Path.join(self._path, "common", "bin", "IarBuild.exe")




    def __str__(self):
        return "IAR-" + self.version



    @property
    def is_ready(self):
        return Path.exists(self.builder)





    def enable_license(self, value):
        """
        Enable iar network license
        """
        if os.system("\"{0}/common/bin/LightLicenseManager.exe\" -s {1} -p ARM.EW"
                     .format(self.path, value)) == 0:
            self.check_license()
            return True
        else:
            return False



    def check_license(self):
        """
        Open LicenseManager.exe, wait for it communicate with license server.
        """
        proc = subprocess.Popen(["{0}/common/bin/LicenseManager.exe".format(self.path)])
        time.sleep(30)
        proc.kill()




    @build
    def build_project(self, project, target, logfile, **kwargs):
        """Return a string about the build command line.

        Arguments:
            project {iar.Project} -- iar project object
            target {string} -- target name
            logfile {string} -- log file path

        Raises:
            IOError -- [description]

        Returns:
            string -- build commandline



        IAR command line guide is quoted from IAR Workbench reference:

            To build the project from the command line, use the IAR Command Line Build Utility
            (iarbuild.exe) located in the common\bin directory. As input you use the project
            file, and the invocation syntax is:

                iarbuild project.ewp [-clean|-build|-make] <configuration>
                [-log errors|warnings|info|all]

            -----------------------------------
            Parameter           Description
             -----------------------------------
            project.ewp     Your IAR Embedded Workbench project file.
            -clean          Removes any intermediate and output files.
            -build          Rebuilds and relinks all files in the current build configuration.
            -make           Brings the current build configuration up to date by compiling,
                            assembling, and linking only the files that have changed since the last
                            build.
            configuration   The name of the configuration you want to build, which can either be
                            one of the predefined configurations Debug or Release, or a name that
                            you define yourself. For more information about build configurations, see
                            Projects and build configurations, page 32.
            -log errors     Displays build error messages.
            -log warnings   Displays build warning and error messages.
            -log info       Displays build warning and error messages, and messages issued by the
                            #pragma message preprocessor directive
            -log all        Displays all messages generated from the build, for example compiler
                            sign-on information and the full command line.
        """

        try:
            if not project.prjpath.endswith(".ewp"):
                projpath = glob.glob(Path.dirname(project.prjpath)+"/*.ewp")[0]
            else:
                projpath = project.prjpath
        except Exception:
            raise IOError("Cannot find *.ewp file, iarbuild cannot build!")

        cpu_count = multiprocessing.cpu_count()
        buildcmd = '"{0}" "{1}" -build "{2}" -log info -parallel {3}'.format(
            self.builder,
            projpath,
            target,
            cpu_count)

        if logfile:
            buildcmd += ' >> "%s" 2>&1'%(logfile)

        return buildcmd




    def install_pack(self, packpath, tmpdir):
        zip_ref = zipfile.ZipFile(packpath, 'r')
        zip_ref.extractall(tmpdir)
        zip_ref.close()
        logging.info("Scucessfully unziped!")

        items = [i for i in os.listdir(tmpdir) if i not in ("binary", "logs")]
        iararm = self.path+"/arm"

        if len(items) == 1:
            foldername = items[0]
            folderpath = tmpdir+"/"+foldername
            print("unzip dir: %s"%folderpath)
            sopurce_path = folderpath
            dest_path = None

            if "arm" in foldername:
                if foldername != "arm":
                    sopurce_path = Path.join(tmpdir, "arm").replace("\\", "/")
                    os.rename(folderpath, sopurce_path)

                dest_path = iararm

            elif "config" in foldername:
                if foldername != "config":
                    sopurce_path = Path.join(tmpdir, "config").replace("\\", "/").replace("//", "/")
                    os.rename(folderpath, sopurce_path)

                dest_path = iararm+"/config"
            else:
                raise NotImplementedError("Unknown structure tree!")

            copydir(sopurce_path, dest_path)
            logging.info("Successfully installed!")
        else:
            raise NotImplementedError("Not supported format")


    def programming(self, board, prjdir, target, file, **kwargs):
        """This will use IAR Cspybat.exe to download debugfile.

        In order to simple the cspybat, this function just replace the iar root,
        and update the usb serial number.

        Arguments:
            prjdir {str} -- project root directory
            target {str} -- target name
            board {mcutk.board.Board} Board object
            debugfile {str} -- path to debug file(image)
            timeout {int}  -- time out

        Raises:
            ValueError -- Raise when not found *.xcl files

        Returns:
            int -- cspybat exit code
        """
        timeout = kwargs.get('timeout', 120)
        return _cspy_programming(self.path, prjdir, board.usbid, target, file, timeout)



    def transform_elf(self, type, in_file, out_file):
        """IAR ELF Tool.
        This method actually will call <iar_root>/arm/bin/ielftool.exe.
        """
        return _elftool(self.path, type, in_file, out_file)




def _elftool(iar_root, type, in_file, out_file):
    """IAR ELF Tool.

    Arguments:
        iar_root {str} -- [description]
        type {str} -- [description]
        in_file {str} -- [description]
        out_file {str} -- [description]

    Raises:
        IOError -- raise when ielftool.exe does not exists.
        ValueError -- raise when type is unsupported.
    """

    elftool = Path.join(iar_root, 'arm/bin/ielftool.exe')
    if not Path.exists(elftool):
        raise IOError('arm/bin/ielftool.exe: does not exists!')

    supported_types = ['bin', 'srec', 'ihex']

    if type not in supported_types:
        raise ValueError('unsupported format type!')

    elftool_command = [
        elftool,
        in_file,
        out_file,
        "--"+type
    ]

    return subprocess.call(elftool_command, shell=True) == 0




def _cspy_programming(iar_root, prjdir, usbid, target, debugfile, timeout):
    """This will use IAR Cspybat.exe to download debugfile.

    In order to simple the cspybat, this function just replace the iar root,
    and update the usb serial number.

    Arguments:
        iar_root {str} -- the root directory of IAR
        prjdir {str} -- project root directory
        usbid {str} -- debug probe serial number
        target {str} -- app target name
        debugfile {str} -- path to debug file(image)

    Raises:
        ValueError -- Raise when not found *.xcl files

    Returns:
        int -- cspybat exit code
    """
    general_xcl = _update_xcl_file(iar_root, prjdir, target, '/*.%s.general.xcl'%target)
    driver_xcl = _update_xcl_file(iar_root, prjdir, target, '/*.%s.driver.xcl'%target)

    # a workround for https://jira.sw.nxp.com/browse/KPSDK-21428
    # TODO: wait for iar fix this issue
    #usbid = usbid[-8:]

    iar_root = iar_root.replace('\\', '/')
    cspybat_command = r'"{0}\\common\\bin\\cspybat.exe" -f "{1}" "--debug_file={2}"'\
    ' --leave_target_running --timeout 500 --backend -f "{3}" "--drv_communication=USB:#{4}"'.format(
        iar_root,
        general_xcl,
        debugfile,
        driver_xcl,
        usbid
    )
    ret = run_command(cspybat_command, stdout=True, timeout=timeout)
    logging.info('iar cspybat.exe exit code: %s', ret[0])

    return ret


def _update_xcl_file(iar_root, prjdir, target, glob_pattern):
    """Replace iar_root and project path in xcl file."""
    str_root_pattern = r"(C:.Program.Files.*IAR Systems\\Embedded Workbench[\w\W]*\\arm\\)|(C:.PROGRA.*IARSYS~1.EMBEDD~.*(\/|\\)arm\/)|(C:.PROGRA.*IAR.*(\/|\\)arm\/)"
    str_usbid_pattern = "--drv_communication=.*\n"
    str_path_pattern = r'[a-zA-Z]\:.*(\\|\/)'
    root_pattern = re.compile(str_root_pattern, re.I)
    usbid_pattern = re.compile(str_usbid_pattern, re.M)
    path_pattern = re.compile(str_path_pattern, re.M)

    settings_dir= Path.join(prjdir, 'settings')
    xclfiles = glob.glob(settings_dir + glob_pattern)
    if not xclfiles:
        raise ValueError("not found *.general.xcl")

    # find the "*.xcl"
    for xcl in xclfiles:
        if target in xcl:
            xclfile = xcl
            break
    else:
        xclfile = xclfiles[0]

    iar_root += r'\\arm/'
    # update xcl content
    with open(xclfile, "r+") as f:
        lines = f.readlines()
        for idx, line in enumerate(lines):
            # inspect the iar_root directory
            if root_pattern.search(line) is not None:
                line = root_pattern.sub(iar_root, line)

            # update project path
            elif path_pattern.search(line) is not None:
                # python3 need to escape the path
                prjdir = prjdir.replace('\\', '/')
                line = path_pattern.sub(prjdir + "/", line)

            # remove the usb id in xcl file
            if usbid_pattern.search(line) is not None:
                line = ''
            # disable verify step
            elif "--drv_verify_download" in line:
                line = ''

            lines[idx] = line

        content = ''.join(lines)
        f.seek(0)
        f.truncate()
        f.write(content)

    return xclfile



def get_all_instance():
    """Get all installed iar instance from local PC.

    Returns:
        list of tuple -- [(path1, version1), ...]
    """
    try:
        import _winreg as winreg
    except ImportError:
        import winreg

    # may more than one iar info on one PC
    index = 0
    version_pool = []
    # windows 32bit
    if platform.architecture()[0] == "32bit":
        root_key = r"SOFTWARE\IAR Systems\Embedded Workbench\5.0\EWARM"
    else:
        root_key = r"SOFTWARE\Wow6432Node\IAR Systems\Embedded Workbench\5.0\EWARM"

    try:
        key_object = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, root_key, 0, winreg.KEY_READ)
    except WindowsError as e:
        logging.debug("not found IAR instance in windows registry!")
        return version_pool


    # walk all installed iar
    while True:
        iar_path = "Unknown"
        iar_version = "Unknown"
        try:
            #enum sub_key name
            sub_key_name = winreg.EnumKey(key_object, index)
            #get sub key path
            sub_key_path = root_key + "\\" + sub_key_name
            #open this path
            sub_key_object = winreg.OpenKey(
                winreg.HKEY_LOCAL_MACHINE,
                sub_key_path,
                0,
                winreg.KEY_READ)

            try:
                #QueryEx return a tuple (value, type)
                iar_path = winreg.QueryValueEx(sub_key_object, "InstallPath")[0].replace('\\', '/')
                iar_version = sub_key_name
            except WindowsError:
                pass

        except WindowsError as e:
            if "Access is denied" in str(e):
                raise e
            break

        if iar_version != "Unknown":
            version_pool.append((iar_path, iar_version))
        index += 1

    return version_pool



def get_latest():
    """Get the latest iar version

    Returns:
        tuple -- (path, version)
    """
    version_pool = get_all_instance()
    if version_pool:
        return _get_max_version(version_pool)
    else:
        return None, None





def _get_max_version(version_pool):
    versions = [(ver[0], LooseVersion(ver[1])) for ver in version_pool]
    versions.sort(key=lambda x:x[1])
    return versions[-1]



