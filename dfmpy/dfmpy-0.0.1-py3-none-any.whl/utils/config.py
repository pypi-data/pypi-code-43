# TODO docs

from configparser import ConfigParser
from configparser import DEFAULTSECT
from configparser import NoSectionError
from functools import lru_cache
from logging import getLogger
from os.path import expanduser
from os.path import expandvars
from pathlib import Path
from platform import system
from socket import gethostname

from xdgenvpy import XDGPackage

# TODO add defaults in here so that the config files are not required.

# TODO docs
LOG = getLogger()

# TODO docs
__XDG_ENV = XDGPackage('dfmpy')

# TODO docs
__CONFIG_DEFAULTS = {
    'hostname': gethostname(),
    'system': system(),
}


class DfmpyConfig(object):
    # TODO docs

    def __init__(self, config):
        # TODO docs
        # TODO unit test
        self._config = config
        LOG.debug('Config: %s', dict(self._config))

    def __getattr__(self, attribute):
        # TODO docs
        # TODO unit test
        # TODO check CLI args for an override before checking the file
        value = self._config.get(attribute, None)

        # Normalize the value.
        if value:
            value = expanduser(expandvars(value.strip()))
        return value


def __remove_comments(s):
    # TODO docs
    # TODO unit test
    try:
        return s[:s.index('#')]
    except ValueError:
        return s


@lru_cache(maxsize=1)
def get_config():
    # TODO docs
    # TODO unit test
    # TODO supply a default set of args that was written to a default config file.
    config = ConfigParser(defaults=__CONFIG_DEFAULTS.copy())

    config_file = Path(__XDG_ENV.XDG_CONFIG_HOME).joinpath('config.ini')
    if config_file.exists():
        LOG.debug('Reading config file: %s', config_file)
        config.read(config_file)

    valid_sections = ('dfmpy',)
    section = DEFAULTSECT
    for vs in valid_sections:
        if config.has_section(vs):
            section = vs
    if not section:
        raise NoSectionError(f'Config {config_file}'
                             f' must include a valid section: {valid_sections}')
    LOG.debug('Using section %s from %s', section, config_file)
    try:
        return DfmpyConfig(config[section])
    except NoSectionError as e:
        e.message = f'{e.message} in {config_file}'
        raise e


def get_globs(filepath):
    # TODO docs
    # TODO unit test
    globs = []
    if Path(filepath).exists():
        with open(filepath, 'r') as f:
            globs = f.readlines()
        globs = [__remove_comments(line) for line in globs]
        globs = [line.strip() for line in globs]
        globs = [line for line in globs if line]
    return tuple(globs)


@lru_cache(maxsize=1)
def get_ignore_globs():
    # TODO docs
    # TODO unit test
    ignore_file = Path(__XDG_ENV.XDG_CONFIG_HOME).joinpath('ignore.globs')
    globs = get_globs(ignore_file)
    return tuple(globs)
