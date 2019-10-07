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
import netifaces
import os

import speedtest

from ..logger import local_logger
from .config import Config, Section, Option
from .errors import NetworkException

SPEEDTEST_MINI_PORT = 8085

config = Config()


class NetworkInfo:

    def __init__(self, interface=None):
        """
            Initialises NetworkInfo by collecting network information
        :param interface: interface used by the network
        """
        llogger = local_logger.LocalLogger()
        llogger.log_method_call(self.__class__.__name__, sys._getframe().f_code.co_name)
        if interface is None:
            self._interface = get_default_interface()
            llogger.debug("Using default interface " + self._interface)
        else:
            self._interface = interface
        self._ip_address = get_ip_of_interface(self._interface)

    @property
    def interface(self):
        return self._interface

    @property
    def ip_address(self):
        return self._ip_address


def check_network_bandwidth_of_repository(tag_of_repository):
    """
        Check the network bandwidth based on the network connection to the repository
    :param tag_of_repository: Tag of the repository
    :return: dictionary with results or None
    """
    llogger = local_logger.LocalLogger()
    llogger.log_call(sys._getframe().f_code.co_name)
    if tag_of_repository is None:
        raise NetworkException("Repository is None")
    try:
        s = speedtest.Speedtest()
        s.get_best_server(s.set_mini_server("http://" + str(tag_of_repository) + ":" + str(SPEEDTEST_MINI_PORT)))
        s.download()
        results_dict = s.results.dict()
        llogger.debug(results_dict)
        return results_dict
    except (speedtest.SpeedtestMiniConnectFailure, speedtest.ConfigRetrievalError):
        raise NetworkException("Unable to check network bandwidth")


def get_ip_of_interface(interface_name):
    """
        Get the IP of the host based on the name of the interface
    :param interface_name: Name of the interface
    :return: ip of the interface if it exists or None
    """
    llogger = local_logger.LocalLogger()
    llogger.log_call(sys._getframe().f_code.co_name)
    if interface_name not in get_interface_list():
        llogger.debug("The interface " + str(interface_name) + " does not exist")
        raise NetworkException("The interface " + str(interface_name) + " does not exist")

    try:
        return netifaces.ifaddresses(interface_name)[2][0]['addr']
    except KeyError:
        llogger.debug("Unable to get ip address for interface " + str(interface_name))
        raise NetworkException("Unable to get ip address for interface " + str(interface_name))


def get_interface_list():
    """
        Get a list of available interfaces on the current system
    :return: list of available interfaces
    """
    llogger = local_logger.LocalLogger()
    llogger.log_call(sys._getframe().f_code.co_name)
    return netifaces.interfaces()


def get_default_interface():
    """
        Get the first interface listed in hostname
    :return: interface
    """
    llogger = local_logger.LocalLogger()
    llogger.log_call(sys._getframe().f_code.co_name)
    interface = config.get(Section.INTERNET, Option.INTERFACE)
    if interface is not None:
        return interface

    # TODO: Only works on Linux
    in_stream = os.popen("hostname -I")
    try:
        ip_address = str(in_stream.read()).split(" ")[0]
        if ip_address is not None:
            return get_interface_of_ip(ip_address)
    except KeyError:
        raise NetworkException("Unable to find a default interface")
    finally:
        in_stream.close()


def get_interface_of_ip(ip_address):
    """
        Get the name of the interface with the given ip address
    :param ip_address: ip address of the searched interface
    :return: interface if found or None
    """
    llogger = local_logger.LocalLogger()
    llogger.log_call(sys._getframe().f_code.co_name)
    for interface in get_interface_list():
        try:
            if str(ip_address) == str(netifaces.ifaddresses(interface)[2][0]['addr']):
                return interface
        except KeyError:
            pass
    raise NetworkException("No interface available for ip address " + str(ip_address))
