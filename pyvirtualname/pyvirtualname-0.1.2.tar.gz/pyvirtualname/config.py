import os
from configparser import RawConfigParser, NoSectionError, NoOptionError

CONFIG_PATH = [
    '/etc/pyvirtualname.conf',
    os.path.expanduser('~/.pyvirtualname.conf'),
    os.path.realpath('./pyvirtualname.conf'),
]


class ConfigurationManager(object):
    """
    Application wide configuration manager
    """
    def __init__(self):
        self.config = RawConfigParser()
        self.config.read(CONFIG_PATH)

    def get(self, section, name):
        try:
            return os.environ['PVN_'+name.upper()]
        except KeyError:
            pass

        try:
            return self.config.get(section, name)
        except (NoSectionError, NoOptionError):
            pass

        return None

    def read(self, config_file):
        self.config.read(config_file)


config = ConfigurationManager()
