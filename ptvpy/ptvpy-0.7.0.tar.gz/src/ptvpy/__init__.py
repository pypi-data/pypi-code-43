"""Command line program and Python library for particle tracking velocimetry."""


from ._version import get_versions

#: Detailed version information about this release.
_version_info = get_versions()
__version__ = _version_info["version"]
del get_versions


class PtvPyError(Exception):
    """Base for errors specific to PtvPy.

    Parameters
    ----------
    message : str
        A message describing the cause of the error.
    hint : str, optional
        A helpful hint on what to do about the error.
    """

    def __init__(self, message: str, hint: str = None):
        self.message = message
        self.hint = hint
        super().__init__(message, hint)

    def __str__(self):
        return self.message
