#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
import os

import jsonpickle
import Pyro4
import Pyro4.errors

from . import master_dummy, worker_dummy, swarm_engine_dummy
from .logger import local_logger
from .utils import network, process_helper, pyro_interface
from .utils.errors import NetworkException

PORT = 0
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
        self._interface = interface
        self._master = None
        self._pyro_daemon = pyro_daemon
        self._swarm_engine = swarm_engine_dummy.SwarmEngine()
        self._swarm_list_of_worker = dict()

    def reset_dummy(self):
        llogger = local_logger.LocalLogger()
        llogger.log_method_call(self.__class__.__name__, sys._getframe().f_code.co_name)
        llogger.debug("RESETTING DAEMON DUMMY")
        self._master = None
        self._swarm_engine.__init__()
        self._swarm_list_of_worker = dict()

        try:
            network_info = network.NetworkInfo("lo")
        except NetworkException:
            llogger.debug("Unable to access localhost network")
            return

        pyro_nameservice_object = pyro_interface.get_name_service(network_info.ip_address)
        dict_of_registered_objects = pyro_nameservice_object.list()
        for key_of_registered_objects, _ in list(dict_of_registered_objects.items()):
            if key_of_registered_objects != pyro_interface.SWARMROBD_IDENTIFIER:
                llogger.debug("Remove %s from nameserver", key_of_registered_objects)
                self._pyro_daemon.unregister(key_of_registered_objects)
                pyro_nameservice_object.remove(name=key_of_registered_objects)

    def get_pyro_daemon(self):
        llogger = local_logger.LocalLogger()
        llogger.log_method_call(self.__class__.__name__, sys._getframe().f_code.co_name)
        return jsonpickle.encode(self._pyro_daemon)

    def shutdown(self, host_ip):
        """
            RPC method for closing the pyro daemon
        :return:
        """
        llogger = local_logger.LocalLogger()
        llogger.log_method_call(self.__class__.__name__, sys._getframe().f_code.co_name)
        return os.getpid()

    def is_daemon_running(self):
        """
            RPC method for returning if the daemon is currently running
        :return:
        """
        llogger = local_logger.LocalLogger()
        llogger.log_method_call(self.__class__.__name__, sys._getframe().f_code.co_name)
        return True

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
        llogger.debug("Create new swarm on %s", advertise_address)
        host_ip = network.get_ip_of_interface(self._interface)
        pyro_nameservice = Pyro4.locateNS(host=host_ip, port=9090, broadcast=False)
        uri = self._pyro_daemon.register(master_dummy.Master(interface, advertise_address))
        pyro_nameservice.register(SWARMROB_MASTER_IDENTIFIER, uri)
        self._master = Pyro4.Proxy(uri)
        self._master.start_remote_logging_server()
        return jsonpickle.encode(self._swarm_engine.create_new_swarm(self._master, predefined_uuid=predefined_uuid))

    def register_worker_at_local_daemon(self, new_worker):
        """
            Method for registering a new worker at the local daemon
        :param new_worker: Object of the new worker
        :return:
        """
        llogger = local_logger.LocalLogger()
        llogger.log_method_call(self.__class__.__name__, sys._getframe().f_code.co_name)
        self._swarm_list_of_worker.update({str(new_worker.swarm_uuid): new_worker})

    def unregister_worker_at_local_daemon(self, swarm_uuid):
        """
            Unregister the worker at the local daemon
        :param swarm_uuid: UUID of the swarm the worker was assigned to
        :return:
        """
        llogger = local_logger.LocalLogger()
        llogger.log_method_call(self.__class__.__name__, sys._getframe().f_code.co_name)
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
        try:
            ns = Pyro4.locateNS(host=str(nameservice_uri))
            proxy = Pyro4.Proxy(ns.lookup(SWARMROB_MASTER_IDENTIFIER))
            new_worker = worker_dummy.Worker(swarm_uuid, self._interface, worker_uuid)
            uri = self._pyro_daemon.register(new_worker, objectId=new_worker.uuid)
            new_worker = Pyro4.Proxy(uri)
            ns.register(str(new_worker.uuid), uri)
            swarm_info = jsonpickle.decode(
                proxy.register_worker_at_master(jsonpickle.encode(swarm_uuid), jsonpickle.encode(new_worker)))
            llogger.debug("SwarmInfo:" + jsonpickle.encode(swarm_info))
            self.register_worker_at_local_daemon(new_worker)
            hostname, port = proxy.get_remote_logging_server_info()
            new_worker.start_remote_logger(hostname, port)
        except Pyro4.errors.NamingError as e:
            raise RuntimeError(e)

    def join_docker_swarm(self, worker_uuid, master_address, join_token):
        llogger = local_logger.LocalLogger()
        llogger.log_method_call(self.__class__.__name__, sys._getframe().f_code.co_name)
        return True

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
        try:
            if self._swarm_list_of_worker[swarm_uuid].uuid != worker_uuid:
                llogger.debug("Couldn't remove worker %s. Swarm %s doesn't have a worker with uuid %S on this machine.",
                              worker_uuid, swarm_uuid)
                return False
        except KeyError:
            llogger.debug("Couldn't remove worker %s. Swarm %s doesn't have a worker with uuid %S on this machine.",
                          worker_uuid, swarm_uuid)
            return False
        llogger.debug("Successfully removed worker with uuid %s from swarm %s", worker_uuid, swarm_uuid)
        return True

    def get_mode(self):
        """
            Returns the mode of the node (master/worker)
        :return: Mode of the node
        """
        llogger = local_logger.LocalLogger()
        llogger.log_method_call(self.__class__.__name__, sys._getframe().f_code.co_name)
        if self._master is True:
            return '{"py/reduce": [{"py/type": "swarmrob.swarmengine.mode.Mode"}, ' \
                   '{"py/tuple": ["MASTER"]}, null, null, null]}'
        if len(self._swarm_list_of_worker) > 0:
            return '{"py/reduce": [{"py/type": "swarmrob.swarmengine.mode.Mode"}, ' \
                   '{"py/tuple": ["WORKER"]}, null, null, null]}'
        return '{"py/reduce": [{"py/type": "swarmrob.swarmengine.mode.Mode"}, ' \
               '{"py/tuple": ["NONE"]}, null, null, null]}'

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
        if self._master is None:
            raise RuntimeError("Swarm not initialized")
        if type(composition_as_json) != str or swarm_uuid is None or self._master is None:
            raise RuntimeError()

    def get_swarm_status_as_json(self):
        """
            Get the swarm status as JSON
        :return: swarm as json
        """
        llogger = local_logger.LocalLogger()
        llogger.log_method_call(self.__class__.__name__, sys._getframe().f_code.co_name)
        try:
            host_ip = network.get_ip_of_interface(self._interface)
            ns = Pyro4.locateNS(host=str(host_ip))
            master_uri = ns.lookup(SWARMROB_MASTER_IDENTIFIER)
            proxy = Pyro4.Proxy(master_uri)
            return proxy.get_swarm_status_as_json()
        except (NetworkException, Pyro4.errors.NamingError):
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

    def reset_evaluation_logger(self):
        """
            Resets the time of the evaluation logger to let it use a new file
        :return:
        """
        llogger = local_logger.LocalLogger()
        llogger.log_method_call(self.__class__.__name__, sys._getframe().f_code.co_name)


def main():
    process_helper.create_daemon()
    llogger = local_logger.LocalLogger()
    llogger.log_call(sys._getframe().f_code.co_name)
    llogger.enable = True

    try:
        network_info = network.NetworkInfo("lo")
    except NetworkException:
        llogger.debug("Unable to access localhost network")
        return
    pyro_nameservice_object = pyro_interface.get_name_service(network_info.ip_address, start=True)
    pyro_interface.clear_name_service(pyro_nameservice_object)
    with Pyro4.Daemon(host=network_info.ip_address, port=PORT) as pyro_daemon:
        daemon_uri = pyro_daemon.register(SwarmRobDaemon(network_info.interface, pyro_daemon))
        pyro_nameservice_object.register(pyro_interface.SWARMROBD_IDENTIFIER, daemon_uri)
        llogger.debug("Daemon started. Object URI = %s", daemon_uri)
        pyro_daemon.requestLoop(SwarmRobDaemon().is_daemon_running)
    sys.exit(0)


if __name__ == "__main__":
    main()
