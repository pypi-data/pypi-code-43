#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright 2018,2019 Aljoscha Pörtner
# Copyright 2019 André Kirsch
# This file is part of SwarmRob.
#
# SwarmRob is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# SwarmRob is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with SwarmRob.  If not, see <https://www.gnu.org/licenses/>.

import sys
import configparser
import os
from enum import Enum

import swarmrob
from ..logger import local_logger

CONFIG_FILE = os.path.dirname(swarmrob.__file__) + "/swarmrob.conf"


class Section(Enum):
    """
    Enum that contains all sections listed in the swarmrob config file
    """
    INTERNET = "Internet"
    LOGGING = "Logging"


class Option(Enum):
    """
    Enum that contains all options listed int the swarmrob config file
    """
    INTERFACE = "interface"
    LOGGING_ENABLED = "enabled"
    LOGGING_FOLDER = "logging_folder"
    LOGGING_IDENT = "logging_identifier"


class SingletonType(type):
    """
    Helper class for singleton
    """
    def __call__(cls, *args, **kwargs):
        try:
            return cls.__instance
        except AttributeError:
            cls.__instance = super(SingletonType, cls).__call__(*args, **kwargs)
            return cls.__instance


class Config(object, metaclass=SingletonType):
    """
    The config object is responsible for reading the settings from the config file located at '/etc/swarmrob.conf'
    """

    def __init__(self):
        """
        Initializes the config
        """
        llogger = local_logger.LocalLogger()
        llogger.log_method_call(self.__class__.__name__, sys._getframe().f_code.co_name)
        self._file = None
        self._config = None
        self._load_config()

    def _load_config(self, file=CONFIG_FILE):
        """
            load_config loads the configuration located at '/etc/swarmrob.conf'
        :return:
        """
        llogger = local_logger.LocalLogger()
        llogger.log_method_call(self.__class__.__name__, sys._getframe().f_code.co_name)
        self._file = file
        self._config = configparser.ConfigParser()
        self._config.read(self._file)

    def get(self, section, option):
        """
            Returns the value under section and option in the config file
        :param section: Section Enum
        :param option: Option Enum
        :return: string value of setting or none
        """
        llogger = local_logger.LocalLogger()
        llogger.log_method_call(self.__class__.__name__, sys._getframe().f_code.co_name)
        try:
            section, option = self._get_values(section, option)
            value = self._config.get(section, option)
            if not value == '':
                return str(value)
            return None
        except configparser.Error:
            return None

    def get_boolean(self, section, option):
        """
            Returns the value under section and option in the config file as a boolean
        :param section: Section Enum
        :param option: Option Enum
        :return: boolean value of setting or none
        """
        llogger = local_logger.LocalLogger()
        llogger.log_method_call(self.__class__.__name__, sys._getframe().f_code.co_name)
        try:
            section, option = self._get_values(section, option)
            return self._config.getboolean(section, option)
        except (configparser.Error, ValueError):
            return None

    def _get_values(self, section, option):
        """
            Converts section and option into their string values
        :param section
        :param option
        :return:
        """
        llogger = local_logger.LocalLogger()
        llogger.log_method_call(self.__class__.__name__, sys._getframe().f_code.co_name)
        if type(section) is Section:
            section = str(section.value)
        if type(option) is Option:
            option = str(option.value)
        if type(section) is not str or type(option) is not str:
            return None, None
        return section, option
