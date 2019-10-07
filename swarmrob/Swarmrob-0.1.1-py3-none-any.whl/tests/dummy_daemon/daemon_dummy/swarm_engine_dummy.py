#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys

from .logger import local_logger
from swarmrob.swarmengine import swarm
from .utils.errors import SwarmException
import jsonpickle


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


class SwarmEngine(object, metaclass=SingletonType):
    """
    The SwarmEngine is controlled by the SwarmRob daemon and encapsulates the management method of for the swarms
    """

    def __init__(self):
        """
            Initializing the swarm engine
        :return:
        """
        llogger = local_logger.LocalLogger()
        llogger.log_method_call(self.__class__.__name__, sys._getframe().f_code.co_name)
        self.swarm = None

    def create_new_swarm(self, new_master, predefined_uuid=None):
        """
            Factory method for creating a new swarm
        :param new_master: Object of the new master
        :param predefined_uuid: Predefined UUID of the swarm
        :return: Object of the new swarm
        """
        llogger = local_logger.LocalLogger()
        llogger.log_method_call(self.__class__.__name__, sys._getframe().f_code.co_name)
        self.swarm = swarm.Swarm(predefined_uuid, new_master)
        print(jsonpickle.encode(self.swarm))
        return self.swarm

    def register_worker_in_swarm(self, swarm_uuid, new_worker):
        """
            Register a new worker at the swarm
        :param swarm_uuid: The UUID of the swarm
        :param new_worker: Object of the new worker
        :return:
        """
        llogger = local_logger.LocalLogger()
        llogger.log_method_call(self.__class__.__name__, sys._getframe().f_code.co_name)
        llogger.debug("Add worker: " + str(new_worker) + " to swarm: " + swarm_uuid)
        self.swarm.add_worker_to_list(new_worker)

    def unregister_worker_in_swarm(self, swarm_uuid, worker_uuid):
        """
            Unregister worker at the swarm
        :param swarm_uuid: UUID of the swarm
        :param worker_uuid: UUID of the worker that should be removed
        :return:
        """
        llogger = local_logger.LocalLogger()
        llogger.log_method_call(self.__class__.__name__, sys._getframe().f_code.co_name)
        llogger.debug("Remove worker: " + str(worker_uuid) + " from swarm: " + swarm_uuid)
        self.swarm.remove_worker_from_list(worker_uuid)

    def start_swarm_by_composition(self, composition, swarm_uuid):
        """
            Start swarm by parsed service composition
        :param composition: Object of service composition
        :param swarm_uuid: UUID of the swarm
        :raises SwarmException
        """
        llogger = local_logger.LocalLogger()
        llogger.log_method_call(self.__class__.__name__, sys._getframe().f_code.co_name)
        if self.swarm is None:
            raise SwarmException("Swarm not initialized")
