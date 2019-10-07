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
import os
import traceback

from clint.arguments import Args
from clint.textui import puts, colored, indent

from .logger import local_logger
from .utils.cmd_parser import Argument, CMDParser
from .utils.errors import NetworkException
from .utils import network
from . import worker
from . import daemon


def main():
    """
        Main function of the Swarmrob CLI
    :return:
    """
    if os.geteuid():
        sys.exit(colored.red("Swarmrob needs to be started with root privileges"))
    llogger = local_logger.LocalLogger()
    llogger.log_call(sys._getframe().f_code.co_name)
    params = CMDParser(include_help=False).parse_arguments()
    llogger.enable = params.verbose
    args = Args()

    with indent(4, quote=''):
        puts(colored.green("Swarmbot - Container Orchestration for Robotic Applications"))

    try:
        switch_command(str(args.get(0)))
    except KeyError:
        with indent(4, quote='>>'):
            puts(colored.red(str(args.get(0)) + " is not a valid command"))
            puts(colored.red("Type 'swarmrob help' for a command list"))
    except Exception as e:
        puts(colored.red("An unknown error occurred"))
        llogger.exception(e, "An unknown error occurred")
        llogger.error(traceback.format_exc())
        sys.exit(1)


def switch_command(cmd):
    """
        Switch command function of the Swarmrob CLI
    :return:
    """
    llogger = local_logger.LocalLogger()
    llogger.log_call(sys._getframe().f_code.co_name)

    if is_master_available():
        from . import master
        commands = {
            'master': master.main,
            'worker': worker.main,
            'daemon': daemon.main,
            'check': check_for_startup,
            'help': show_help,
        }
    else:
        commands = {
            'master': print_master_error_message,
            'worker': worker.main,
            'daemon': daemon.main,
            'check': check_for_startup,
            'help': show_help,
        }
    return commands[cmd]()


def check_for_startup():
    """
        Check function of the Swarmrob CLI. Checks if the given repository can be reached by this node.
    :return:
    """
    llogger = local_logger.LocalLogger()
    llogger.log_call(sys._getframe().f_code.co_name)
    params = CMDParser(arguments=[Argument.REPOSITORY]).parse_arguments()
    puts(colored.yellow("Check Network Bandwidth for repository: " + params.repository))
    try:
        result_dict = network.check_network_bandwidth_of_repository(params.repository)
        puts(colored.green("Repository is available"))
        puts(colored.green("Download: " + str(result_dict.get("download"))))
        puts(colored.green("Latency: " + str(result_dict.get("ping"))))
        print()
        return True
    except NetworkException:
        puts(colored.red("Repository is not available"))
        print()
        return False


def show_help():
    """
        Shows the help on the swarmrob CLI
    :return:
    """
    llogger = local_logger.LocalLogger()
    llogger.log_call(sys._getframe().f_code.co_name)

    with indent(4, quote='>>'):
        puts(colored.white("Command list"))
    index = 1
    if is_master_available() is True:
        with indent(5, quote=str(index) + '.'):
            puts(colored.white("master - Access all master commands. Type 'swarmrob master help' for more info."))
            index += 1
    with indent(5, quote=str(index) + '.'):
        puts(colored.white("worker - Access all worker commands. Type 'swarmrob worker help' for more info."))
    with indent(5, quote=str(index+1) + '.'):
        puts(colored.white("daemon - Access all daemon commands. Type 'swarmrob daemon help' for more info."))
    with indent(5, quote=str(index+2) + '.'):
        puts(colored.white("check - Checks for missing usage requirements and installs them if possible."))
    with indent(5, quote=str(index+3) + '.'):
        puts(colored.white("help - Prints this help page."))
    print()
    return True


def print_master_error_message():
    """
        Prints an error message if the master command is not supported
    """
    llogger = local_logger.LocalLogger()
    llogger.log_call(sys._getframe().f_code.co_name)
    if is_master_available() is False:
        puts(colored.red("Master is only supported in the full version."))
        puts("You are using the worker version.")
        puts("For a list of available commands type 'swarmrob help.")
        print()
    return True


def is_master_available():
    """
        Checks if the master is supported
    :return: True, when the master is supported
    """
    llogger = local_logger.LocalLogger()
    llogger.log_call(sys._getframe().f_code.co_name)
    try:
        from . import master
        return True
    except ImportError:
        return False
