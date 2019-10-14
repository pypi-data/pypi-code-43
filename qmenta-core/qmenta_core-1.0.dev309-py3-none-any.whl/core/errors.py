"""
Define the root error class for all QMENTA exceptions. All exceptions raised
by the QMENTA Core library are subclasses of ``qmenta.core.errors.Error`` and
thus are expected exceptions. If other exceptions are raised, this indicates
unexpected behavior of the library.
"""


class Error(Exception):
    """
    Base class for all QMENTA errors.
    """
    def __init__(self, *args: str) -> None:
        Exception.__init__(self, *args)


class CannotReadFileError(Error):
    """
    When a file cannot be read.

    Parameters
    ----------
    filename : str
        The filename of the file that could not be read
    """
    def __init__(self, message: str) -> None:
        Error.__init__(self, message)


class CannotWriteFileError(Error):
    """
    When a file cannot be written to.

    Parameters
    ----------
    filename : str
        The filename of the file that could not be written
    """
    def __init__(self, filename: str) -> None:
        Error.__init__(self, 'Cannot write file: {}'.format(filename))


class InvalidBuildSpecError(Error):
    """
    When the ``build.yaml`` file is not according to the requirements.
    """
    pass
