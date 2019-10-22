# system modules
import logging
import os
from os.path import abspath, exists, expanduser, join

# internal modules
import xdgspec
from xdgspec.version import __version__
from xdgspec.utils import *

# external modules

logger = logging.getLogger(__name__)

XDG_HOME_DEFAULTS = {
    "XDG_DATA_HOME": expanduser(join("~", ".local", "share")),
    "XDG_CONFIG_HOME": expanduser(join("~", ".config")),
    "XDG_CACHE_HOME": expanduser(join("~", ".cache")),
}
XDG_DIRS_DEFAULTS = {
    "XDG_DATA_DIRS": ":".join(
        (
            expanduser(join(join(os.sep, "usr"), "local", "share")),
            expanduser(join(join(os.sep, "usr"), "share")),
        )
    ),
    "XDG_CONFIG_DIRS": expanduser(join(join(os.sep, "etc"), "xdg")),
}
XDG_DEFAULTS = XDG_HOME_DEFAULTS.copy()
XDG_DEFAULTS.update(XDG_DIRS_DEFAULTS)


class XDGDirectoryVariable:
    """
    Class to access an XDG Base Directory variable

    Args:
        name (str): the name of the XDG Base Directory variable
        defaults (sequence, optional): variable value defaults
    """

    def __init__(self, name, defaults=XDG_DEFAULTS):
        self.defaults = defaults
        self.name = name

    @property
    def name(self):  # pragma: no cover
        """
        The name of the variable. Has to be a valid environment variable name.

        :type: :any:`str`
        """
        try:
            self._name
        except AttributeError:
            self._name = ""
        return self._name

    @name.setter
    def name(self, new):
        new = str(new)
        if new not in self.defaults:
            raise ValueError(
                "Invalid name '{}'. Use one of {}.".format(
                    new, ", ".join(map("'{}'".format, self.defaults.keys()))
                )
            )
        self._name = new

    @property
    def value(self):
        """
        The value of the variable. If the environment variable is unset,
        returns the default.
        """
        return os.environ.get(
            self.name, XDG_DEFAULTS.get(self.name)
        ) or XDG_DEFAULTS.get(self.name)

    def __str__(self):
        """
        Stringification of this object returns its :attr:`value`.
        """
        return str(self.value)


class Directory:
    """
    Class representing a directory. Objects of this class can be used as a
    context manager, making sure that the directory exists.

    Args:
        path (str): the path to the directory
    """

    def __init__(self, path):
        self.path = path

    @property
    def path(self):
        """
        This directory's path
        """
        return self._path

    @path.setter
    def path(self, new):
        self._path = new

    def __enter__(self):
        """
        Entering this object as a context manager makes sure that its
        :attr:`path` exists.
        """
        if not exists(self.path):
            logger.info("Create nonexistent directory '{}'".format(self.path))
            os.makedirs(self.path)
        return self.path

    def __exit__(self, *args, **kwargs):
        pass

    def __str__(self):
        """
        Stringification of this object returns its :attr:`path`.
        """
        return str(self.path)


class XDGDirectory(XDGDirectoryVariable, Directory):
    """
    Class representing a user-specific directory from the XDG Base Directory
    Specification.

    Args:
        name (str): the name of the XDG Base Directory variable
    """

    def __init__(self, name):
        XDGDirectoryVariable.__init__(
            self, name=name, defaults=XDG_HOME_DEFAULTS
        )

    @property
    def path(self):
        """
        This directory's path corresponds to its :attr:`value`.
        """
        return expanduser(self.value)

    def __str__(self):
        """
        Stringification of this object returns its :attr:`path`.
        """
        return str(self.path)


class XDGPackageDirectory(XDGDirectory):
    """
    Class to represent the directory of an application package in the sense of
    the XDG Base Directory Specifiation.

    Args:
        name (str): the name of the XDG Base Directory variable
        packagename (str): the name of the application package
    """

    def __init__(self, name, packagename):
        XDGDirectory.__init__(self, name)
        self.packagename = packagename

    @property
    def packagename(self):
        """
        The application package name
        """
        return self._packagename

    @packagename.setter
    def packagename(self, new):
        self._packagename = new

    @property
    def path(self):
        """
        Returns the stringification of this object
        (:any:`XDGPackageDirectory.__str__`)
        """
        return str(self)

    def __str__(self):
        """
        Stringification of this object returns expands its :attr:`value` and
        appends a subdirectory named like :attr:`packagename`.
        """
        return join(expanduser(self.value), self.packagename)


class XDGDirectories(XDGDirectoryVariable):
    """
    Class represending XDG Base Directory listing variables

    Args:
        name (str): the name of the XDG Base Directory variable
    """

    def __init__(self, name):
        XDGDirectoryVariable.__init__(
            self, name=name, defaults=XDG_DIRS_DEFAULTS
        )

    @property
    def paths(self):
        """
        Sequence of paths, i.e. the :attr:`value` split at colons

        :type: :any:`list`
        """
        return self.value.split(":")

    @property
    def existing_paths(self):
        """
        Generator yielding unique and only existing paths in the :attr:`value`
        """
        return filter(
            exists,
            unique(filter(lambda p: abspath(expanduser(p)), self.paths)),
        )

    def __iter__(self):
        return self.existing_paths
