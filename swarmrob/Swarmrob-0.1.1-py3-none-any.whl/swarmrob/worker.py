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

from clint.arguments import Args
from clint.textui import puts, colored, indent

import jsonpickle

from .logger import local_logger
from .utils.cmd_parser import Argument, CMDParser
from .utils.errors import NetworkException
from .utils import network, pyro_interface, table_builder
from . import daemon


sys.path.insert(0, os.path.abspath('..'))


def main():
    """
        Main method of the worker
    :return:
    """
    llogger = local_logger.LocalLogger()
    llogger.log_call(sys._getframe().f_code.co_name)
    args = Args()
    try:
        switch_command(str(args.get(1)))
        return True
    except KeyError:
        with indent(4, quote='>>'):
            puts(colored.red(str(args.get(1)) + " is not a valid command"))
            puts(colored.red("Type 'swarmrob help' for a command list"))
        return False


def switch_command(cmd):
    """
        Switch-case method of the worker commands
    :param cmd: command string typed in by the user
    :return:
    """
    llogger = local_logger.LocalLogger()
    llogger.log_call(sys._getframe().f_code.co_name)
    commands = {
        'join': join_swarm,
        'leave': leave_swarm,
        'status': status_worker,
        'help': show_help,

    }
    return commands[cmd]()


def show_help():
    """
        Shows the help on the worker CLI
    :return:
    """
    llogger = local_logger.LocalLogger()
    llogger.log_call(sys._getframe().f_code.co_name)
    with indent(4, quote='>>'):
        puts(colored.white("Worker command list"))
    with indent(5, quote='1.'):
        puts(colored.white("join - Joins the given swarm as a worker."))
    with indent(5, quote='2.'):
        puts(colored.white("leave - Leaves the given swarm."))
    with indent(5, quote='3.'):
        puts(colored.white("status - Prints the current status of the worker."))
    with indent(5, quote='4.'):
        puts(colored.white("help - Prints this help page."))
    print()
    return True


def join_swarm():
    """
        Abstracts the join_swarm command on the worker CLI
    :return:
    """
    llogger = local_logger.LocalLogger()
    llogger.log_call(sys._getframe().f_code.co_name)
    puts(colored.yellow("Join swarm"))
    params = CMDParser(program_path="worker join", description="Join a swarm as a worker.",
                       arguments=[Argument.INTERFACE, Argument.UUID, Argument.WORKER_UUID_OPTIONAL]).parse_arguments()

    if '@' not in params.uuid:
        puts(colored.red("Invalid uuid. Correct syntax is <uuid>@<ns_uri>."))
        llogger.debug("Invalid uuid. Correct syntax is <uuid>@<ns_uri>.")
        return False

    swarm_uuid = str(params.uuid).split("@")[0]
    nameservice_uri = str(params.uuid).split("@")[1]

    try:
        network_info = network.NetworkInfo(params.interface)
    except NetworkException:
        puts(colored.red("Host interface not valid. Specify a different host interface."))
        puts(colored.red("Possible options are: " + " ".join(network.get_interface_list())))
        llogger.debug("Missing host interface. Add one with option --interface.")
        return False

    try:
        proxy = pyro_interface.get_daemon_proxy(network_info.ip_address)
        proxy.register_worker(swarm_uuid, nameservice_uri, params.worker_uuid)
        return True
    except NetworkException as e:
        puts(colored.red(str(e)))
        daemon.check_daemon_running(network_info.interface)
        return False
    except RuntimeError as e:
        puts(colored.red(str(e)))
        llogger.error(e)
        return False


def leave_swarm():
    """
        Command to remove the worker from the swarm
    :return:
    """
    llogger = local_logger.LocalLogger()
    llogger.log_call(sys._getframe().f_code.co_name)
    puts(colored.yellow("Leave swarm"))
    params = CMDParser(program_path="worker leave", description="Leave a swarm.",
                       arguments=[Argument.INTERFACE, Argument.SWARM_UUID, Argument.WORKER_UUID]).parse_arguments()

    if '@' not in params.swarm_uuid:
        puts(colored.red("Invalid swarm uuid. Correct syntax is <uuid>@<ns_uri>."))
        llogger.debug("Invalid swarm uuid. Correct syntax is <uuid>@<ns_uri>.")
        return False

    swarm_uuid = str(params.swarm_uuid).split("@")[0]
    nameservice_uri = str(params.swarm_uuid).split("@")[1]
    worker_uuid = str(params.worker_uuid)

    try:
        network_info = network.NetworkInfo(params.interface)
    except NetworkException:
        puts(colored.red("Host interface not valid. Specify a different host interface."))
        puts(colored.red("Possible options are: " + " ".join(network.get_interface_list())))
        llogger.debug("Missing host interface. Add one with option --interface.")
        return False

    try:
        proxy = pyro_interface.get_daemon_proxy(network_info.ip_address)
        removed = proxy.unregister_worker(swarm_uuid, nameservice_uri, worker_uuid)
        if removed:
            puts("Successfully removed worker with uuid " + worker_uuid + " from swarm " + swarm_uuid)
            llogger.debug("Successfully removed worker with uuid %s from swarm %s", worker_uuid, swarm_uuid)
            return True
        else:
            puts(colored.red("Failed to remove worker with uuid " + worker_uuid + " from swarm " + swarm_uuid))
            llogger.error("Failed to remove worker with uuid %s from swarm %s", worker_uuid, swarm_uuid)
    except NetworkException as e:
        puts(colored.red(str(e)))
        daemon.check_daemon_running(network_info.interface)
    return False


def status_worker():
    """
        Shows the status of the worker on the CLI
    :return:
    """
    llogger = local_logger.LocalLogger()
    llogger.log_call(sys._getframe().f_code.co_name)
    params = CMDParser(program_path="worker status", description="Show the status of the worker.",
                       arguments=[Argument.INTERFACE]).parse_arguments()
    try:
        network_info = network.NetworkInfo(params.interface)
    except NetworkException:
        puts(colored.red("Host interface not valid. Specify a different host interface."))
        puts(colored.red("Possible options are: " + " ".join(network.get_interface_list())))
        llogger.debug("Missing host interface. Add one with option --interface.")
        return False

    try:
        proxy = pyro_interface.get_daemon_proxy(network_info.ip_address)
        worker_status_as_json = proxy.get_worker_status_as_json()
        print(table_builder.worker_daemon_status_to_table(jsonpickle.decode(worker_status_as_json)))
        return True
    except NetworkException as e:
        puts(colored.red(str(e)))
        daemon.check_daemon_running(network_info.interface)
        return False
