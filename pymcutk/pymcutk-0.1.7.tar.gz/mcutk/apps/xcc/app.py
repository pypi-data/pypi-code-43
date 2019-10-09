import os
import re
import glob
import logging
import platform
import subprocess

from mcutk.apps.decorators import build
from mcutk.apps.idebase import IDEBase, BuildResult
from mcutk.apps.cmake import generate_build_cmdline


class APP(IDEBase):
    """Xtensa XCC compiler."""

    OSLIST = ["Windows","Linux","Darwin"]

    # C:\usr\xtensa\XtDevTools\install\tools\RI-2019.1-win32\XtensaTools
    def __init__(self, path, *args, **kwargs):
        super(APP, self).__init__("xcc", path, *args, **kwargs)


    @property
    def is_ready(self):
        return os.path.exists(self.path)


    @build
    def build_project(self, project, target, logfile, **kwargs):
        """Return a command line string.

        Arguments:
            project {xcc.Project} -- xcc project object
            target {string} -- target name
            logfile {string} -- log file path

        Returns:
            string -- commandline string.
        """
        os.environ["XCC_DIR"] = self.path
        return generate_build_cmdline(project, target, logfile)

    def transform_elf(self, type, in_file, out_file):
        pass


    @staticmethod
    def get_latest():
        """Search and return a latest instance from system."""
        # RI-2019.1-win32\XtensaTools\bin
        default_root_win = "C:/usr/xtensa/XtDevTools/install/tools"
        path_pattern = default_root_win + "/*/XtensaTools"
        path_list = glob.glob(path_pattern)
        if not path_list:
            return
        path = path_list[0]
        version = path.replace(default_root_win, '').replace("/XtensaTools", '').replace('/', '')
        return APP(path, version=version)

    @staticmethod
    def parse_build_result(exitcode, logfile):
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


