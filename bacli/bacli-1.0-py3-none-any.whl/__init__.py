""" Define what is imported with `from bacli import *`. """

from .cli import cli
from .cli_legacy import command, setDescription

__all__ = ["cli", "command", "setDescription"]
