import configargparse
import logging
import pathlib
import re

from contextlib      import contextmanager
from lark            import Lark, Transformer
from lark.exceptions import ParseError, UnexpectedCharacters
from typing          import Optional, Union, Any, Callable, List

_logger = logging.getLogger(__name__)
class Configurable:
    app = None
    _configurable_instances = []

    def __init_subclass__(cls, **kw):
        super().__init_subclass__(**kw)

    @property
    def settings(self):
        return {
            key: val
            for key,val in vars(self).items()
            if val == Setting
        }

    @classmethod
    def _run_create_config(cls, parser):
        for subclass in cls.__subclasses__():
            subclass.create_config(parser)

        for subclass in cls._configurable_instances:
            subclass.createClArgs(parser)

    def __init__(self, *arg, app=None, **kw):
        self.app = self.app or app
        super().__init__(*arg, **kw)
        self._configurable_instances.append(self)

    def createClArgs(self, parser):
        pass

    @classmethod
    def create_config(cls, parser):
        """Create the application configuration"""
        pass

    @classmethod
    def config_parse_args(cls, args, *, unknown_ok=False, help=True, **kw):
        if help:
            kw['add_help'] = True

        kw['formatter_class'] = configargparse.ArgumentDefaultsHelpFormatter

        parser = configargparse.ArgParser(**kw)
        cls._run_create_config(parser)

        if unknown_ok:
            config, unknown = parser.parse_known_args(args=args)
        else:
            config = parser.parse_args(args=args)

        return config

class SettingManagerError(KeyError): pass

class SettingTransformer(Transformer):
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

    ?dict_key: BOOLEAN -> boolean
             | INTEGER -> integer
             | FLOAT   -> float
             | STRING  -> string
             | BYTES   -> bytes
             | tuple

    key:     KEY
    list:    "[" (value ("," value)* (",")?)? "]"
    set:     "{" value ("," value)* (",")? "}"
    tuple:   "(" value ("," value)* (",")? ")"
    dict:    "{" (pair ("," pair)* (",")?)? "}"
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

    app = None

    def __init__(self, app=None, filename=None):
        super().__init__()

        self.app      = self.app or app
        self.filename = filename

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

class MemorySettingManager(dict):
    def flush(self):
        pass

class Setting(Configurable):
    userkey = None
    cmdline = None

    def _getkey(self, instance):
        if self.userkey is not None:
            return self.userkey
        else:
            return f"{instance.__class__.__module__}.{instance.__class__.__name__}.{self.name}"

    def _getSettingManager(self, instance, app=None):
        if app is None:
            app = getattr(instance, 'app', None)
        if app is None or getattr(app, 'settings_manager', None) is None:
            var = f"_{self.__class__.__name__}__memory_settings"
            if not hasattr(instance, var):
                _logger.error(f"Setting '{self.name}' of {instance}: SettingManager not found, using instance storage.")
                setattr(instance, var, MemorySettingManager())
            return getattr(instance, var)
        else:
            return getattr(app, 'settings_manager', None)

    def __set_name__(self, owner, name):
        self.name = name

    def __get__(self, instance, owner):
        if instance is None:
            return self

        key = self._getkey(instance)
        try:
            return self._getSettingManager(instance)[key]
        except KeyError:
            if callable(self.default):
                return self.default()
            else:
                return self.default

    def __set__(self, instance, value):
        key          = self._getkey(instance)
        manager      = self._getSettingManager(instance)
        manager[key] = value
        manager.flush()

    def __delete__(self, instance):
        key     = self._getkey(instance)
        manager = self._getSettingManager(instance)

        if key in manager:
            del manager[key]
            manager.flush()

    def __init__(self,
            key:     Union[str,bool,None] = None,
            short:   Union[str,bool,None] = None,
            argLong: Union[str,bool,None] = None,
            *,
            default: Any                  = None,
            help:    str                  = "",
            choices: Optional[Union[Callable[[],List[str]], List[str]]] = None,
            **kw):

        super().__init__()

        self.default  = default
        self.clArgs   = []
        self.clKwargs = kw
        self.cmdline  = None
        self.help     = help
        self.choices  = choices

        # The user key might be set in a subclass in the __set_name__ method
        # ... do not override that value!
        # ... Except that a boolean True means revert to the auto generated key
        if key is True:
            self.userkey = None
        elif type(key) == str:
            self.userkey = key
        # else: do nothing

        # Configure command line options
        if short is None and argLong is None:
            # No  commmand line
            pass

        elif type(short) == str and argLong is None:
            # Short command line option only
            self.clArgs.append(short)

        elif short is None and type(argLong) == str:
            # Long command line option only, user specified
            self.clArgs.append(argLong)

        elif type(short) == str and argLong is True and type(self.userkey) == str:
            # User supplied short command line option, automatic long option from user key
            self.clArgs.append(short)
            self.clArgs.append(f"--{self.userkey.replace('.','-')}")

        elif short is None and argLong is True and type(self.userkey) == str:
            # No short command line option, automatic long option from user key
            self.clArgs.append(short)
            self.clArgs.append(f"--{self.userkey.replace('.','-')}")

        elif self.userkey is None and argLong is True:
            # Detect an invalid configuration and raise an error
            raise ValueError("Cannot set an automatic command line option unless the setting key is explicitly specified!")

        elif type(short) not in (str,None) and type(argLong) not in (str,None):
            raise ValueError(f"Invalid configuration: {self.__class__.__name__}({key}, {short}, {arglong}, ...)")

    def createClArgs(self, parser):
        # Save the default value to command line arguments as it is used in both places
        # ... set it here so that runtime calculations are accurate!
        if callable(self.default):
            self.clKwargs['default'] = self.default()
        else:
            self.clKwargs['default'] = self.default

        if callable(self.choices):
            self.clKwargs['choices'] = self.choices()
        else:
            self.clKwargs['choices'] = self.choices

        self.clKwargs['help'] = self.help

        if len(self.clArgs) > 0:
            self.cmdline = parser.add(*self.clArgs, **self.clKwargs)

    @contextmanager
    def tempval(self, instance, value):
        """
        Set a temporary value for this setting using a context manager.

        Example:

        >>> from mnectar.config import Setting
        >>> class Foo:
        ...     myval = Setting(default=True)
        ...     def bar(self):
        ...         assert self.myval == True
        ...         with Foo.myval.tempval(self, False):
        ...             # Some Action
        ...             assert self.myval == False
        ...         assert self.myval == True
        """
        try:
            orig = self.__get__(instance, type(instance))
            self.__set__(instance, value)
            yield
        finally:
            if orig == self.default:
                self.__delete__(instance)
            else:
                self.__set__(instance, orig)
