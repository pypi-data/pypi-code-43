import os
import glob

from xml.etree import cElementTree as ET
from mcutk.apps.projectbase import ProjectBase
from mcutk.exceptions import ProjectNotFound
from mcutk.apps import eclipse

class Project(eclipse.Project):
    """ARM DS5 project object

    This class could parser the settings in .cproject and .project.
    Parameters:
        prjpath: path of .project
    """

    PROJECT_EXTENSION = '.cproject'

    def __init__(self, prjpath, *args, **kwargs):
        super(Project, self).__init__(prjpath, **kwargs)
        self.parse(self.prjpath)





