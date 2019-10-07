"""
Setup configuration
"""

from __future__ import annotations

import io
import logging
import os
from configparser import ConfigParser
from configparser import ExtendedInterpolation
from typing import List

logger = logging.getLogger(__name__)


class EnvironmentInterpolation(ExtendedInterpolation):

    def before_get(self, parser, section, option, value, defaults):
        # environment varialbes
        value = os.path.expandvars(value)
        # config file variables
        value = super().before_get(parser, section, option, value, defaults)
        return value


class RichConfigParser(ConfigParser):

    def __init__(self):
        super().__init__(self, interpolation=EnvironmentInterpolation())

    def __str__(self):
        text = io.StringIO()
        for section in self.sections():
            text.write(f"[{section}]\n")
            for (key, value) in self.items(section):
                text.write(f"{key}={value}\n")
        return text.getvalue()

    def get_list(self, section, option) -> List[str]:
        value = self.get(section, option)
        return produce_list(value)


def produce_list(text:str) -> List[str]:
        result = text.splitlines()
        result = map(str.strip, result)
        result = filter(None, result)
        return list(result)


def ensure_environment() -> None:
    "provide environment variables expected by 'config.ini'"
    if not os.environ.get('HOME'):
        os.environ['HOME'] = '/root'
    if not os.environ.get('PWD'):
        os.environ['PWD'] = os.getcwd()


def setup_logging(config_parser:ConfigParser) -> None:
    "provide logging configuration"

    section = config_parser['logging']

    trace_level_name = section.get('trace_level_name')
    trace_level_code = section.getint('trace_level_code')

    def method_trace(self, message, *args, **kwargs) -> None:
        if self.isEnabledFor(trace_level_code):
            self._log(trace_level_code, message, args, **kwargs)

    logging.addLevelName(trace_level_code, trace_level_name)
    logging.Logger.trace = method_trace  # custom logging function

    logging.basicConfig(
        level=section['level'].strip().upper(),
        datefmt=section['datefmt'].strip(),
        format=section['format'].strip(),
    )


def produce_config() -> RichConfigParser:
    "provide global configuration"
    ensure_environment()
    config_parser = RichConfigParser()
    config_dir = os.path.dirname(os.path.abspath(__file__))
    config_path = os.path.join(config_dir, "config.ini")
    #
    config_parser.read(config_path)
    setup_logging(config_parser)
    config_path_list = config_parser.get_list('config', 'path_list')
    logger.info(f"config path_list: {config_path_list}")
    #
    config_parser.read(config_path_list)
    setup_logging(config_parser)
    return config_parser


CONFIG = produce_config()

__all__ = [
    'CONFIG',
]
