import os
import re
import platform
import glob
from distutils.version import LooseVersion

from mcutk.apps.decorators import build
from mcutk.apps.idebase import IDEBase, BuildResult
from mcutk.apps.eclipse import generate_build_cmdline

class APP(IDEBase):
    """ARM Development Studio(DS5/DS).

    Create an instance:
        (1) search in windows registry:
            >>> ds5 = APP.get_latest()
            >>> print ds5.version

        (2) from api:
            >>> ds5 = APP("C:\Program Files\DS-5 v5.22.0", version="5.22.0")
            >>> print ds5.version
    """

    OSLIST = ["Windows", "Linux"]

    EXITCODE = {
        0: "PASS",
        1: "Errors"
    }


    def __init__(self, path, *args, **kwargs):
        super(APP, self).__init__("ds5", path, *args, **kwargs)
        self.builder = os.path.join(self._path, "bin", "eclipse")



    @build
    def build_project(self, project, target, logfile, **kwargs):
        """Return a string about the build command line.

        Arguments:
            project {ds5.Project} -- ds5 project object
            target {string} -- target name
            logfile {string} -- log file path
            workspace {string} -- ds5 build workspace

        Returns:
            string -- build commandline

        """
        workspace = kwargs.get('workspace')
        cmdline = generate_build_cmdline(self.builder, workspace, project.prjdir, project.name, target)
        if logfile:
            cmdline.append('>> "{}" 2>&1'.format(logfile))
        return " ".join(cmdline)



    @staticmethod
    def get_latest():
        """Search and return a latest ds5 instance in system

        Returns:
            <ds5.APP object>
        """
        path, version = get_latest()
        if path:
            return APP(path, version=version)
        else:
            return None




    @staticmethod
    def parse_build_result(exitcode, logfile):
        """Parse ds5 build result

        Arguments:
            exitcode {int} -- the exit code of ds5 process
            logfile {string} -- a file contains the output from ds5.

        Returns:
            <BuildResult object> -- the build result

        Notes:
        ds5 exit code
            noerror warnnings: 0
            erros: none-zero

        Parser the log file by search the keyword: "Total number of warnings: <>".
        """
        content = []
        result = BuildResult.Pass
        if 0 == exitcode:
            with open(logfile, "r") as f:
                content = f.read()
                if re.search(r"Warning:", content):
                    result = BuildResult.Warnings
        else:
            result = BuildResult.Errors
        return result



    @staticmethod
    def verify(path):
        """Verify the path is valid ARM DS installation."""
        return os.path.exists(path+"/bin/eclipse")



    @property
    def is_ready(self):
        return os.path.exists(self.builder)



    @staticmethod
    def default_install_path(osname):
        default_path_table = {
            "Windows": r"C:\Program Files",
            "Linux": r"/usr/local"
        }
        return default_path_table[osname]


def get_latest():
    """Get the latest ARM DS instance

    Returns:
        tuple -- (path, version)
    """
    osname = platform.system()
    ds5_tool_list = []
    try:
        default_root_path = APP.default_install_path(osname)
        for per_folder in glob.glob(default_root_path + '/DS-5**'):
            ds5_tool_list.append(os.path.join(default_root_path, per_folder))

    except Exception:
        return None,None


    ds5_versions = {}
    for per_ds5 in ds5_tool_list:
        revfile = os.path.join(per_ds5, "/sw/info/rev.txt")
        if os.path.exists(revfile):
            with open(revfile, "r") as f:
                content = f.read()
            match = re.search(r"\d+", content)
            if match:
                ds5_versions[match.group()] = per_ds5

    try:
        latest_v = sorted(ds5_versions.keys(), key=lambda v:LooseVersion(v))[-1]
        return ds5_versions[latest_v], latest_v
    except IndexError:
        pass

    return None, None


