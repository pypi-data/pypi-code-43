import click
import click._compat


class CloutException(Exception):
    pass


class ValidationError(CloutException):
    pass


class MissingInput(CloutException):
    def __init__(self, group, string, found):
        self.group = group
        self.string = string
        self.found = found

    def __str__(self):
        return f"Parsing fails at {self.found}"
