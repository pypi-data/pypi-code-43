"""
Module providing helpers to deal with the debconf database, which is used to configure Debian packages.
"""

import quixote.build.shell as shell
from typing import Union, List


class _DebconfTypeMeta(type):
    def __new__(mcs, name, underlying_type_hint, formatter):
        def init(self, value: underlying_type_hint):
            """
            :param value:           the value to use for the answer
            """
            self.value = value

        wrapper = type(name, (object,), {})
        wrapper.__doc__ = f"Class representing a debconf answer of type '{name}'"
        wrapper.__init__ = init
        wrapper.__str__ = formatter
        return wrapper


Select = _DebconfTypeMeta("Select", str, lambda self: f"select {self.value}")
MultiSelect = _DebconfTypeMeta("MultiSelect", List[str], lambda self: f"multiselect {', '.join(self.value)}")
String = _DebconfTypeMeta("String", str, lambda self: f"string {self.value}")
Boolean = _DebconfTypeMeta("Boolean", bool, lambda self: f"boolean {str(self.value).lower()}")
Note = _DebconfTypeMeta("Note", str, lambda self: f"note {self.value}")
Text = _DebconfTypeMeta("Text", str, lambda self: f"text {self.value}")
Password = _DebconfTypeMeta("Password", str, lambda self: f"password {self.value}")


def set_selections(
        package: str,
        question: str,
        value: Union[Select, MultiSelect, String, Boolean, Note, Text, Password]
):
    """
    Insert an answer for a given question of a given package into the debconf database (see debconf-set-selections(1))

    :param package:         the package owning the question
    :param question:        the name of the question
    :param value:           the value to use as answer for this question
    """
    return shell.command(f"echo '{package}' '{question}' '{value}' | debconf-set-selections")


def reset(package: str, question: str):
    """
    Reset answers for a given question of a given package in the debconf database

    :param package:         the package owning the question
    :param question:        the name of the question
    """
    return shell.command(f"echo RESET {question} | debconf-communicate {package}")


def unregister(package: str, question: str):
    """
    Unregister a given question of a given package in the debconf database

    :param package:         the package owning the question
    :param question:        the name of the question
    """
    return shell.command(f"echo UNREGISTER {question} | debconf-communicate {package}")


def purge(package: str):
    """
    Purge all the answers for questions of a given package in the debconf database

    :param package:         the package whose questions to purge
    """
    return shell.command(f"echo PURGE | debconf-communicate {package}")
