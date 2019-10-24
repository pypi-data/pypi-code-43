class Error(Exception):
    """Base class for exceptions in this module."""
    pass

class ConfigError(Error):
    """
    Exception raised when error occurs while extracting an accession.
    Attributes:
        message -- explanation of the error
    """

    def __init__(self, message):
        self.message = message
