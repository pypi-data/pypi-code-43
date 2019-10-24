'''
Program configuration infrastructure
'''

from . import config
from . import globals

__all__ = 'CONFIG', 'CONFIGDIRECTORY'

globals.CONFIG = config.Config()
CONFIG = globals.CONFIG

CONFIGDIRECTORY = config.config_directory()
