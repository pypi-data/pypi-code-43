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
import argparse
import os.path
from enum import Enum


class Argument(Enum):
    """
    Enum class for all possible command line arguments
    """
    VERBOSE = 0, '-v', "--verbose", "verbose", "store_true", None, False, 'Enable verbose logging mode'
    REPOSITORY = 1, '-r', "--repository", "repository", "store", str, True, ''
    ADVERTISE_ADDRESS = 2, '-a', '--advertise_address', "advertise_address", "store", str, False, \
                           'Advertise address used to access the daemon'
    INTERFACE = 3, '-i', '--interface', "interface", "store", str, False,\
                   'Interface to use for and connect to the daemon'
    UUID_OPTIONAL = 4, '-u', '--uuid', "uuid", "store", str, False, 'UUID of the object'
    UUID = 5, '-u', '--uuid', "uuid", "store", str, True, 'UUID of the object'
    COMPOSE_FILE = 6, '-c', '--compose_file', "compose_file", "store", str, True, 'Path to the edf file'
    LOG_IDENTIFIER = 7, '-l', '--log_identifier', "log_identifier", "store", str, False, 'Identifier for a log file'
    LOG_FOLDER = 8, '-f', '--log_folder', "log_folder", "store", str, False, 'Path to save evaluation logs in'
    WORKER_UUID = 9, '-w', '--worker_uuid', "worker_uuid", "store", str, True, 'UUID of the worker'
    WORKER_UUID_OPTIONAL = 10, '-w', '--worker_uuid', "worker_uuid", "store", str, False, 'UUID of the worker'
    SWARM_UUID = 11, '-s', '--swarm_uuid', "swarm_uuid", "store", str, True, 'UUID of the swarm'
    DAEMONIZE = 12, '-n', '--no-daemon', "daemonize", "store_false", None, False, 'Run swarmrob daemon in background'

    def __new__(cls, identifier, short_name, long_name, destination, action, data_type, required, help_msg):
        """
            Creates a new argument
        :param short_name: single character name of the argument
        :param long_name: complete name of the argument
        :param destination: variable name to save the value in
        :param action: action type, e.g. store, store_true
        :param data_type: Type of the saved data
        :param required
        :param help_msg
        :return:
        """
        arg = object.__new__(cls)
        arg.short_name = short_name
        arg.long_name = long_name
        arg.destination = destination
        arg.action = action
        arg.data_type = data_type
        arg.required = required
        arg.help_msg = help_msg
        arg._value_ = identifier
        return arg


class CMDParser:

    def __init__(self, program_path=None, description=None, arguments=None, include_help=True):
        """
            Initializes the command line parser
        :param program_path: sub path of the program
        :param description: description of the command
        :param arguments: list of arguments to include
        :param include_help: True, when the help argument should be included
        """
        self._arg_parser = argparse.ArgumentParser(prog=CMDParser._get_program_path(program_path),
                                                   description=description, add_help=include_help)
        if arguments is None:
            arguments = []
        if Argument.VERBOSE not in arguments:
            arguments.append(Argument.VERBOSE)
        self._add_arguments(arguments)

    def _add_arguments(self, arguments):
        """
            Adds all given arguments to the command line parser
        :param arguments: list of arguments
        :return:
        """
        if arguments is not None:
            for arg in arguments:
                if arg.data_type is None:
                    self._arg_parser.add_argument(arg.short_name, arg.long_name, action=arg.action,
                                                  dest=arg.destination, required=arg.required, help=arg.help_msg)
                else:
                    self._arg_parser.add_argument(arg.short_name, arg.long_name, action=arg.action,
                                                  dest=arg.destination, type=arg.data_type, required=arg.required,
                                                  help=arg.help_msg)

    @staticmethod
    def _get_program_path(program_sub_path):
        """
            Generates the full program path
        :param program_sub_path: sub path of the program
        :return: String
        """
        _, filename = os.path.split(sys.argv[0])
        if program_sub_path is None:
            program_sub_path = filename
        else:
            program_sub_path = filename + ' ' + program_sub_path
        return program_sub_path

    def parse_arguments(self):
        """
            Parses the command line parameters and returns their values
        :return: command line parameters
        """
        params = self._arg_parser.parse_known_args(sys.argv)
        return params[0]
