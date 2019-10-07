#!/usr/bin/env python
# -*- coding: utf-8 -*-


import sys

import Pyro4
import jsonpickle
import socket
import uuid

from swarmrob.swarmengine.swarm_engine_worker import WorkerInfo

from .logger import local_logger
from .utils import network


@Pyro4.expose
@Pyro4.behavior(instance_mode="single")
class Worker:

    def __init__(self, swarm_uuid, interface, worker_uuid):
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
        if worker_uuid is None:
            self._uuid = uuid.uuid4().hex
        else:
            self._uuid = worker_uuid
        self._swarm_uuid = swarm_uuid
        self._remote_logger = None

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
        llogger.debug("Run container: %s in background", service_definition_as_json)
        return True

    def join_docker_swarm(self, master_address, join_token):
        llogger = local_logger.LocalLogger()
        llogger.log_method_call(self.__class__.__name__, sys._getframe().f_code.co_name)
        if join_token is None:
            raise RuntimeError()

    def stop_all_services(self):
        """
            Stops all containers of the current worker
        :return:
        """
        llogger = local_logger.LocalLogger()
        llogger.log_method_call(self.__class__.__name__, sys._getframe().f_code.co_name)

    def check_hardware(self, service_definition_as_json):
        """
            RPC method for checking the hardware capabilities of the worker for a specific service
        :param service_definition_as_json: Service definition as JSON
        :return: 1, when all hardware requirements have been met, otherwise 0
        """
        if service_definition_as_json is not None:
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
        return 0.5

    def get_vram_usage(self):
        """
            RPC method for returning the VRAM usage of the worker
        :return: VRAM usage of the worker
        """
        llogger = local_logger.LocalLogger()
        llogger.log_method_call(self.__class__.__name__, sys._getframe().f_code.co_name)
        return 0.5

    def get_swap_ram_usage(self):
        """
            RPC method for returning the SWAP usage of the worker
        :return: SWAP usage of the worker
        """
        llogger = local_logger.LocalLogger()
        llogger.log_method_call(self.__class__.__name__, sys._getframe().f_code.co_name)
        return 0.5

    def get_bandwidth(self, repository):
        """
            RPC method for returning the network bandwidth of the worker
        :param repository: repository that should be used to get the network bandwidth
        :return: network bandwidth
        """
        llogger = local_logger.LocalLogger()
        llogger.log_method_call(self.__class__.__name__, sys._getframe().f_code.co_name)
        return 1000

    def get_remaining_image_download_size(self, image_tag):
        """
            RPC method for checking if the service image is available on the worker
        :param image_tag: name of the image
        :return: size of image if it needs to be downloaded, otherwise 0
        """
        llogger = local_logger.LocalLogger()
        llogger.log_method_call(self.__class__.__name__, sys._getframe().f_code.co_name)
        return 100

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
        return jsonpickle.encode(worker)
