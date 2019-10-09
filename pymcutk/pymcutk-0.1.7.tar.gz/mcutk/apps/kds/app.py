import os
import re
import platform
import glob

from distutils.version import LooseVersion
from mcutk.apps.decorators import build
from mcutk.apps.idebase import IDEBase, BuildResult

class APP(IDEBase):
    """
    kinetis-design-studio Workbench interface implementation.
    This class inherit from IDEBase, and it has the ability to build project,
    and parse the build result.

    Create an instance:
        (1) search in windows registry:
            >>> kds = APP.get_latest()
            >>> print kds.version

        (2) from api
            >>> kds = APP("C:/Freescale/KDS_3.0.0", version="3.0.0")
            >>> print kds.version

    """

    OSLIST = ["Windows", "Linux", "Mac"]

    EXITCODE = {
        0:	"PASS",
        1:	"Errors"
    }

    def __init__(self, path, *args, **kwargs):
        super(APP, self).__init__("kds", path, *args, **kwargs)
        self.builder = os.path.join(self._path, "eclipse", "kinetis-design-studio")


    @build
    def build_project(self, project, target, logfile, *kwargs):
        """Return a string about the build command line.

        Arguments:
            project {kds.Project} -- kds project object
            target {string} -- target name
            logfile {string} -- log file path
            workspace {string} -- kds build workspace
        Returns:
            string -- build commandline

        KDS command line guide is quoted from KDS Workbench reference:

            To build the project from the command line, use the KDS Command Line Build Utility
            (kinetis-design-studio) located in the eclipse directory. As input you use the project
            file, and the invocation syntax is:

                kinetis-design-studio --launcher.suppressErrors -nosplash
                -application {org.eclipse.cdt.managedbuilder.core.headlessbuild|other applications}
                [-cleanBuild|-build] {project_name_reg_ex/config_name_reg_ex | all}
                [-import|-importAll] {[uri:/]/path/to/project}}
                -data {workspace path}

            ------------------------------------------------
            Parameter                   Description
            ------------------------------------------------
            -application applicationId  The application to run. Applications are declared by plug-ins supplying extensions to the org.eclipse.core.runtime.applications extension point. This argument is
                                        typically not needed. If specified, the value overrides the value supplied by the configuration. If not specified, the Eclipse Workbench is run.
            --launcher.suppressErrors   If specified the executable will not display any error or message dialogs. This is useful if the executable is being used in an unattended situation
            -nosplash                   Controls whether or not the splash screen is shown.
            -data workspacePath         The path of the workspace on which to run the Eclipse platform. The workspace location is also the default location for projects. Relative paths are interpreted.
                                        relative to the directory that Eclipse was started from.
            -nosplash                   Runs the platform without putting up the splash screen.
            -import                     {[uri:/]/path/to/project} -- Import projects under URI.
            -importAll                  {[uri:/]/path/to/projectTreeURI} -- Import all projects under URI.
            -build                      {project_name_reg_ex{/config_reg_ex} | all} -- Build projects.
            -cleanBuild                 {project_name_reg_ex{/config_reg_ex} | all} -- Clean and  build projects.
            -I                          {include_path} -- additional include_path to add to tools
            -include                    {include_file} -- additional include_file to pass to tools
            -D                          {prepoc_define} -- addition preprocessor defines to pass to the tools
            -E                          {var=value} -- replace/add value to environment variable when running all tools
            -Ea                         {var=value} -- append value to environment variable when running all tools
            -Ep                         {var=value} -- prepend value to environment variable when running all tools
            -Er                         {var} -- remove/unset the given environment variable
            -T                          {toolid} {optionid=value} -- replace a tool option value in each configuration built
            -Ta                         {toolid} {optionid=value} -- append to a tool option value in each configuration built
            -Tp                         {toolid} {optionid=value} -- prepend to a tool option value in each configuration built
            -Tr                         {toolid} {optionid=value} -- remove a tool option value in each configuration built

        """

        if "Windows" == platform.system():
            env_set = 'set path={0}/bin;{0}/toolchain/bin;{1};'.format(self._path, os.getenv("Path"))
        else:
            env_set = 'export PATH={0}/bin:{0}/toolchain/bin:{1}'.format(self._path, os.getenv("PATH"))

        data = {
            "env": env_set,
            "builder": self.builder,
            "prjname": project.name,
            "target": target,
            "prjdir": project.prjdir,
            "workspace": kwargs.get('workspace'),
            "logfile": logfile,
        }

        buildcmd = '{env} && "{builder}" --launcher.suppressErrors -nosplash -application "org.eclipse.cdt.managedbuilder.core.headlessbuild" '\
        ' -cleanBuild "{prjname}/{target}" -import "{prjdir}" -data "{workspace}" >> {logfile} 2>&1'.format(**data)

        return buildcmd


    @staticmethod
    def get_latest():
        """Search and return a latest KDS instance in system

        Returns:
            <KDS.APP object>
        """
        path, version = get_latest()
        if path:
            return APP(path, version=version)
        else:
            return None


    @staticmethod
    def parse_build_result(exitcode, logfile):
        """Parse KDS build result

        Arguments:
            exitcode {int} -- the exit code of kinetis-design-studio process
            logfile {string} -- a file contains the output from kinetis-design-studio.

        Returns:
            <BuildResult object> -- the build result
        Notes:
        ---------------------
        kinetis-design-studio exit code
            noerror warnnings: 0
            erros: none-zero

        Parser the log file by search the keyword: "Total number of warnings: <>".
        """
        content = []
        result = BuildResult.Pass
        if 0 == exitcode:
            with open(logfile, "r") as f:
                content = f.read()
                if re.search(r"warning:", content):
                    result = BuildResult.Warnings
        else:
            result = BuildResult.Errors
        return result

    @staticmethod
    def verify(path):
        '''
        verify the path of compiler is avaliable
        '''
        return os.path.exists(path+"/eclipse/kinetis-design-studio")

    @property
    def is_ready(self):
        return os.path.exists(self.builder)

    @staticmethod
    def default_install_path(osname):
        default_path_table = {
            "Windows": "C:/Freescale",
            "Linux": "/opt/Freescale",
            "Darwin": "/Applications"
        }
        return default_path_table[osname]


def get_latest():
    """Get the latest kds version

    Returns:
        tuple -- (path, version)
    """
    osname = platform.system()
    kds_tool_list = []
    try:
        default_root_path = APP.default_install_path(osname)
        for per_folder in glob.glob(default_root_path + '/KDS**'):
            if "Darwin" == osname:
                kds_tool_list.append(os.path.join(default_root_path, per_folder, "Contents"))
            else:
                kds_tool_list.append(os.path.join(default_root_path, per_folder))
    except Exception:
        return None,None



    kds_versions = {}
    for per_kds in kds_tool_list:
        readmefile = per_kds + "/README.TXT"
        if not os.path.exists(readmefile):
            continue
        with open(readmefile, "r") as f:
            lines = f.readlines()
        for line in lines:
            match = re.search(r"\d\.\d\.\d", line)
            if match:
                kds_versions[match.group()] = per_kds
                break

    if kds_versions:
        latest_v = sorted(kds_versions.keys(), key=lambda v:LooseVersion(v))[-1]
        return kds_versions[latest_v], latest_v

    return None, None

