import os
import re
import glob
import platform

from mcutk.apps.projectbase import ProjectBase
from mcutk.exceptions import ProjectNotFound

def generate_build_cmdline(project, target, logfile):
    """Generate and return an executable commands."""

    osname = platform.system()
    if "Windows" == osname:
        suffix = 'bat'
    else:
        suffix = 'sh'

    current_path = os.path.dirname(os.path.abspath(__file__))
    script_file = os.path.join(current_path, "cmake_build.{}".format(suffix)).replace('\\', '/')

    buildcmd = "{script} \"{prj_root}\" {target} \"{toolchain_file}\"".format(
        script=script_file,
        prj_root=project.prjdir,
        target=target,
        toolchain_file=project.toolchain_file,
    )

    if logfile:
        buildcmd = "{} >> {} 2>&1".format(buildcmd, logfile)

    return buildcmd


class Project(ProjectBase):
    """ Wraps a project defined in CMakeLists.txt."""

    PROJECT_EXTENSION = 'CMakeLists.txt'

    @classmethod
    def frompath(cls, path):
        """Return a project instance from a given file path or directory.

        If path is a directory, it will search the project file and return an instance.
        Else this will raise mcutk.apps.exceptions.ProjectNotFound.
        """

        if os.path.isfile(path) and path.endswith(cls.PROJECT_EXTENSION):
            return cls(path)

        if glob.glob(path + "/CMakeLists.txt") and glob.glob(path + "/build_all.*"):
            return cls(path + "/CMakeLists.txt")

        raise ProjectNotFound("Not found CMake project in path: %s"%path)

    def __init__(self, path, *args, **kwargs):
        super(Project, self).__init__(path, **kwargs)
        self._name = None
        self._conf = self._parse_project()
        self._targets = self._conf.keys()
        self._toolchain_file = self.get_toolchain_file()

    def _parse_project(self):
        """Parse configurations from CMakeLists.txt.

        Returns:
            dict -- targets configuration
        """
        targets = dict()

        with open(self.prjpath, 'r') as fh:
            content = fh.read()

        # extract output name
        output_keywords = [
            r'add_library\(.+(\.)?\w+',
            r'add_executable\(.+(\.)?\w+',
            r'set_target_properties\(\w+(\.)?\w+',
            r'TARGET_LINK_LIBRARIES'
        ]

        excutable = None
        for kw in output_keywords:
            s = re.compile(kw).search(content)
            if s != None:
                excutable = s.group(0).split('(')[1].strip()
                break
        else:
            raise ValueError("Unable to detect output definition in CMakeLists.txt. [%s]"%self.prjpath)
        self._appname = excutable.split('.')[0]

        # extract build types
        for m in re.findall("CMAKE_C_FLAGS_\w+ ", content):
            tname = m.replace('CMAKE_C_FLAGS_', '').lower().strip()
            if tname not in targets:
                targets[tname] = "{}/{}".format(tname, excutable)

        return targets

    def get_toolchain_file(self):
        try:
            script_file = glob.glob(os.path.dirname(self.prjpath) + "/build_all.*")[0]
        except Exception:
            raise IOError("Unable to indentify CMAKE_TOOLCHAIN_FILE! Because script(build_all.sh/.bat) is not found!")

        with open(script_file, "r") as fh:
            filecontent = fh.readlines()

        toolchain_file = ''
        for line in filecontent:
            if "-DCMAKE_TOOLCHAIN_FILE=" in line:
                toolchain_file = line.split("-DCMAKE_TOOLCHAIN_FILE=")[1].split(" ")[0]
                break

        return toolchain_file.replace('"', '')

    @property
    def name(self):
        """Return the application name"""
        return self._appname

    @property
    def toolchain_file(self):
        """Return a relative path for cmake_toolchain_file."""
        return self._toolchain_file

    @property
    def idename(self):
        """Return the toolchain name that the cmake defined."""
        filename = os.path.basename(self.toolchain_file)
        return filename.replace(".cmake", '')

