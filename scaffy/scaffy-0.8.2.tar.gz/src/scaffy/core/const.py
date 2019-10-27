# -*- coding: utf-8 -*-
"""
This is just so that all the configuration is in one place.

Changing the configuration will still require releasing new version.
"""

from __future__ import absolute_import, unicode_literals

# stdlib imports
from os.path import expanduser


DEFAULT_LOCAL_STORE_PATH = expanduser('~/.config/scaffy/local')

# Scaffold settings
FILE_EXT = '.scaffold'
CONFIG_FILE = 'scaffy-scaffold-config.json'
TIME_FORMAT = '%Y-%m-%d %H:%M:%S'
