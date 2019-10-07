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

import jsonpickle
import Pyro4
import Pyro4.errors
from clint.arguments import Args
from clint.textui import colored, indent, puts

from .logger import local_logger
from .services import edf_parser
from .utils.cmd_parser import Argument, CMDParser
from .utils.errors import NetworkException, CompositionException
from .utils import network
from .utils import pyro_interface
from .utils import table_builder
from . import daemon


sys.path.insert(0, os.path.abspath('..'))

RECURSION_LIMIT = 100000


def main():

    """
        Main function of the Swarmrob Master CLI
    :return:
    """
    llogger = local_logger.LocalLogger()
    llogger.log_call(sys._getframe().f_code.co_name)
    console_arguments = Args()
    try:
        switch_command(str(console_arguments.get(1)))
        return True
    except KeyError:
        llogger.exception(traceback.format_exc())
        with indent(4, quote='>>'):
            puts(colored.red(str(console_arguments.get(1)) + " is not a valid command"))
            puts(colored.red("Type 'swarmrob help' for a command list"))
        return False


def switch_command(cmd):
    """
        Switch command function of the Swarmrob Master CLI
    :return:
    """
    llogger = local_logger.LocalLogger()
    llogger.log_call(sys._getframe().f_code.co_name)
    commands = {
        'init': init_swarm,
        'swarm_status': swarm_status,
        'worker_status': worker_status,
        'start_swarm': start_swarm_by_compose_file,
        'help': show_help,
        }
    return commands[cmd]()


def show_help():
    """
        Shows the help on the master CLI
    :return:
    """
    llogger = local_logger.LocalLogger()
    llogger.log_call(sys._getframe().f_code.co_name)
    with indent(4, quote='>>'):
        puts(colored.white("Master command list"))
    with indent(5, quote='1.'):
        puts(colored.white("init - Initializes a new swarm."))
    with indent(5, quote='2.'):
        puts(colored.white("swarm_status - Prints the status of one swarm."))
    with indent(5, quote='3.'):
        puts(colored.white("worker_status - Prints the status of one single worker in a swarm."))
    with indent(5, quote='4.'):
        puts(colored.white("start_swarm - Starts a swarm with a given composition."))
    with indent(5, quote='5.'):
        puts(colored.white("help - Prints this help page."))
    print()
    return True


def init_swarm():
    """
        Initializes a swarm and starts a master on the predefined advertise address. The uuid of the
        swarm is randomly generated at runtime or can be specified with --swarm_uuid (Hint: Only for Development)
    :return:
    """
    llogger = local_logger.LocalLogger()
    llogger.log_call(sys._getframe().f_code.co_name)
    new_swarm = None
    params = CMDParser(program_path="master init", description="Initialize the swarm by creating a master node.",
                       arguments=[Argument.ADVERTISE_ADDRESS, Argument.INTERFACE, Argument.UUID_OPTIONAL
                                  ]).parse_arguments()

    if params.uuid is not None and '@' in params.uuid:
        params.uuid = str(params.uuid).split("@")[0]

    try:
        network_info = network.NetworkInfo(params.interface)
    except NetworkException:
        puts(colored.red("Host interface not valid. Specify a different host interface."))
        puts(colored.red("Possible options are: " + " ".join(network.get_interface_list())))
        llogger.debug("Missing host interface. Add one with option --interface.")
        return False

    if params.advertise_address is None:
        params.advertise_address = network_info.ip_address
        puts("Missing advertise address. Using advertise address " + str(params.advertise_address)
             + " given by interface.")
        llogger.debug("Missing advertise address. Using advertise address " + str(params.advertise_address)
                      + " given by interface.")

    puts(colored.yellow("Init swarm on " + params.advertise_address))
    llogger.debug("Init swarm on: %s and interface: %s", params.advertise_address, network_info.interface)

    try:
        swarmrob_daemon_proxy = pyro_interface.get_daemon_proxy(network_info.ip_address)
        sys.setrecursionlimit(RECURSION_LIMIT)

        new_swarm = jsonpickle.decode(swarmrob_daemon_proxy.create_new_swarm(params.advertise_address,
                                                                             network_info.interface,
                                                                             predefined_uuid=params.uuid))
    except RuntimeError as e:
        puts(colored.red(str(e)))
        llogger.exception(str(e))
    except NetworkException as e:
        puts(colored.red(str(e)))
        daemon.check_daemon_running(network_info.interface)
    except (Pyro4.errors.DaemonError, Pyro4.errors.CommunicationError) as e:
        puts(colored.red("A daemon related error occurred - " + str(e)))
        llogger.error("A daemon related error occurred - " + str(e))
        llogger.exception(traceback.format_exc())
        daemon.check_daemon_running(network_info.interface)
    if new_swarm is not None:
        puts(colored.yellow("Swarm created: Type 'swarmrob worker join --uuid " + str(new_swarm.uuid) + "@" + str(
                new_swarm.advertise_address) + "' on the node to join the swarm"))
        llogger.debug("Swarm created: Type 'swarmrob worker join --uuid " + str(new_swarm.uuid) + "@" + str(
                new_swarm.advertise_address) + "' on the node to join the swarm")
        return True
    else:
        llogger.error("Can't create the swarm")
        puts(colored.red("Can't create the swarm"))
        return False


def swarm_status():
    """
        The status of the swarm (advertise address, uuid, worker list, ...). The swarm is represented as a table
    :return:
    """
    llogger = local_logger.LocalLogger()
    llogger.log_call(sys._getframe().f_code.co_name)
    params = CMDParser(program_path="master swarm_status", description="Print the status of the swarm.",
                       arguments=[Argument.INTERFACE]).parse_arguments()

    try:
        network_info = network.NetworkInfo(params.interface)
    except NetworkException:
        puts(colored.red("Host interface not valid. Specify a different host interface."))
        puts(colored.red("Possible options are: " + " ".join(network.get_interface_list())))
        llogger.debug("Missing host interface. Add one with option --interface.")
        return False

    try:
        swarmrob_daemon_proxy = pyro_interface.get_daemon_proxy(network_info.ip_address)
        swarm_status_as_json = swarmrob_daemon_proxy.get_swarm_status_as_json()
        if swarm_status_as_json is None:
            puts(colored.red("No swarm status available. Is the master initialized?"))
            return False
        print(table_builder.swarm_status_to_table(jsonpickle.decode(swarm_status_as_json)))
        print(table_builder.swarm_status_to_worker_list(jsonpickle.decode(swarm_status_as_json)))
        return True
    except NetworkException as e:
        puts(colored.red(str(e)))
        daemon.check_daemon_running(network_info.interface)
    return False


def worker_status():
    """
        The status of a specific worker. The worker can be defined by
        --worker_uuid and represented as a table
    :return:
    """
    llogger = local_logger.LocalLogger()
    llogger.log_call(sys._getframe().f_code.co_name)
    params = CMDParser(program_path="master worker_status", description="Print the status of a single worker.",
                       arguments=[Argument.INTERFACE, Argument.WORKER_UUID]).parse_arguments()

    try:
        network_info = network.NetworkInfo(params.interface)
    except NetworkException:
        puts(colored.red("Host interface not valid. Specify a different host interface."))
        puts(colored.red("Possible options are: " + " ".join(network.get_interface_list())))
        llogger.debug("Missing host interface. Add one with option --interface.")
        return False

    try:
        swarmrob_daemon_proxy = pyro_interface.get_daemon_proxy(network_info.ip_address)
    except NetworkException as e:
        puts(colored.red(str(e)))
        daemon.check_daemon_running(network_info.interface)
        return False

    swarm_status_as_json = swarmrob_daemon_proxy.get_swarm_status_as_json()
    if swarm_status_as_json is None:
        puts(colored.red("No worker found with id " + params.worker_uuid))
        return False
    worker_list = list(dict(jsonpickle.decode(swarm_status_as_json)._worker_list).items())

    worker_info = None
    for _, worker_list_val in worker_list:
        worker = jsonpickle.decode(worker_list_val.get_info_as_json())
        if str(worker.uuid) == params.worker_uuid:
            worker_info = worker

    if worker_info is None:
        puts(colored.red("No worker found with id " + params.worker_uuid))
        return False

    print(table_builder.worker_status_to_table(worker_info))
    print(table_builder.service_list_to_table(worker_info))
    return True


def start_swarm_by_compose_file():
    """
        Starts a predefined swarm based on a docker compose file.
    :return:
    """
    llogger = local_logger.LocalLogger()
    llogger.log_call(sys._getframe().f_code.co_name)
    params = CMDParser(program_path="master start_swarm", description="Run an EDF file inside a swarm.",
                       arguments=[Argument.INTERFACE, Argument.UUID, Argument.COMPOSE_FILE, Argument.LOG_FOLDER,
                                  Argument.LOG_IDENTIFIER]).parse_arguments()

    try:
        network_info = network.NetworkInfo(params.interface)
    except NetworkException:
        puts(colored.red("Host interface not valid. Specify a different host interface."))
        puts(colored.red("Possible options are: " + " ".join(network.get_interface_list())))
        llogger.debug("Missing host interface. Add one with option --interface.")
        return False

    try:
        swarm_composition = edf_parser.create_service_composition_from_edf(params.compose_file)
    except CompositionException as e:
        puts(colored.red(str(e)))
        llogger.exception(e, "Unable to load edf file")
        return False

    if swarm_composition.is_empty():
        puts(colored.red("No services found. Make sure the edf file exists and contains services."))
        return False

    llogger.debug("Try to start swarm: %s with the following composition", params.uuid)
    llogger.debug("\n" + swarm_composition.format_service_composition_as_table())
    puts("Try to start swarm: " + params.uuid + " with the following composition")
    puts("\n" + swarm_composition.format_service_composition_as_table())

    try:
        swarmrob_daemon_proxy = pyro_interface.get_daemon_proxy(network_info.ip_address)
    except NetworkException as e:
        puts(colored.red(str(e)))
        daemon.check_daemon_running(network_info.interface)
        return False

    if params.log_identifier is not None or params.log_folder is not None:
        swarmrob_daemon_proxy.configure_evaluation_logger(params.log_folder, params.log_identifier, True)
    swarmrob_daemon_proxy.reset_evaluation_logger()

    try:
        swarmrob_daemon_proxy.start_swarm_by_composition(jsonpickle.encode(swarm_composition), params.uuid)
        puts(colored.yellow("Successfully started swarm"))
        return True
    except RuntimeError as e:
        puts("Error while starting swarm\n" + str(e))
        llogger.exception(e, "Error while starting swarm")
        return False
