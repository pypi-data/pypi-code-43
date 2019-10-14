# -*- coding: utf-8 -*-
import os
import configparser
from os.path import dirname, abspath
"""Top-level package for Publishing Boy."""

__author__ = """Red"""
__email__ = 'przemyslaw.kot@gmail.com'
__version__ = '0.1.0'

ROOT_PATH = dirname(dirname(abspath(__file__)))

config_file = os.path.join(ROOT_PATH, 'config/settings.cfg')

config = configparser.ConfigParser()
config.read(config_file)
