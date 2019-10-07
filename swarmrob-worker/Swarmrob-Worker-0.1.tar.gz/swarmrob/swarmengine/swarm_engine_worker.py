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
import psutil
import socket
import traceback

import jsonpickle
import Pyro4
import Pyro4.naming

from ..dockerengine import docker_container_list
from ..dockerengine import docker_interface
from ..logger import local_logger
from ..logger import remote_logger
from ..utils import network
from ..utils.errors import DockerException, NetworkException


@Pyro4.expose
@Pyro4.behavior(instance_mode="single")
class Worker:

    def __init__(self, swarm_uuid, interface):
        """
            Initialization method of a worker object
        :param swarm_uuid: uuid of the swarm the worker is assigned to
        :param interface: the interface the worker should listen on
        """
        llogger = local_logger.LocalLogger()
        llogger.log_method_call(self.__class__.__name__, sys._getframe().f_code.co_name)
        self._advertise_address = network.get_ip_of_interface(interface)
        self._interface = interface
        self._hostname = socket.gethostname()
        self._uuid = uuid.uuid4().hex
        self._swarm_uuid = swarm_uuid
        self._remote_logger = None
        self._container_list = docker_container_list.DockerContainerList()

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
        :return: UUID of the worker
        """
        llogger = local_logger.LocalLogger()
        llogger.log_method_call(self.__class__.__name__, sys._getframe().f_code.co_name)
        return self._uuid

    @uuid.setter
    def uuid(self, uuid):  # exposed as 'proxy.attr' writable
        """
            RPC setter method for self.uuid
        :param uuid: UUID of the worker
        :return:
        """
        llogger = local_logger.LocalLogger()
        llogger.log_method_call(self.__class__.__name__, sys._getframe().f_code.co_name)
        self._uuid = uuid

    @property
    def advertise_address(self):  # exposed as 'proxy.attr' remote attribute
        """
            RPC property method for self.advertise_address
        :return: Advertise address of the worker
        """
        llogger = local_logger.LocalLogger()
        llogger.log_method_call(self.__class__.__name__, sys._getframe().f_code.co_name)
        return self._advertise_address

    @advertise_address.setter
    def advertise_address(self, advertise_address):  # exposed as 'proxy.attr' writable
        """
            RPC setter method for self.advertise_address
        :param advertise_address: Advertise address of the worker
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
        :return: Hostname of the worker
        """
        llogger = local_logger.LocalLogger()
        llogger.log_method_call(self.__class__.__name__, sys._getframe().f_code.co_name)
        return self._hostname

    @hostname.setter
    def hostname(self, hostname):  # exposed as 'proxy.attr' writable
        """
            RPC setter method for self.hostname
        :param hostname: Hostname of the worker
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
        :return: Interface of the worker
        """
        llogger = local_logger.LocalLogger()
        llogger.log_method_call(self.__class__.__name__, sys._getframe().f_code.co_name)
        return self._interface

    @interface.setter
    def interface(self, interface):  # exposed as 'proxy.attr' writable
        """
            RPC setter method for self.interface
        :param interface: Interface of worker
        :return:
        """
        llogger = local_logger.LocalLogger()
        llogger.log_method_call(self.__class__.__name__, sys._getframe().f_code.co_name)
        self._interface = interface
        llogger.debug("interface set to %s", interface)

    def start_remote_logger(self, hostname, port):
        """
            RPC method for starting the remote logger on the worker
        :param hostname:  Hostname of the remote logging server
        :param port: Port of the remote logging server
        :return: True when the remote logger started successfully
        """
        llogger = local_logger.LocalLogger()
        llogger.log_method_call(self.__class__.__name__, sys._getframe().f_code.co_name)
        if hostname is None or port is None:
            llogger.debug("Remote logger could not be started: %s:%s", hostname, port)
            return False
        self._remote_logger = remote_logger.RemoteLogger(hostname, port, self._swarm_uuid, self._uuid)
        self._remote_logger.debug("Remote logger for worker: %s registered on %s:%s",
                                  self._uuid, hostname, port)
        llogger.debug("Remote logger for worker: %s registered on %s:%s", self._uuid, hostname, port)
        return True

    def start_service(self, service_definition_as_json, swarm_network):
        """
            RPC method for starting a service in background on the worker
        :param service_definition_as_json: Service definition as JSON
        :param swarm_network: Network name
        :return: True when the service has been started successfully
        """
        llogger = local_logger.LocalLogger()
        llogger.log_method_call(self.__class__.__name__, sys._getframe().f_code.co_name)
        docker_interface_object = docker_interface.DockerInterface()
        llogger.debug("Run container: %s in background", service_definition_as_json)
        service_definition = jsonpickle.decode(service_definition_as_json)
        try:
            container = docker_interface_object.run_container_in_background(service_definition, self._remote_logger,
                                                                            swarm_network)
            container.service_definition = service_definition
            self._container_list.append(container)
            return True
        except DockerException as e:
            llogger.exception(e, "Error while starting service " + service_definition.tag)
            return False

    def join_docker_swarm(self, master_address, join_token):
        llogger = local_logger.LocalLogger()
        llogger.log_method_call(self.__class__.__name__, sys._getframe().f_code.co_name)
        docker_interface_object = docker_interface.DockerInterface()
        try:
            docker_interface_object.join_docker_swarm(master_address, self._interface, join_token)
        except DockerException:
            raise RuntimeError(traceback.format_exc())

    def stop_all_services(self):
        """
            Stops all containers of the current worker
        :return:
        """
        llogger = local_logger.LocalLogger()
        llogger.log_method_call(self.__class__.__name__, sys._getframe().f_code.co_name)
        self._container_list.stop_all_containers()

    def check_hardware(self, service_definition_as_json):
        """
            RPC method for checking the hardware capabilities of the worker for a specific service
        :param service_definition_as_json: Service definition as JSON
        :return: 1, when all hardware requirements have been met, otherwise 0
        """
        llogger = local_logger.LocalLogger()
        llogger.log_method_call(self.__class__.__name__, sys._getframe().f_code.co_name)
        service_definition = jsonpickle.decode(service_definition_as_json)
        docker_interface_object = docker_interface.DockerInterface()
        volume_vector = docker_interface_object.check_volumes(service_definition)
        llogger.debug("Vector of volume check: %s", volume_vector)
        device_vector = docker_interface_object.check_devices(service_definition)
        llogger.debug("Vector of device check: %s", device_vector)
        hardware_vector = volume_vector + device_vector
        llogger.debug("Vector of hardware check: %s", hardware_vector)
        if all(x == 1 for x in hardware_vector) or hardware_vector == []:
            return 1
        else:
            return 0

    def get_cpu_usage(self):
        """
            RPC method for returning the CPU usage of the worker
        :return: CPU usage of the worker
        """
        llogger = local_logger.LocalLogger()
        llogger.log_method_call(self.__class__.__name__, sys._getframe().f_code.co_name)
        return psutil.cpu_percent(interval=1)

    def get_vram_usage(self):
        """
            RPC method for returning the VRAM usage of the worker
        :return: VRAM usage of the worker
        """
        llogger = local_logger.LocalLogger()
        llogger.log_method_call(self.__class__.__name__, sys._getframe().f_code.co_name)
        mem = psutil.virtual_memory()
        return mem.percent

    def get_swap_ram_usage(self):
        """
            RPC method for returning the SWAP usage of the worker
        :return: SWAP usage of the worker
        """
        llogger = local_logger.LocalLogger()
        llogger.log_method_call(self.__class__.__name__, sys._getframe().f_code.co_name)
        mem = psutil.swap_memory()
        return mem.percent

    def get_bandwidth(self, repository):
        """
            RPC method for returning the network bandwidth of the worker
        :param repository: repository that should be used to get the network bandwidth
        :return: network bandwidth
        """
        llogger = local_logger.LocalLogger()
        llogger.log_method_call(self.__class__.__name__, sys._getframe().f_code.co_name)
        try:
            return network.check_network_bandwidth_of_repository(repository).get("download")
        except NetworkException:
            return 0

    def get_remaining_image_download_size(self, image_tag):
        """
            RPC method for checking if the service image is available on the worker
        :param image_tag: name of the image
        :return: size of image if it needs to be downloaded, otherwise 0
        """
        llogger = local_logger.LocalLogger()
        llogger.log_method_call(self.__class__.__name__, sys._getframe().f_code.co_name)
        img_size = 0
        try:
            docker_interface_object = docker_interface.DockerInterface()
            img_size = docker_interface_object.get_image_size(image_tag)
        except DockerException as e:
            llogger.exception(e, "Unable to get remaining image download size")
            pass
        if img_size < 0:
            return 0
        return img_size

    def get_info_as_json(self):
        """
            RPC method for returning the general info of the worker
        :return: WorkerInfo as json
        """
        llogger = local_logger.LocalLogger()
        llogger.log_method_call(self.__class__.__name__, sys._getframe().f_code.co_name)
        # Get logger for local logging
        llogger = local_logger.LocalLogger()
        # Log function call
        llogger.debug("Call: %s", sys._getframe().f_code.co_name)
        worker = WorkerInfo(uuid=self._uuid, hostname=self._hostname, advertise_address=self._advertise_address,
                            swarm_uuid=self._swarm_uuid)
        self._container_list.reload_containers()
        for container in self._container_list:
            worker.services.append(ServiceInfo(id=str(container.id), image=str(container.image.tags),
                                               name=str(container.service_definition.id),
                                               status=str(container.status)))
        return jsonpickle.encode(worker)


class WorkerInfo:
    """
    Worker representation containing only its data
    """
    def __init__(self, uuid, hostname, advertise_address=None, swarm_uuid=None):
        llogger = local_logger.LocalLogger()
        llogger.log_method_call(self.__class__.__name__, sys._getframe().f_code.co_name)
        self.uuid = uuid
        self.advertise_address = advertise_address
        self.hostname = hostname
        self.swarm_uuid = swarm_uuid
        self.services = []


class ServiceInfo:
    """
    Service representation containing only its data
    """
    def __init__(self, id, image=None, name=None, status=None):
        llogger = local_logger.LocalLogger()
        llogger.log_method_call(self.__class__.__name__, sys._getframe().f_code.co_name)
        self.id = id
        self.image = image
        self.name = name
        self.status = status
