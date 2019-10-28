import click
import click._compat


class CloutException(Exception):
    """Base exception for Clout exceptions."""


class ValidationError(CloutException):
    """Raised for invalid command-line arguments."""


class MissingInput(CloutException):
    """Raised for missing command-line arguments."""

    def __init__(self, group, string, found):
        self.group = group
        self.string = string
        self.found = found

    def __str__(self):
        return f"Parsing fails at {self.found}"
