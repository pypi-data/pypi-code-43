import os
import re
import glob

from mcutk.apps import cmake
from mcutk.exceptions import ProjectNotFound

class Project(cmake.Project):
    """xcc project object

    This class could parser the settings in CMakeLists.txt & build_all.sh.
    Parameters:
        prjpath: path of CMakeLists.txt

    """
    pass

