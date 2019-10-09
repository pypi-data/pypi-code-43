import os
import glob
import logging
import tempfile
from distutils.version import LooseVersion
from xml.etree import cElementTree as ET
from difflib import SequenceMatcher
from mcutk.exceptions import ProjectNotFound, ProjectParserError
from mcutk.apps.projectbase import ProjectBase
from mcutk.apps import eclipse


class Project(eclipse.Project):
    """LPCxpresso project parser."""


    @classmethod
    def frompath(cls, path):
        """Return a project instance from a given file path or directory.

        If path is a directory, it will search the project file and return an instance.
        Else this will raise mcutk.apps.exceptions.ProjectNotFound.
        """
        if os.path.isfile(path) and (path.endswith('.project') or path.endswith('.cproject')):
            return cls(path)

        instance = None
        for file in glob.glob(path + "/.project"):
            filepath = os.path.abspath(file)
            if "lpcx" in filepath:
                drivers = filepath.replace("\\", "/").split("/")
                if "lpcx" in drivers:
                    instance = cls(file)
                    break
        return instance



    def __init__(self, prjpath, **kwargs):
        """LPCX project constructor.

        Arguments:
            prjpath {str} -- path to .cproject/.project

        """
        super(Project, self).__init__(prjpath, **kwargs)
        self.parse(self.prjpath)









