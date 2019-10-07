# Python modules
from __future__ import division
import exceptions

# 3rd party modules

# Our modules



class MultifileAttributeMismatchError(exceptions.Exception):
    """Raised when a class in this module opens multiple files and the
    attributes (dims and sweep width) don't match.
    """
    pass


class MultifileTypeMismatchError(exceptions.Exception):
    """Raised when a class in this module opens multiple files and the
    the object types in the returned list are not all of the same type.
    """
    pass


class UnsupportedDimensionalityError(exceptions.Exception):
    """Raised when a class in this module opens a file in which all
    dimensions are > 1.
    """
    pass


class IncorrectDimensionalityError(exceptions.Exception):
    """Raised when a class in this module opens a file in which at least one
    dimensions that should be 1 is not 1.
    """
    pass


class SIDataError(UnsupportedDimensionalityError):
    """Raised when a class in this module opens a file containing SI data.
    This is a special case of UnsupportedDimensionalityError. We expect
    to support SI data eventually, and then this will go away.
    """
    pass


class OpenFileAttributeMismatchError(exceptions.Exception):
    """Raised when a class in this module opens one or more files and the
    attributes (dims and sweep width) of the new files don't match the
    attributes of the currently open files.
    """
    pass


class OpenFileTypeMismatchError(exceptions.Exception):
    """Raised when a class in this module opens one or more files and the
    object types in which the new files are stored don't match the object
    types of the currently open files.
    """
    pass


class FileNotFoundError(exceptions.Exception):
    """
    Raised when a reader module can't find a matching data file for a params
    file or vice versa.
    """
    pass


class OpenFileUserReadRawError(exceptions.Exception):
    """Raised when a user derived class want to indicate that there is a
    problem within their read_raw method.
    """
    pass

class IncompleteHeaderParametersError(exceptions.Exception):
    """Raised when a user derived class want to indicate that there is a
    problem within their read_raw method.
    """
    pass



