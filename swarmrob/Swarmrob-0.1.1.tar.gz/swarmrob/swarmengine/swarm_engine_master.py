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
import uuid
import socket
import traceback

import jsonpickle
import Pyro4
import Pyro4.naming

from ..logger import local_logger
from ..logger import remote_logging_server
from ..utils.errors import DockerException, NetworkException
from . import swarm_engine


@Pyro4.expose
@Pyro4.behavior(instance_mode="single")
class Master:
    """
    Proxy class for remote procedure calls of the master engine
    """

    def __init__(self, interface, advertise_address):
        llogger = local_logger.LocalLogger()
        llogger.log_method_call(self.__class__.__name__, sys._getframe().f_code.co_name)
        self._advertise_address = advertise_address
        self._hostname = socket.gethostname()
        self._interface = interface
        self._uuid = uuid.uuid4().hex
        self._swarm_uuid = None
        self._remote_logging_server = None

    @property
    def swarm_uuid(self):  # exposed as 'proxy.attr' remote attribute
        """
            RPC property method for self.swarm_uuid
        :return: UUID of the swarm
        """
        llogger = local_logger.LocalLogger()
        llogger.log_method_call(self.__class__.__name__, sys._getframe().f_code.co_name)
        return self._swarm_uuid

    @swarm_uuid.setter
    def swarm_uuid(self, swarm_uuid):  # exposed as 'proxy.attr' writable
        """
            RPC setter method for self.swarm_uuid
        :param swarm_uuid:
        :return:
        """
        llogger = local_logger.LocalLogger()
        llogger.log_method_call(self.__class__.__name__, sys._getframe().f_code.co_name)
        self._swarm_uuid = swarm_uuid

    @property
    def uuid(self):  # exposed as 'proxy.attr' remote attribute
        """
            RPC property method for self.uuid
        :return: UUID of the master
        """
        llogger = local_logger.LocalLogger()
        llogger.log_method_call(self.__class__.__name__, sys._getframe().f_code.co_name)
        return self._uuid

    @uuid.setter
    def uuid(self, uuid):  # exposed as 'proxy.attr' writable
        """
            RPC setter method for self.uuid
        :param uuid: UUID of the master
        :return:
        """
        llogger = local_logger.LocalLogger()
        llogger.log_method_call(self.__class__.__name__, sys._getframe().f_code.co_name)
        self._uuid = uuid

    @property
    def advertise_address(self):  # exposed as 'proxy.attr' remote attribute
        """
            RPC property method for self.advertise_address
        :return: Advertise address of the master
        """
        llogger = local_logger.LocalLogger()
        llogger.log_method_call(self.__class__.__name__, sys._getframe().f_code.co_name)
        return self._advertise_address

    @advertise_address.setter
    def advertise_address(self, advertise_address):  # exposed as 'proxy.attr' writable
        """
            RPC setter method for self.advertise_address
        :param advertise_address: Advertise address of the master
        :return:
        """
        llogger = local_logger.LocalLogger()
        llogger.log_method_call(self.__class__.__name__, sys._getframe().f_code.co_name)
        self._advertise_address = advertise_address
        llogger.debug("AdvertiseAddress set to %s", advertise_address)

    @property
    def hostname(self):  # exposed as 'proxy.attr' remote attribute
        """
            RPC property method for self.hostname
        :return: Hostname of the master
        """
        llogger = local_logger.LocalLogger()
        llogger.log_method_call(self.__class__.__name__, sys._getframe().f_code.co_name)
        return self._hostname

    @hostname.setter
    def hostname(self, hostname):  # exposed as 'proxy.attr' writable
        """
            RPC setter method for self.hostname
        :param hostname: Hostname of the master
        :return:
        """
        llogger = local_logger.LocalLogger()
        llogger.log_method_call(self.__class__.__name__, sys._getframe().f_code.co_name)
        self._hostname = hostname
        llogger.debug("hostname set to %s", hostname)

    @property
    def interface(self):  # exposed as 'proxy.attr' remote attribute
        """
            RPC property method for self.interface
        :return: Interface of the master
        """
        llogger = local_logger.LocalLogger()
        llogger.log_method_call(self.__class__.__name__, sys._getframe().f_code.co_name)
        return self._interface

    @interface.setter
    def interface(self, interface):  # exposed as 'proxy.attr' writable
        """
            RPC setter method for self.interface
        :param interface: Interface of master
        :return:
        """
        llogger = local_logger.LocalLogger()
        llogger.log_method_call(self.__class__.__name__, sys._getframe().f_code.co_name)
        self._interface = interface
        llogger.debug("interface set to %s", interface)

    def register_worker_at_master(self, swarm_uuid_as_json, new_worker_as_json):
        """
            RPC method for registering a worker in the swarm
        :param swarm_uuid_as_json: UUID of the swarm as JSON
        :param new_worker_as_json: New worker of the swarm as JSON
        :return: Swarm status as JSON
        """
        llogger = local_logger.LocalLogger()
        llogger.log_method_call(self.__class__.__name__, sys._getframe().f_code.co_name)
        llogger.debug("Try to register new worker: %s", str(new_worker_as_json))
        if swarm_engine.SwarmEngine().swarm is None:
            raise RuntimeError("Swarm not initialized")
        if swarm_uuid_as_json is None or new_worker_as_json is None:
            raise RuntimeError("A parameter is None")
        new_worker = jsonpickle.decode(new_worker_as_json)
        swarm_uuid = jsonpickle.decode(swarm_uuid_as_json)
        new_worker.hostname = swarm_engine.SwarmEngine().swarm.get_unique_worker_hostname(new_worker.hostname)
        try:
            swarm_engine.SwarmEngine().register_worker_in_swarm(swarm_uuid, new_worker)
        except DockerException:
            raise RuntimeError(traceback.format_exc())
        return self.get_swarm_status_as_json()

    def unregister_worker_at_master(self, swarm_uuid_as_json, worker_uuid_as_json):
        """
            RPC method for unregistering a worker in the swarm
        :param swarm_uuid_as_json: UUID of the swarm as JSON
        :param worker_uuid_as_json: UUID of the worker as JSON
        :return: Swarm status as JSON
        """
        llogger = local_logger.LocalLogger()
        llogger.log_method_call(self.__class__.__name__, sys._getframe().f_code.co_name)
        if swarm_engine.SwarmEngine().swarm is None:
            raise RuntimeError("Swarm not initialized")
        if swarm_uuid_as_json is None or worker_uuid_as_json is None:
            return False
        worker_uuid = jsonpickle.decode(worker_uuid_as_json)
        llogger.debug("Try to unregister worker: %s", worker_uuid)
        swarm_uuid = jsonpickle.decode(swarm_uuid_as_json)
        return swarm_engine.SwarmEngine().unregister_worker_in_swarm(swarm_uuid, worker_uuid)

    def get_swarm_status_as_json(self):
        """
            RPC method for returning the swarm status as JSON
        :return: Swarm status as JSON
        """
        llogger = local_logger.LocalLogger()
        llogger.log_method_call(self.__class__.__name__, sys._getframe().f_code.co_name)
        llogger.debug("Returning swarm with uuid: %s", self.swarm_uuid)
        llogger.debug(jsonpickle.encode(swarm_engine.SwarmEngine().swarm))
        return jsonpickle.encode(swarm_engine.SwarmEngine().swarm)

    def start_remote_logging_server(self):
        """
            Start remote logging server of the swarm
        :return:
        """
        llogger = local_logger.LocalLogger()
        llogger.log_method_call(self.__class__.__name__, sys._getframe().f_code.co_name)
        self._remote_logging_server = remote_logging_server.RemoteLoggingServer(self._interface)
        try:
            self._remote_logging_server = remote_logging_server.RemoteLoggingServer(self._interface)
            self._remote_logging_server.start()
            llogger.debug("Started logging server for swarm: %s on interface: %s with hostname: %s:%s",
                          self._swarm_uuid, self._remote_logging_server.interface, self._remote_logging_server.hostname,
                          self._remote_logging_server.port)
        except NetworkException as e:
            llogger.exception(e, "Unable to start Remote Logger using interface " + self._interface)

    def get_remote_logging_server_info(self):
        """
            Returns the remote logging server hostname and port
        :return: hostname, port
        """
        llogger = local_logger.LocalLogger()
        llogger.log_method_call(self.__class__.__name__, sys._getframe().f_code.co_name)
        if self._remote_logging_server is not None:
            return self._remote_logging_server.hostname, self._remote_logging_server.port
        return None, None
