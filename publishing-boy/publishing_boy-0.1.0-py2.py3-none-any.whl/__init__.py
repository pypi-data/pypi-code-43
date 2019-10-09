# -*- coding: utf-8 -*-
import os
import configparser
"""Top-level package for Publishing Boy."""

__author__ = """Red"""
__email__ = 'przemyslaw.kot@gmail.com'
__version__ = '0.1.0'

PATH = os.path.dirname(os.path.abspath(__file__))

config_file = os.path.join(PATH, 'settings.cfg')

config = configparser.ConfigParser()
config.read(config_file)
