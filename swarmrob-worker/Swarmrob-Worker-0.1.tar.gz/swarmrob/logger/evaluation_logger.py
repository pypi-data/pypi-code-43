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

import csv
import os
import sys
import time
from enum import Enum
from os import path

from . import local_logger
from ..utils import config

FILE_ENDING = ".csv"

COSTS_HEADER = ["Service", "Worker", "CPU/Worker", "VRAM/Worker", "SWAP/Worker", "Bandwidth/Worker",
                "CPU/COSTS", "VRAM/COSTS", "SWAP/COSTS", "DOWNLOAD/COSTS", "OVERALL/COSTS"]
ALLOCATIONS_HEADER = ["Service", "Worker"]
ALLOC_METRICS_HEADER = ["Name of Metric", "Service", "Worker", "Value", "Number of Workers", "Number of Services"]


class LogType(Enum):
    """
    Enum class for the different evaluation log types
    """
    COSTS = "costs"
    ALLOCATIONS = "allocations"
    ALLOC_METRICS = "alloc_metrics"


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


class EvaluationLogger(metaclass=SingletonType):
    """
    The evaluation logger is responsible for logging the evaluation split up into the three log types Costs, Allocations
    and Alloc_metrics.
    """

    def __init__(self):
        """
        Initializing the Evaluation Logger.
        """
        llogger = local_logger.LocalLogger()
        llogger.log_method_call(self.__class__.__name__, sys._getframe().f_code.co_name)
        conf = config.Config()
        self.timestr = time.strftime("%Y_%m_%d_%H_%M_%S")
        self.log_folder = conf.get(config.Section.LOGGING, config.Option.LOGGING_FOLDER)
        self.log_ident = conf.get(config.Section.LOGGING, config.Option.LOGGING_IDENT)
        if self.log_folder is not None and self.log_ident is not None:
            self.enabled = conf.get_boolean(config.Section.LOGGING, config.Option.LOGGING_ENABLED)
        else:
            self.enabled = False
        if self.enabled:
            llogger.debug("The evaluation logger is enabled")
        else:
            llogger.debug("The evaluation logger is disabled")

    def set_log_folder(self, new_log_folder):
        """
            Sets a new log folder. If the new log folder is None then logging will be disabled.
        :param new_log_folder: new log folder
        :return: the new log folder
        """
        llogger = local_logger.LocalLogger()
        llogger.log_method_call(self.__class__.__name__, sys._getframe().f_code.co_name)
        self.log_folder = new_log_folder
        if self.log_folder is None:
            self.enabled = False
        elif '~' in self.log_folder:
            self.log_folder = self.log_folder.replace('~', path.expanduser('~'))
        llogger.debug("Evaluation log folder set to %s", self.log_folder)
        return self.log_folder

    def set_log_ident(self, new_log_ident):
        """
            Sets a new log identifier. If the new log identifier is None then logging will be disabled.
        :param new_log_ident: new log identifier
        :return: the new log identifier
        """
        llogger = local_logger.LocalLogger()
        llogger.log_method_call(self.__class__.__name__, sys._getframe().f_code.co_name)
        self.log_ident = new_log_ident
        llogger.debug("Evaluation log identifier set to %s", self.log_ident)
        return self.log_ident

    def reset_time(self):
        """
            Resets or creates a new time string used in the file name. Resetting the time will always create a new file
            if there is enough time between two resets (1 second).
        :return:
        """
        llogger = local_logger.LocalLogger()
        llogger.log_method_call(self.__class__.__name__, sys._getframe().f_code.co_name)
        self.timestr = time.strftime("%Y_%m_%d_%H_%M_%S")

    def enable(self, enable=True):
        """
            Enables or disables the evaluation logger. If the log_ident or the log_folder is None the evaluation logger
            can't be enabled.
        :param enable: defines whether the evaluation logger should be enabled or disabled
        :return: new status of the evaluation logger
        """
        llogger = local_logger.LocalLogger()
        llogger.log_method_call(self.__class__.__name__, sys._getframe().f_code.co_name)
        if enable is False:
            self.enabled = False
            llogger.debug("The evaluation logger is disabled")
        elif self.log_folder is not None:
            self.enabled = True
            llogger.debug("The evaluation logger is enabled")
        return self.enabled

    def write(self, data, log_type):
        """
            Logs data for the specified log_type.
        :param data: list of values that should be logged
        :param log_type: to which log_type the data corresponds to
        :return: boolean, True if data has been logged otherwise False
        """
        llogger = local_logger.LocalLogger()
        llogger.log_method_call(self.__class__.__name__, sys._getframe().f_code.co_name)
        if self.enabled:
            self.create_file(log_type)
            with open(self.get_filepath(log_type), 'ab') as csv_file:
                writer = csv.writer(csv_file, delimiter=';', quotechar='|', quoting=csv.QUOTE_MINIMAL)
                writer.writerow(data)
            return True
        return False

    def create_file(self, log_type):
        """
            Creates the sessions log_file for the specified log_type if it doesn't already exist.
        :param log_type: which file should be created
        :return: boolean, True if the file has been created otherwise False
        """
        llogger = local_logger.LocalLogger()
        llogger.log_method_call(self.__class__.__name__, sys._getframe().f_code.co_name)
        self.create_log_folder(log_type)
        filepath = self.get_filepath(log_type)
        if not os.path.isfile(filepath):
            with open(filepath, 'wb') as csv_file:
                writer = csv.writer(csv_file, delimiter=';', quotechar='|', quoting=csv.QUOTE_MINIMAL)
                writer.writerow(self.get_log_type_header(log_type))
            return True
        return False

    def create_log_folder(self, log_type):
        """
            Creates the log_folder for the specified log_type if it doesn't already exist.
        :param log_type: which folder should be created
        :return: boolean, True if the folder has been created otherwise False
        """
        llogger = local_logger.LocalLogger()
        llogger.log_method_call(self.__class__.__name__, sys._getframe().f_code.co_name)
        if not os.path.exists(self.log_folder + str(log_type.value)):
            os.makedirs(self.log_folder + str(log_type.value))
            return True
        return False

    def get_filepath(self, log_type):
        """
            Creates the filepath for the specified log_type.
        :param log_type: which filepath should be created
        :return: string describing the filepath
        """
        llogger = local_logger.LocalLogger()
        llogger.log_method_call(self.__class__.__name__, sys._getframe().f_code.co_name)
        ident = ""
        if self.log_ident is not None or self.log_ident != "":
            ident = '_' + self.log_ident
        return self.log_folder + str(log_type.value) + '/' + str(log_type.value) + ident + '_'\
            + self.timestr + FILE_ENDING

    def get_log_type_header(self, log_type):
        """
            Returns a list of headers for the specified log_type.
        :param log_type: which headers should be returned
        :return: list of header strings
        """
        llogger = local_logger.LocalLogger()
        llogger.log_method_call(self.__class__.__name__, sys._getframe().f_code.co_name)
        if log_type == LogType.COSTS:
            return COSTS_HEADER
        elif log_type == LogType.ALLOCATIONS:
            return ALLOCATIONS_HEADER
        elif log_type == LogType.ALLOC_METRICS:
            return ALLOC_METRICS_HEADER
        return None
