import os
from typing import get_type_hints, Type, List

from enum import Enum


class LogFormat(Enum):
    json = 'json'
    plain = 'plain'

    @property
    def raw(self) -> str:
        return str(self.value)


class LogLevel(Enum):
    critical = 'CRITICAL'
    error = 'ERROR'
    warning = 'WARNING'
    info = 'INFO'
    debug = 'DEBUG'
    notset = 'NOTSET'

    @property
    def raw(self) -> str:
        return str(self.value)


class BaseConfig(object):
    _parsers = {}

    def __init__(self):
        super().__init__()

        self._default = {}
        self._default = {property: self.get(property) for property in self.__dir__() if self._should_wrap(property)}
        self._types = {property: get_type_hints(type(self)).get(property) for property, value in self._default.items()}

    def get(self, name: str):
        return self.__getattribute__(name)

    def update(self, config):
        """
        Update the values from the BaseConfig object.
        :param obj: an object holding the configuration
        """

        if not isinstance(config, BaseConfig):
            raise ImportError

        self._default.update(config._default)
        self._types.update(config._types)

    def __getattribute__(self, name):
        if not name.isupper() or name.startswith('_'):
            return super(BaseConfig, self).__getattribute__(name)

        if name in self._default.keys():
            default = self._default[name]

            try:
                value = os.environ[name]
            except KeyError:
                return default
            else:
                return self.__parse(name, value)

        return super(BaseConfig, self).__getattribute__(name)

    def __setattr__(self, key, value):
        if hasattr(self, '_default') and key in self._default.keys():
            self._default[key] = value
        else:
            super.__setattr__(self, key, value)

    def _should_wrap(self, name: str) -> bool:
        return name.isupper() and not name.startswith('_')

    def __parse(self, name, value):
        type_property = self._types.get(name)

        if type_property is None or type_property not in self._parsers:
            return value

        try:
            return self._parsers[type_property](value)
        except:
            raise AttributeError(
                f'Could not parse "{value}" of type {type(value)} as '
                f'{type_property} using parser {self._parsers[type_property]}')

    @staticmethod
    def parser(type: Type):
        def decorator(parser):
            BaseConfig._parsers[type] = parser
            return parser

        return decorator


@BaseConfig.parser(bool)
def parse_bool(value: str) -> bool:
    return value.lower() in ('true', 'y', 'yes', '1', 'on')


@BaseConfig.parser(int)
def parse_int(value: str) -> int:
    return int(value)


@BaseConfig.parser(float)
def parse_float(value: str) -> float:
    return float(value)

@BaseConfig.parser(List[str])
def parse_list(value: str) -> List[str]:
    return value.split(',')

@BaseConfig.parser(LogLevel)
def parse_log_level(value: str) -> LogLevel:
    return LogLevel(value)


@BaseConfig.parser(LogFormat)
def parse_log_format(value: str) -> LogFormat:
    return LogFormat(value)


class SimpleConfig(BaseConfig):

    LOGO: str = """
 _____       _
|  __ \     (_)               
| |  | |_ __ ___   _____ _ __ 
| |  | | '__| \ \ / / _ \ '__|
| |__| | |  | |\ V /  __/ |   
|_____/|_|  |_| \_/ \___|_|
"""

    LOG_FORMAT: LogFormat = LogFormat.json
    LOG_LEVEL: LogLevel = LogLevel.info


class DriverConfig(SimpleConfig):
    pass
