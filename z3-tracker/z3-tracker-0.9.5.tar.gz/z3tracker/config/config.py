'''
Interface to configuration system
'''

import json
import os
import sys
import typing

from ..version import __version__ as version

from .default import DEFAULT, OVERWRITE


__all__ = 'Config', 'config_directory'


class ConfigOption(dict):
    '''
    Single entry info for configuration file.

    Instance variables:
        name: name of the config option
        default: default value
    '''

    def __init__(
            self, name: str,
            valtype: typing.Callable[[typing.Any], typing.Any],
            default: typing.Any):
        '''
        Args:
            name: name of the config option
            valtype: type of the config option
            default: default value
        '''

        super().__init__()
        self.name = name
        self.valtype = valtype
        self.default = default


class Config(dict):
    '''
    Program configuration.

    Instance variables:
        self: program configuration {'option': value}
        filename: full path to config filename
    '''

    def __init__(self):
        super().__init__()

        self.filename = _config_filename()

        try:
            fid = open(self.filename, 'r')
        except FileNotFoundError:
            imported = None
        else:
            imported = fid.read()
            fid.close()

        try:
            imp_dict = {} if imported is None else json.loads(imported)
        except json.decoder.JSONDecodeError:
            imp_dict = {}

        for entry in imp_dict:
            self._insert_entry(entry, imp_dict[entry])
        self._check_missing()

        self['version'] = version

    def _write_config(self) -> None:
        '''
        Write current configuration to file.
        '''

        self['version'] = version
        with open(self.filename, 'w') as fid:
            json.dump(self, fid)

    def _insert_entry(self, entry_name: str, entry_value: typing.Any) -> None:
        '''
        Insert imported entry.

        Args:
            entry: config file entry read from file
        '''

        if entry_name in DEFAULT:
            self[entry_name] = DEFAULT[entry_name][1](entry_value)

    def _check_missing(self) -> None:
        '''
        Insert missing entries into configuration.
        '''

        changed = False
        if 'version' not in self or self['version'] != version:
            for entry in OVERWRITE[version]:
                self[entry] = DEFAULT[entry][1](DEFAULT[entry][0])
                changed = True
        for entry in DEFAULT:
            if entry not in self:
                self[entry] = DEFAULT[entry][1](DEFAULT[entry][0])
                changed = True
        if changed:
            self._write_config()

    def update(self, entry: str, data: object) -> None:
        '''
        Update config entry with new data.

        Args:
            entry: config entry
            data: new data
        '''

        self[entry] = data
        self._write_config()


def config_directory() -> str:
    '''
    Return configuration directory.

    This will create said directory if it doesn't exist.

    Returns:
        str: full path to configuration directory
    '''

    if sys.platform.startswith('win32'):
        configdir = os.path.join(os.getenv('LOCALAPPDATA'), 'z3-tracker')
    else:
        configdir = os.path.expanduser('~/.z3-tracker')
    if not os.path.isdir(configdir):
        os.mkdir(configdir)
    return configdir


def _config_filename() -> str:
    '''
    Return config file name.

    This will create the config directory if it doesn't exist. The config file
    itself, however, won't.

    Returns:
        str: fill path to config file
    '''

    return os.path.join(config_directory(), 'config.json')
