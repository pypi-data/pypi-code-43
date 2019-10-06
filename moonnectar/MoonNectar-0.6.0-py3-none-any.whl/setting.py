from __future__ import annotations

import logging

_logger = logging.getLogger(__name__)

import weakref

from copy import copy
from dataclasses import dataclass, field
from enum import Enum, Flag, auto
from typing import Optional, Union, Callable, Sequence

import Registry

class Location(Flag):
    # fmt: off
    Memory      = 0
    CommandLine = auto()
    StateFile   = auto()
    Any         = CommandLine | StateFile
    # fmt: on

class SettingTransformer(Transformer):
    # fmt: off
    file    = dict
    key     = lambda self,_: str(_[0])
    line    = tuple
    list    = list
    dict    = dict
    set     = set
    tuple   = tuple
    boolean = lambda self,_: True if _[0] == "True" else False
    integer = lambda self,_: int(_[0])
    float   = lambda self,_: float(_[0])
    bytes   = lambda self,_: eval(_[0])
    string  = lambda self,_: eval(_[0])
    pair    = lambda self,_: (_[0],_[1])
    # fmt: on

class SettingManager(dict):
    _grammar = """
    file: line*
    line: key "=" value "\\n"

    ?value: BOOLEAN -> boolean
          | INTEGER -> integer
          | FLOAT   -> float
          | STRING  -> string
          | BYTES   -> bytes
          | tuple
          | list
          | set
          | dict

    dict_key: BOOLEAN -> boolean
            | INTEGER -> integer
            | FLOAT   -> float
            | STRING  -> string
            | BYTES   -> bytes
            | tuple

    key:     KEY
    list:    "[" value ("," value)* (",")? "]"
    set:     "{" value ("," value)* (",")? "}"
    tuple:   "(" value ("," value)* (",")? ")"
    dict:    "{" pair ("," pair)* (",")? "}"
    pair:    dict_key ":" value

    STRING:  /(?P<quote>['"]).*?(?<!\\\)(?P=quote)/
    BYTES:   /b(?P<quote>['"]).*?(?<!\\\)(?P=quote)/

    KEY     : /[A-Za-z0-9._]+\\b/
    BOOLEAN : "True" | "False"
    INTEGER : /-?[0-9]+/
    FLOAT   : /-?[0-9]+\.[0-9]+/

    %import common.NEWLINE
    %import common.WS
    %ignore WS
    """

    self.app = None

    def __init__(self, app=None, filename = None):
        self.app      = self.app or app
        self.filename = filename

        super().__init__()

        if self.filename is not None:
            self.open(self.filename)

    def flush(self):
        if self.filename is not None:
            with self.filename.open(mode='w', encoding='utf-8') as file:
                file.writelines((f"{key} = {value!r}\n" for key,value in self.items()))

    def open(self, filename):
        self.filename = pathlib.Path(filename).expanduser()

        _logger.debug(f"Loading Settings File: {self.filename}")

        if self.filename.exists():
            with self.filename.open(mode='r', encoding='utf-8') as fd:
                content = fd.read()

            try:
                parser = Lark(self._grammar, start="file")
                parsed = parser.parse(content)
                trans  = SettingTransformer()
                result = trans.transform(parsed)

                self.clear()
                self.update(result)

            except ParseError as ex:
                _logger.error(f"Invalid Setting File [ParseError]: {ex}")
                return []

            except UnexpectedCharacters as ex:
                _logger.error(f"Invalid Setting File [UnexpectedCharacters]: {ex}")
                return []

@dataclass
class Setting:
    """
    Automatic Setting Registration providing persistant application state, command
    line arguments, and automatic GUI preferences.

    :param key: Persistent application state key
    :param arg: Command-Line Argument (short, long, or tuple(short,long))
    :param type: Setting Type Hint.  One of: "int", "bool", "float", "str", "choice", or
                 "pathlist"
    :param choices: A list of valid choices for this setting, or callable generating
                    valid choices (sets type='choice')
    :param default: Default value or callable object generating a default value
    :param help: Help string describing this setting
    :param instance: Internal Use Only! Used to bind this setting to an instance
    :param name
    """

    # fmt: off
    key:       Optional[str,bool]                                = None
    arg:       Optional[Union[str, Tuple[str,str]]]              = None
    type:      Optional[str]                                     = None
    choices:   Optional[Union[Callable[[], Sequence], Sequence]] = None
    default:   Optional[Union[Callable[[], Any], Any]]           = None
    help:      str                                               = ""
    location:  Optional[Location]                                = field(default=None, init=False, compare=False)
    name:      Optional[str]                                     = field(default=None, init=False, compare=False)
    varname:   Optional[str]                                     = field(default=None, init=False, compare=False)
    # fmt: on

    def __post_init__(self):
        self.location = Location.Memory

        if self.arg:
            self.location |= Location.CommandLine

        if self.key is not False:
            self.location ~= Location.Memory
            self.location |= Location.StateFile

    def __set_name__(self, owner, name):
        self.name    = name
        self.varname = f"_{self.__class__.__name__}__{self.name}_value"

    def __get__(self, instance, owner):
        key = self.get_key(instance, owner)

        if Location.Memory in self.location ("and instance/owner has value"):
            # Get from instance or owner
            ...
        elif Location.CommandLine in self.location ("and command line has value"):
            # Get from command line _ONLY_ if value is set (!= default)
            ...
        elif Location.StateFile in self.location ("and state file has value"):
            # Get from app state file
            ...
        elif callable(self.default):
            # Use the default factory
            return self.default()
        else:
            # Use the default value
            return self.default

    def __set__(self, instance, value):
        key = self.get_key(instance, instance.__class__)

        if Location.StateFile in self.location:
            # Set in state file
            ...
        else:
            # Set in instance or owner
            setattr(instance, self.varname, value)

    def __delete__(self, instance):
        key = self.get_key(instance, instance.__class__)

        if Location.Memory in self.location:
            delattr(instance, self.varname)
        elif Location.StateFile in self.location:
            ...

    def get_key(self, instance, owner):
        ikey = getattr(instance, f"_{self.name}_key", None)

        # If the instance defined a key value, use that
        if ikey:
            return ikey

        # If initialed with a string key, use that
        elif type(self.key) == str:
            return self.key

        # If an auto-key was requested and this is a plugin/registry, use the path
        elif self.key and issubclass(owner, Registry) or issubclass(owner, Registry.Plugin):
            return f"{owner.path}.{self.name}"

        # If an auto-key was requested, fallback is the full module path of the variable
        elif self.key:
            return f"{instance.__class__.__module__}.{instance.__class__.__name__}.{self.name}"

        # Otherwise, no auto key requested
        else:
            return None

    def get_app(self, instance):
        # Import the AppInit class here to avoid circular imports
        from .appinit import AppInit

        if instance is None:
            return None
        else:
            appvars = inspect.getmembers(instance, lambda _: isinstance(_, AppInit))
            # Multiple app instances in the same class should never happen.
            # ... if it does, simply return the first found and ignore the rest.
            if appvars:
                return appvars[0]
            else:
                return None

