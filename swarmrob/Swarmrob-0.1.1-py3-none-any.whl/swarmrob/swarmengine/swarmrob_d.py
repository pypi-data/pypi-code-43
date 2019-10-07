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

import Pyro4
import Pyro4.errors
import jsonpickle

from ..logger import local_logger
from ..logger import evaluation_logger
from ..utils import network, pyro_interface
from ..utils.errors import DockerException, SwarmException, NetworkException
from . import mode
from . import swarm_engine
from . import swarm_engine_master
from . import swarm_engine_worker

SWARMROB_MASTER_IDENTIFIER = "swarmrob.master"


class SingletonType(type):
    """
    Helper class for singleton
    """
    def __call__(cls, *args, **kwargs):
        try:
            return cls.__instance
        except AttributeError:
            cls.__instance = super(SingletonType, cls).__call__(*args, **kwargs)
            return cls.__instance


@Pyro4.expose
class SwarmRobDaemon(object, metaclass=SingletonType):

    def __init__(self, interface, pyro_daemon):
        """
            Initialization method of the Swarmrob daemon
        :param interface: interface that is used by the SwarmRobDaemon
        :param pyro_daemon: pyro daemon that is used to communicate with the SwarmRobDaemon
        :return:
        """
        local_logger.LocalLogger().log_method_call(self.__class__.__name__, sys._getframe().f_code.co_name)
        self._daemon_running = True
        self._interface = interface
        self._master = None
        self._pyro_daemon = pyro_daemon
        self._swarm_engine = swarm_engine.SwarmEngine()
        self._swarm_list_of_worker = dict()
        
    def _close_pyro_daemon(self):
        """
            RPC method for closing the pyro daemon
        :return:
        """
        llogger = local_logger.LocalLogger()
        llogger.log_call(sys._getframe().f_code.co_name)
        if self._pyro_daemon is not None:
            self._pyro_daemon.close()

    def shutdown(self, host_ip):
        """
            RPC method for closing the pyro daemon
        :return:
        """
        llogger = local_logger.LocalLogger()
        llogger.log_method_call(self.__class__.__name__, sys._getframe().f_code.co_name)
        self._set_daemon_running(False)
        self._unregister_daemon_at_nameservice(host_ip)
        self._close_pyro_daemon()
        return os.getpid()

    def _unregister_daemon_at_nameservice(self, host_ip):
        """
            RPC method for unregistering the daemon at the nameservice
        :return:
        """
        llogger = local_logger.LocalLogger()
        llogger.log_method_call(self.__class__.__name__, sys._getframe().f_code.co_name)
        try:
            ns = Pyro4.locateNS(host_ip)
            ns.remove(pyro_interface.SWARMROBD_IDENTIFIER)
        except Pyro4.errors.NamingError:
            llogger.debug("Status Daemon: Daemon is not running (Pyro4 NamingError)")

    def is_daemon_running(self):
        """
            RPC method for returning if the daemon is currently running
        :return:
        """
        llogger = local_logger.LocalLogger()
        llogger.log_method_call(self.__class__.__name__, sys._getframe().f_code.co_name)
        return self._daemon_running

    def _set_daemon_running(self, daemon_running):
        """
            RPC method for setting if the daemon is currently running
        :param daemon_running:
        :return:
        """
        llogger = local_logger.LocalLogger()
        llogger.log_method_call(self.__class__.__name__, sys._getframe().f_code.co_name)
        self._daemon_running = daemon_running

    def create_new_swarm(self, advertise_address, interface, predefined_uuid=None):
        """
            RPC method for creating a new swarm
        :param advertise_address: Advertise address of the host
        :param interface: Interface of the host
        :param predefined_uuid: Predefined UUID of the new swarm
        :return: swarm object as json
        """
        llogger = local_logger.LocalLogger()
        llogger.log_method_call(self.__class__.__name__, sys._getframe().f_code.co_name)
        if self._master is not None:
            llogger.debug("Tried to initialize master twice. Aborting.")
            raise RuntimeError("Tried to initialize master twice. Aborting.")
        if advertise_address is None or interface is None:
            raise RuntimeError("Missing parameter")
        llogger.debug("Create new swarm on %s", advertise_address)
        host_ip = network.get_ip_of_interface(self._interface)
        pyro_nameservice = Pyro4.locateNS(host=host_ip, port=9090, broadcast=False)
        uri = self._pyro_daemon.register(swarm_engine_master.Master(interface, advertise_address))
        pyro_nameservice.register(SWARMROB_MASTER_IDENTIFIER, uri)
        self._master = Pyro4.Proxy(uri)
        self._master.start_remote_logging_server()
        try:
            return jsonpickle.encode(self._swarm_engine.create_new_swarm(self._master, predefined_uuid=predefined_uuid))
        except DockerException:
            raise RuntimeError(traceback.format_exc())

    def register_worker_at_local_daemon(self, new_worker):
        """
            Method for registering a new worker at the local daemon
        :param new_worker: Object of the new worker
        :return:
        """
        llogger = local_logger.LocalLogger()
        llogger.log_method_call(self.__class__.__name__, sys._getframe().f_code.co_name)
        if new_worker:
            self._swarm_list_of_worker.update({str(new_worker.swarm_uuid): new_worker})

    def unregister_worker_at_local_daemon(self, swarm_uuid):
        """
            Unregister the worker at the local daemon
        :param swarm_uuid: UUID of the swarm the worker was assigned to
        :return:
        """
        llogger = local_logger.LocalLogger()
        llogger.log_method_call(self.__class__.__name__, sys._getframe().f_code.co_name)
        if swarm_uuid in self._swarm_list_of_worker.keys():
            del self._swarm_list_of_worker[str(swarm_uuid)]

    def register_worker(self, swarm_uuid, nameservice_uri, worker_uuid):
        """
            Register the worker at the nameservice
        :param swarm_uuid: UUID of the swarm
        :param nameservice_uri: URI of the nameservice
        :param worker_uuid: UUID of the worker
        :return:
        """
        llogger = local_logger.LocalLogger()
        llogger.log_method_call(self.__class__.__name__, sys._getframe().f_code.co_name)
        llogger.debug("Try to register worker with interface: %s in swarm: %s at host: %s", self._interface,
                      swarm_uuid, nameservice_uri)
        if not swarm_uuid or not nameservice_uri:
            return False
        ns = Pyro4.locateNS(host=str(nameservice_uri))
        new_worker = swarm_engine_worker.Worker(swarm_uuid, self._interface, worker_uuid)
        uri = self._pyro_daemon.register(new_worker, objectId=new_worker.uuid)
        new_worker = Pyro4.Proxy(uri)
        ns.register(str(new_worker.uuid), uri)
        proxy = Pyro4.Proxy(ns.lookup(SWARMROB_MASTER_IDENTIFIER))
        swarm_info = jsonpickle.decode(
            proxy.register_worker_at_master(jsonpickle.encode(swarm_uuid), jsonpickle.encode(new_worker)))
        llogger.debug("SwarmInfo:" + str(jsonpickle.encode(swarm_info)))
        self.register_worker_at_local_daemon(new_worker)
        hostname, port = proxy.get_remote_logging_server_info()
        new_worker.start_remote_logger(hostname, port)
        return True

    def join_docker_swarm(self, worker_uuid, master_address, join_token):
        llogger = local_logger.LocalLogger()
        llogger.log_method_call(self.__class__.__name__, sys._getframe().f_code.co_name)
        worker = self._swarm_list_of_worker.get(worker_uuid)
        if worker is not None:
            try:
                worker.join_docker_swarm(master_address, join_token)
                return True
            except RuntimeError as e:
                llogger.exception(e, "Unable to join docker swarm")
                return False
        return False

    def unregister_worker(self, swarm_uuid, nameservice_uri, worker_uuid):
        """
            Unregister the worker at the nameservice
        :param swarm_uuid: UUID of the swarm
        :param nameservice_uri: URI of the nameservice
        :param worker_uuid: UUID of the worker
        :return: boolean, True when unregistered successful
        """
        llogger = local_logger.LocalLogger()
        llogger.log_method_call(self.__class__.__name__, sys._getframe().f_code.co_name)
        llogger.debug("Try to unregister worker with interface: %s in swarm: %s at host: %s", self._interface,
                      swarm_uuid, nameservice_uri)
        if not swarm_uuid or not nameservice_uri or not worker_uuid:
            return False
        try:
            if self._swarm_list_of_worker[swarm_uuid].uuid != worker_uuid:
                llogger.debug("Couldn't remove worker %s. Swarm %s doesn't have a worker with uuid %S on this machine.",
                              worker_uuid, swarm_uuid)
                return False
        except KeyError:
            llogger.debug("Couldn't remove worker %s. Swarm %s doesn't have a worker with uuid %S on this machine.",
                          worker_uuid, swarm_uuid)
            return False
        ns = Pyro4.locateNS(host=str(nameservice_uri))
        master_uri = ns.lookup(SWARMROB_MASTER_IDENTIFIER)
        master_proxy = Pyro4.Proxy(master_uri)
        result = master_proxy.unregister_worker_at_master(jsonpickle.encode(swarm_uuid), jsonpickle.encode(worker_uuid))
        if result:
            self._swarm_list_of_worker[swarm_uuid].stop_all_services()
            ns.remove(str(worker_uuid))
            self._pyro_daemon.unregister(worker_uuid)
            self.unregister_worker_at_local_daemon(swarm_uuid)
            llogger.debug("Successfully removed worker with uuid %s from swarm %s", worker_uuid, swarm_uuid)
            return True
        return False

    def get_mode(self):
        """
            Returns the mode of the node (master/worker)
        :return: Mode of the node
        """
        llogger = local_logger.LocalLogger()
        llogger.log_method_call(self.__class__.__name__, sys._getframe().f_code.co_name)
        if self._master is not None:
            return jsonpickle.encode(mode.Mode.MASTER)
        if len(self._swarm_list_of_worker) > 0:
            return jsonpickle.encode(mode.Mode.WORKER)
        return jsonpickle.encode(mode.Mode.NOT_DEFINED)

    def get_worker_status_as_json(self):
        """
            Returns the status of the workers as JSON
        :return: JSON of list of workers
        """
        llogger = local_logger.LocalLogger()
        llogger.log_method_call(self.__class__.__name__, sys._getframe().f_code.co_name)
        return jsonpickle.encode(self._swarm_list_of_worker)

    def start_swarm_by_composition(self, composition_as_json, swarm_uuid):
        """
            Start the services on the swarm based on a composition definition
        :param composition_as_json: Composition definition as JSON
        :param swarm_uuid: UUID of the swarm
        """
        llogger = local_logger.LocalLogger()
        llogger.log_method_call(self.__class__.__name__, sys._getframe().f_code.co_name)
        if composition_as_json is None or type(composition_as_json) != str:
            raise RuntimeError("service composition must be in json format")
        composition = jsonpickle.decode(composition_as_json)
        try:
            self._swarm_engine.start_swarm_by_composition(composition, swarm_uuid)
        except SwarmException as e:
            llogger.exception(e, "Unable to start swarm")
            raise RuntimeError(traceback.format_exc())

    def get_swarm_status_as_json(self):
        """
            Get the swarm status as JSON
        :return: swarm as json
        """
        llogger = local_logger.LocalLogger()
        llogger.log_method_call(self.__class__.__name__, sys._getframe().f_code.co_name)
        try:
            host_ip = network.get_ip_of_interface(self._interface)
            proxy = pyro_interface.get_proxy(SWARMROB_MASTER_IDENTIFIER, host_ip)
            return proxy.get_swarm_status_as_json()
        except NetworkException:
            return None

    def configure_evaluation_logger(self, log_folder=None, log_ident=None, enable=True):
        """
            Configures the evaluation logger by setting its log_folder, log_ident, enabling or disabling it and
            resetting its time
        :param log_folder: None or log folder path
        :param log_ident: identification string
        :param enable: True when the evaluation logger should be enabled
        :return:
        """
        llogger = local_logger.LocalLogger()
        llogger.log_method_call(self.__class__.__name__, sys._getframe().f_code.co_name)
        eval_logger = evaluation_logger.EvaluationLogger()
        if log_folder is not None:
            eval_logger.set_log_folder(log_folder)
        if log_ident is not None:
            eval_logger.set_log_ident(log_ident)
        self.reset_evaluation_logger()
        eval_logger.enable(enable)

    def reset_evaluation_logger(self):
        """
            Resets the time of the evaluation logger to let it use a new file
        :return:
        """
        llogger = local_logger.LocalLogger()
        llogger.log_method_call(self.__class__.__name__, sys._getframe().f_code.co_name)
        evaluation_logger.EvaluationLogger().reset_time()
