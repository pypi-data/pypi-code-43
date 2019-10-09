"""
Project interface definition.
"""
import abc
import os
import glob

from mcutk.exceptions import ProjectNotFound, InvalidTarget



class ProjectBase(object):
    """
    abstract class representing a project basic function
    """
    __metaclass__ = abc.ABCMeta

    # project extension
    PROJECT_EXTENSION = None

    @classmethod
    def frompath(cls, path):
        """Return a project instance from a given file path or directory.

        If path is a directory, it will search the project file and return an instance.
        Else this will raise mcutk.apps.exceptions.ProjectNotFound.
        """
        if not cls.PROJECT_EXTENSION:
            raise ValueError("Error, %s.PROJECT_EXTENSION is not defined! Please report an bug!"%cls)

        if os.path.isfile(path) and path.endswith(cls.PROJECT_EXTENSION):
            return cls(path)

        try:
            project_file = glob.glob(path + "/*" + cls.PROJECT_EXTENSION)[0]
        except IndexError:
            raise ProjectNotFound("Not found project %s in specific folder"%cls.PROJECT_EXTENSION)

        return cls(project_file)



    def __init__(self, path, *args, **kwargs):
        self.prjpath = path
        self.prjdir = os.path.dirname(path)
        self._conf = None
        self._targets = list()


    @property
    def targets(self):
        """Get targets"""
        return list(self._targets)


    @property
    def targetsinfo(self):
        """Returns a dict about the targets data.

        Example:
        {
            "Debug":   "debug_output_dir/output_name",
            "Release": "release_output_dir/output_name",
        }
        """
        return self._conf


    @abc.abstractproperty
    def name(self):
        """Get project name"""
        pass


    def map_target(self, input_target):
        input_target = input_target.strip()
        # map for mdk
        for tname in self.targets:
            if input_target == tname or input_target in tname.split() :
                return tname

        # map for general
        for tname in self.targets:
            if input_target.lower() in tname.lower():
                return tname

        for tname in self.targets:
            print("!@ avaliable target: %s"%tname)

        msg = "Cannot map the input target: {}, project: {}, valid targets: {}".format(input_target, self.prjpath, str(self.targets))
        raise InvalidTarget(msg)



    @property
    def idename(self):
        return str(self.__module__).split('.')[-2]


    def to_dict(self):
        return {
            'toolchain': self.idename,
            'targets': self.targets,
            'project': self.prjpath,
            'name': self.name
        }


