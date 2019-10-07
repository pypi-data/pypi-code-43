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
import requests
import signal

import docker
import docker.errors
import jsonpickle
import Pyro4
import Pyro4.naming
import Pyro4.errors
from clint.arguments import Args
from clint.textui import puts, colored, indent

from .logger import local_logger
from .swarmengine import swarmrob_d
from .utils.cmd_parser import Argument, CMDParser
from .utils.errors import NetworkException
from .utils import network, process_helper, cmd_helper, pyro_interface

SWARMROB_MASTER_URI_ENV = "SWARMROB_MASTER_URI"
WORKER_PORT = 0
PID_FILE = "/var/run/swarmrobd.pid"
sys.path.insert(0, os.path.abspath('..'))


def signal_handler_shutdown(signalnum, frame):
    """
        Signal handler for closing the ETCD connection to the cluster when an interrupt occurred
    :param signalnum:
    :param frame:
    :return:
    """
    llogger = local_logger.LocalLogger()
    llogger.log_call(sys._getframe().f_code.co_name)
    if os.path.exists(PID_FILE):
        os.remove(PID_FILE)
    sys.exit()


def main():
    """
        Main method of the swarmrob daemon
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
        Method for switch-case the daemon mode
    :param cmd: first command word typed in by the user
    :return:
    """
    llogger = local_logger.LocalLogger()
    llogger.log_call(sys._getframe().f_code.co_name)
    commands = {
        'start': start_daemon,
        'status': status_daemon,
        'stop': stop_daemon,
        'help': show_help,
        'check': check_docker,

    }
    return commands[cmd]()


def show_help():
    """
        Method for showing help in the daemon CLI
    :return:
    """
    llogger = local_logger.LocalLogger()
    llogger.log_call(sys._getframe().f_code.co_name)
    with indent(4, quote='>>'):
        puts(colored.white("Daemon command list"))
    with indent(5, quote='1.'):
        puts(colored.white("start - Starts the swarmrob daemon."))
    with indent(5, quote='2.'):
        puts(colored.white("status - Prints the current status of the swarmrob daemon."))
    with indent(5, quote='3.'):
        puts(colored.white("stop - Stops the swarmrob daemon."))
    with indent(5, quote='4.'):
        puts(colored.white("check - Checks if docker is installed correctly."))
    with indent(5, quote='5.'):
        puts(colored.white("help - Prints this help page."))
    print()
    return True


def log_pid():
    llogger = local_logger.LocalLogger()
    llogger.log_call(sys._getframe().f_code.co_name)
    puts(colored.green("SwarmRob Daemon started with PID: " + str(os.getpid())))
    f = open(PID_FILE, "w")
    f.write(str(os.getpid()))
    f.close()
    return True


def start_daemon(interface=None):
    """
        Method for starting and registering the daemon at the nameservice
    :return:
    """
    llogger = local_logger.LocalLogger()
    llogger.log_call(sys._getframe().f_code.co_name)
    params = CMDParser(program_path="daemon start", description="Start the swarmrob daemon.",
                       arguments=[Argument.INTERFACE, Argument.DAEMONIZE]).parse_arguments()

    ret_code = 0
    if params.daemonize:
        ret_code = process_helper.create_daemon()
    os.chdir('/')
    log_pid()
    host_interface = params.interface
    if host_interface is None:
        host_interface = interface
    try:
        network_info = network.NetworkInfo(host_interface)
    except NetworkException:
        puts(colored.red("Host interface not valid. Specify a different host interface."))
        puts(colored.red("Possible options are: " + " ".join(network.get_interface_list())))
        llogger.debug("Missing host interface. Add one with option --interface.")
        return False

    pyro_nameservice_object = pyro_interface.get_name_service(network_info.ip_address, start=True)
    pyro_interface.clear_name_service(pyro_nameservice_object)
    with Pyro4.Daemon(host=network_info.ip_address, port=WORKER_PORT) as pyro_daemon:
        daemon_uri = pyro_daemon.register(swarmrob_d.SwarmRobDaemon(network_info.interface, pyro_daemon))
        pyro_nameservice_object.register(pyro_interface.SWARMROBD_IDENTIFIER, daemon_uri)
        signal.signal(signal.SIGINT, signal_handler_shutdown)
        llogger.debug("Daemon started. Object URI = %s", daemon_uri)
        puts(colored.green("Daemon started. Object URI = " + str(daemon_uri)))
        pyro_daemon.requestLoop(swarmrob_d.SwarmRobDaemon().is_daemon_running)
    sys.exit(ret_code)


def check_daemon_running(interface=None):
    llogger = local_logger.LocalLogger()
    llogger.log_call(sys._getframe().f_code.co_name)
    # Check if daemon is running and start it
    try:
        try:
            network_info = network.NetworkInfo(interface)
        except NetworkException:
            puts(colored.red("Host interface not valid. Specify a different host interface."))
            puts(colored.red("Possible options are: " + " ".join(network.get_interface_list())))
            return False
        pyro_interface.get_daemon_proxy(network_info.ip_address)
        puts(colored.green("Daemon running"))
    except NetworkException:
        puts(colored.red("Daemon not running"))
        result = cmd_helper.query_yes_no("Start daemon?")
        if result:
            start_daemon(interface)
    return True


def stop_daemon():
    """
        Method for stopping the daemon and unregistering the daemon at the nameservice
    :return:
    """
    llogger = local_logger.LocalLogger()
    llogger.log_call(sys._getframe().f_code.co_name)
    params = CMDParser(program_path="daemon stop", description="Stop the swarmrob daemon.",
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
        if proxy.is_daemon_running():
            pid = proxy.shutdown(network_info.ip_address)
            os.kill(pid, signal.SIGKILL)
        else:
            puts(colored.red("Daemon is not running"))
            llogger.debug("Status Daemon: Daemon is not running")
    except NetworkException as e:
        puts(colored.red(str(e)))
        return False
    return True


def status_daemon():
    """
        Method for showing the status of the daemon at the daemon CLI
    :return:
    """
    llogger = local_logger.LocalLogger()
    llogger.log_call(sys._getframe().f_code.co_name)
    params = CMDParser(program_path="daemon status", description="Print the daemon status.",
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
        if proxy.is_daemon_running():
            daemon_mode = jsonpickle.decode(proxy.get_mode())
            puts(colored.green("Daemon is running and in mode: " + str(daemon_mode.value)))
            llogger.debug("Status Daemon: Daemon is running in mode: %s", str(daemon_mode.value))
            return True
        else:
            puts(colored.red("Daemon is not running"))
            llogger.debug("Status Daemon: Daemon is not running")
    except NetworkException as e:
        puts(colored.red(str(e)))
    return False


def check_docker():
    """
        Helper method for checking if docker is installed
    :return:
    """
    llogger = local_logger.LocalLogger()
    llogger.log_call(sys._getframe().f_code.co_name)
    try:
        docker_client = docker.from_env()
        docker_client.containers.run("hello-world")
        puts("Running a test docker environment was successful")
        llogger.debug("Running a test docker environment was successful")
        docker_client.close()
        return True
    except (docker.errors.APIError, requests.exceptions.ConnectionError) as e:
        print(e)
        puts(colored.red("Unable to start a docker environment."))
        llogger.exception(e, "Unable to start a docker environment.")
        return False
