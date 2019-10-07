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

import queue
import datetime
import sys
import threading
import time
from collections import deque

import jsonpickle

from ..dockerengine import docker_interface
from ..logger import evaluation_logger
from ..logger import local_logger
from ..utils.errors import SwarmException
from . import swarm

WORKER_PORT = 0


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
        if new_master is None:
            return None
        docker_interface_object = docker_interface.DockerInterface()
        docker_interface_object.init_docker_swarm(new_master.interface)
        self.swarm = swarm.Swarm(predefined_uuid, new_master)
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
        if not new_worker or not swarm_uuid:
            return
        llogger.debug("Add worker: " + str(new_worker) + " to swarm: " + str(swarm_uuid))
        self.swarm.add_worker_to_list(new_worker)
        dio = docker_interface.DockerInterface()
        if new_worker.advertise_address != self.swarm.master.advertise_address:
            new_worker.join_docker_swarm(self.swarm.advertise_address, dio.get_join_token())

    def unregister_worker_in_swarm(self, swarm_uuid, worker_uuid):
        """
            Unregister worker at the swarm
        :param swarm_uuid: UUID of the swarm
        :param worker_uuid: UUID of the worker that should be removed
        :return:
        """
        llogger = local_logger.LocalLogger()
        llogger.log_method_call(self.__class__.__name__, sys._getframe().f_code.co_name)
        if not worker_uuid or not swarm_uuid:
            return
        llogger.debug("Remove worker: " + str(worker_uuid) + " from swarm: " + str(swarm_uuid))
        return self.swarm.remove_worker_from_list(worker_uuid)

    def start_swarm_by_composition(self, composition, swarm_uuid):
        """
            Start swarm by parsed service composition
        :param composition: Object of service composition
        :param swarm_uuid: UUID of the swarm
        :raises SwarmException
        """
        llogger = local_logger.LocalLogger()
        llogger.log_method_call(self.__class__.__name__, sys._getframe().f_code.co_name)
        start_timer = datetime.datetime.now()
        if composition is None or swarm_uuid is None:
            raise SwarmException("Start swarm parameters are None")
        if self.swarm is None:
            raise SwarmException("Swarm not initialized")
        llogger.debug("Try to match swarm: %s with the following composition", str(swarm_uuid))
        llogger.debug("\n" + composition.format_service_composition_as_table())
        result = self._assign_services_to_workers(composition)
        if result is True:
            llogger.debug("Worker matched. Try to start network")
            network = self._create_docker_network()
            llogger.debug(composition._allocation)
            self._start_services_on_workers(composition, network)
            total_time_of_run = datetime.datetime.now() - start_timer
            evaluation_logger.EvaluationLogger().write(["Total Time of Run", "*", "*",
                                                        total_time_of_run.total_seconds(),
                                                        self.swarm.get_worker_count(),
                                                        len(composition.get_open_allocations())],
                                                       evaluation_logger.LogType.ALLOC_METRICS)
            llogger.debug("Time elapsed for Total Run: %f", total_time_of_run.total_seconds())
            return True
        return False

    def _start_services_on_workers(self, composition, network):
        """
            Start the services on the allocated workers
        :param composition: Object of service composition
        :param network: docker network
        :raises SwarmException
        """
        llogger = local_logger.LocalLogger()
        llogger.log_method_call(self.__class__.__name__, sys._getframe().f_code.co_name)
        if not self.swarm or not composition or not network or self.swarm.get_worker_count() <= 0:
            raise SwarmException("Preconditions for starting services not met")
        start_timer = datetime.datetime.now()
        service_key_queue = deque(list(composition._allocation.keys()))
        started_services = []
        while len(service_key_queue) > 0:
            # TODO: DIRTY FIX: waiting 1 sec to make sure docker has cleaned up before starting next service
            #                  because of a docker daemon bug not finding the network when starting two services
            #                  at the same time on the same worker
            time.sleep(1)
            service_key = service_key_queue.popleft()
            worker_key = composition.get_worker_key(service_key)
            service = composition.get_service(service_key)
            if service.are_dependencies_started(started_services):
                worker = self.swarm.get_worker(worker_key)
                if worker is None:
                    llogger.debug("Error worker not found for worker key %s", str(worker_key))
                    raise SwarmException("Worker not found for worker key " + str(worker_key))
                elif worker.start_service(jsonpickle.encode(service), network) is False:
                    llogger.debug("Error starting service %s on worker %s", service.tag, worker.uuid)
                    raise SwarmException("Failed to start service " + service.tag + " on worker " + worker.uuid)
                started_services.append(service_key)
                llogger.debug("Started service " + service_key + " on worker " + worker_key)
            else:
                service_key_queue.append(service_key)
        elapsed_time_until_service_start = datetime.datetime.now() - start_timer
        evaluation_logger.EvaluationLogger().write(["Time for starting containers", "*", "*",
                                                    elapsed_time_until_service_start.total_seconds(),
                                                    self.swarm.get_worker_count(),
                                                    composition.get_service_count()],
                                                   evaluation_logger.LogType.ALLOC_METRICS)
        llogger.debug("Time elapsed for starting containers: %f", elapsed_time_until_service_start.total_seconds())

    def _create_docker_network(self):
        """
            Create a new Docker network
        :return: List of Networks
        """
        llogger = local_logger.LocalLogger()
        llogger.log_method_call(self.__class__.__name__, sys._getframe().f_code.co_name)
        if self.swarm is None:
            return None
        docker_interface_object = docker_interface.DockerInterface()
        network = docker_interface_object.create_network(network_name=self.swarm.uuid)
        llogger.debug("Network created: %s", jsonpickle.encode(network.attrs))
        return network.attrs.get("Name")

    def _assign_services_to_workers(self, composition):
        """
            Assign the composition of services to the swarm workers
        :param composition: Service composition
        :return: bool
        """
        llogger = local_logger.LocalLogger()
        llogger.log_method_call(self.__class__.__name__, sys._getframe().f_code.co_name)
        if not composition or not self.swarm:
            return False
        open_allocations = composition.get_open_allocations()
        llogger.debug("Open service allocations: %s", len(open_allocations))
        service_allocation_dict = self._allocate_services_to_workers(composition, open_allocations)
        if service_allocation_dict is not None:
            for worker, service_list in list(service_allocation_dict.items()):
                composition.assign_worker_to_services(service_list, worker)
                for service in service_list:
                    evaluation_logger.EvaluationLogger().write([service, worker.hostname],
                                                               evaluation_logger.LogType.ALLOCATIONS)
            llogger.debug(composition._allocation)
            return True
        else:
            llogger.debug(composition._allocation)
            return False

    def _allocate_services_to_workers(self, composition, allocations):
        llogger = local_logger.LocalLogger()
        llogger.log_method_call(self.__class__.__name__, sys._getframe().f_code.co_name)
        if not composition or not allocations or not self.swarm:
            return None
        from ..service_allocation import ortools_interface
        hardware_matrix, cost_matrix = self._get_cost_and_hardware_matrix(composition, allocations)
        start_timer = datetime.datetime.now()
        service_allocation_dict = ortools_interface.allocate_services_to_workers(
            services=allocations,
            workers=self.swarm._worker_list,
            hardware_matrix=hardware_matrix,
            cost_matrix=cost_matrix)
        time_of_allocation = datetime.datetime.now() - start_timer
        evaluation_logger.EvaluationLogger().write(["Time of service_allocation", "*", "*",
                                                    time_of_allocation.total_seconds(),
                                                    self.swarm.get_worker_count(), len(allocations)],
                                                   evaluation_logger.LogType.ALLOC_METRICS)
        return service_allocation_dict

    def _get_cost_and_hardware_matrix(self, composition, allocations):
        llogger = local_logger.LocalLogger()
        llogger.log_method_call(self.__class__.__name__, sys._getframe().f_code.co_name)
        if not composition or not allocations or not self.swarm:
            return None, None
        hardware_matrix = []
        cost_matrix = []
        start_timer = datetime.datetime.now()
        for service_key in allocations:
            service = composition.get_service(service_key)
            if not service:
                hardware_row_for_service, cost_row_for_service = self._get_cost_and_hardware_row_for_service(service)
                hardware_matrix.append(hardware_row_for_service)
                cost_matrix.append(cost_row_for_service)
        time_of_calculation = datetime.datetime.now() - start_timer
        evaluation_logger.EvaluationLogger().write(["Time of cost calculation", "*", "*",
                                                    time_of_calculation.total_seconds(), self.swarm.get_worker_count(),
                                                    len(allocations)], evaluation_logger.LogType.ALLOC_METRICS)
        llogger.debug("Time elapsed for cost calculation: %f", time_of_calculation.total_seconds())
        return hardware_matrix, cost_matrix

    def _get_cost_and_hardware_row_for_service(self, service):
        llogger = local_logger.LocalLogger()
        llogger.log_method_call(self.__class__.__name__, sys._getframe().f_code.co_name)
        if not service or not self.swarm:
            return None, None
        from ..service_allocation import cost_calculation
        hardware_row_for_service = []
        cost_row_for_service = []
        column_id = 0
        thread_queue = queue.Queue()
        thread_pool = list()
        thread_results = dict()
        cost_calculation_object = cost_calculation.CostCalculation()
        for _, worker_value in self.swarm.get_worker_list():
            thread_ = threading.Thread(target=cost_calculation_object.calculate_costs_and_check_hardware_in_thread,
                                       name=column_id,
                                       args=[column_id, service, worker_value, thread_queue])
            column_id = column_id + 1
            thread_pool.append(thread_)

        # Start all threads in thread pool
        for thread in thread_pool:
            thread.start()
        # Kill all threads
        for thread in thread_pool:
            thread.join()

        while not thread_queue.empty():
            thread_response = thread_queue.get()
            thread_results.update({list(thread_response.keys())[0]: thread_response})

        llogger.debug(thread_results)
        for i in range(0, column_id):
            thread_result = thread_results.get(i)
            if thread_result is not None:
                hardware_row_for_service.append(thread_result.get(i).get("hw"))
                cost_row_for_service.append(thread_result.get(i).get("cost"))
        return hardware_row_for_service, cost_row_for_service
