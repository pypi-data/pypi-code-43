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
import traceback
import time
from multiprocessing import Process

import Pyro4
import Pyro4.util
import Pyro4.naming
from Pyro4.errors import CommunicationError, NamingError

from ..logger import local_logger
from ..utils.errors import NetworkException

PYRO_NS_BROADCAST = False
PYRO_NS_PORT = 9090

SWARMROBD_IDENTIFIER = "swarmrob.swarmrobd"


def get_proxy(rpc_name, ip_address):
    """
        Returns a proxy object based on its identifier and the ip of the name service
    :param rpc_name: name of the remote object
    :param ip_address: IP address of the name service
    :return: Daemon proxy
    """
    llogger = local_logger.LocalLogger()
    llogger.log_call(sys._getframe().f_code.co_name)
    try:
        sys.excepthook = Pyro4.util.excepthook
        pyro_nameservice = get_name_service(ip_address)
        uri = pyro_nameservice.lookup(rpc_name)
        proxy = Pyro4.Proxy(uri)
        return proxy
    except (CommunicationError, NamingError) as e:
        llogger.exception(e, "Naming service not available. Is it running and is the master registered?")
        llogger.error(traceback.format_exc())
        raise NetworkException("Naming service not available. Is it running and is the master registered?")


def get_daemon_proxy(ns_ip):
    """
        Returns a proxy object using the default daemon identifier
    :param ns_ip: IP address of the name service
    :return: Daemon proxy
    """
    llogger = local_logger.LocalLogger()
    llogger.log_call(sys._getframe().f_code.co_name)
    return get_proxy(SWARMROBD_IDENTIFIER, ns_ip)


def _start_nameservice(host_ip):
    """
        Starts the name service loop
    :param host_ip: IP address of the name service
    :return:
    """
    llogger = local_logger.LocalLogger()
    llogger.log_call(sys._getframe().f_code.co_name)
    Pyro4.naming.startNSloop(str(host_ip), PYRO_NS_PORT)


def start_name_service(ip_address):
    """
        Starts the name service in a new thread
    :param ip_address: IP address of the name service
    :return: NameServer object
    """
    p = Process(target=_start_nameservice, args=(ip_address,))
    p.start()
    time.sleep(1.0)
    return Pyro4.locateNS(host=ip_address, port=PYRO_NS_PORT)


def get_name_service(ip_address, start=False):
    """
        Locates the Pyro4 name service
    :param ip_address: IP address of the name service
    :param start: True, if the name service should be started when it does not exist
    :raises NetworkException
    :return: NameServer object
    """
    llogger = local_logger.LocalLogger()
    llogger.log_call(sys._getframe().f_code.co_name)
    try:
        return Pyro4.locateNS(host=ip_address, port=PYRO_NS_PORT, broadcast=PYRO_NS_BROADCAST)
    except NamingError as e:
        if start:
            llogger.debug("Naming service not available. Starting naming service.")
            return start_name_service(ip_address)
        else:
            llogger.exception(e, "Naming service not available. Is it running and is the master registered?")
            llogger.error(traceback.format_exc())
            raise NetworkException("Naming service not available. Is it running and is the master registered?")


def clear_name_service(name_service):
    """
        Clears all the registered objects of the name service
    :param name_service: NameServer object
    :return:
    """
    llogger = local_logger.LocalLogger()
    llogger.log_call(sys._getframe().f_code.co_name)
    dict_of_registered_objects = name_service.list()
    for key_of_registered_objects, _ in list(dict_of_registered_objects.items()):
        llogger.debug("Remove %s from nameserver", key_of_registered_objects)
        name_service.remove(name=key_of_registered_objects)
    name_service.remove()
