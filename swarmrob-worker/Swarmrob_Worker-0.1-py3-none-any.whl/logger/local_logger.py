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

import logging

LOCAL_LOGGER_FILE = "/tmp/swarmrob.log"


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


class LocalLogger(object, metaclass=SingletonType):
    """
    Singleton class for the local logger
    """

    def __init__(self):
        """
            Initialization of the LocalLogger object
        """
        self.local_logger = logging.getLogger(__name__)
        self.local_logger.setLevel(logging.DEBUG)
        formatter = logging.Formatter('%(asctime)s %(name)-12s %(levelname)-8s %(message)s')

        file_handler = logging.FileHandler(LOCAL_LOGGER_FILE)
        file_handler.setFormatter(formatter)
        file_handler.setLevel(logging.DEBUG)
        self.local_logger.addHandler(file_handler)

        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        console_handler.setLevel(logging.DEBUG)
        self.local_logger.addHandler(console_handler)
        self.log_calls = True
        self.enable = False

    def log_method_call(self, class_name, method_name):
        if self.log_calls and self.enable:
            self.debug("Call: %s %s", class_name, method_name)
        return self.log_calls and self.enable

    def log_call(self, function_name):
        if self.log_calls and self.enable:
            self.debug("Call: %s", function_name)
        return self.log_calls and self.enable

    def debug(self, msg, *args):
        """
            Overwritten debug method of the logging module
        :param msg: Message that should be logged
        :param args: List of additional arguments
        :return:
        """
        if self.enable is True:
            self.local_logger.debug(msg, *args)
        return self.enable

    def error(self, msg, *args):
        """
            Overwritten error method of the logging module
        :param msg: Message that should be logged
        :param args: List of additional arguments
        :return:
        """
        if self.enable is True:
            self.local_logger.error(msg, *args)
        return self.enable

    def exception(self, exception, msg=""):
        """
            Overwritten exception method of the logging module
        :param exception: Thrown exception
        :param msg: Message that should be logged
        :return:
        """
        if self.enable is True:
            error_message = msg + "\n" + str(exception)
            self.local_logger.error(error_message)
        return self.enable
