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

from terminaltables import SingleTable

from ..logger import local_logger


class ServiceComposition:
    """
    Class that abstracts service compositions of the EDF
    """

    def __init__(self):
        """
        Initialization of a ServiceComposition object
        """
        llogger = local_logger.LocalLogger()
        llogger.log_method_call(self.__class__.__name__, sys._getframe().f_code.co_name)
        self._version = None
        self._services = dict()
        self._allocation = dict()

    def add_service(self, service_key, service_object):
        """
            Add service to service composition
        :param service_key: Key of the service
        :param service_object: Object of the service
        :return:
        """
        llogger = local_logger.LocalLogger()
        llogger.log_method_call(self.__class__.__name__, sys._getframe().f_code.co_name)
        if service_key is None or service_key == '' or service_object is None:
            return
        llogger.debug("Add service: %s", service_key)
        llogger.debug("\n" + service_object.format_service_definition_as_table())
        self._services.update({str(service_key): service_object})
        self._allocation.update({str(service_key): None})

    def assign_worker_to_service(self, service_key, worker_object):
        """
            Assign worker to service
        :param service_key: Key of the service
        :param worker_object: Object of the worker
        :return:
        """
        llogger = local_logger.LocalLogger()
        llogger.log_method_call(self.__class__.__name__, sys._getframe().f_code.co_name)
        if service_key not in self._allocation.keys() or worker_object is None:
            return
        self._allocation.update({str(service_key): str(worker_object.uuid)})
        llogger.debug("Worker: %s allocated to service %s", worker_object.uuid, service_key)

    def assign_worker_to_services(self, service_key_list, worker_object):
        """
            Assign worker to services
        :param service_key_list: List containing keys of services
        :param worker_object: Object of the worker
        :return:
        """
        llogger = local_logger.LocalLogger()
        llogger.log_method_call(self.__class__.__name__, sys._getframe().f_code.co_name)
        if type(service_key_list) is list:
            for service_key in service_key_list:
                self.assign_worker_to_service(service_key, worker_object)

    def get_open_allocations(self):
        """
            Returns the services that are not allocated yet
        :return: Open allocations of the service composition
        """
        llogger = local_logger.LocalLogger()
        llogger.log_method_call(self.__class__.__name__, sys._getframe().f_code.co_name)
        open_allocations = list()
        for service_key, worker_object in list(self._allocation.items()):
            if worker_object is None:
                open_allocations.append(service_key)
        return open_allocations

    def get_list_of_allocated_workers(self):
        """
            Returns a list of the workers that are already allocated
        :return:  List of workers that are already allocated
        """
        llogger = local_logger.LocalLogger()
        llogger.log_method_call(self.__class__.__name__, sys._getframe().f_code.co_name)
        allocated_worker_list = list()
        for _, worker in list(self._allocation.items()):
            if worker is not None:
                allocated_worker_list.append(worker)
        return allocated_worker_list

    def is_empty(self):
        """
            Returns true when service list is empty
        :return:
        """
        return self.get_service_count() == 0

    def get_service_count(self):
        """
            Returns the amount of registered services in this service composition
        :return: Integer
        """
        return len(list(self._allocation.items()))

    def get_worker_key(self, service_key):
        """
            Returns a worker key for the given service key
        :param service_key: key of the service
        :return: worker_key
        """
        return self._allocation.get(service_key)

    def get_service(self, service_key):
        """
            Returns the service with the given service key
        :param service_key: key of the service
        :return: Service
        """
        return self._services.get(service_key)

    def get_service_key_list(self):
        """
            Returns all registered service_keys in a list
        :return: list
        """
        return list(self._allocation.keys())

    def format_service_composition_as_table(self):
        """
            Returns a service composition definition formatted as a table
        :return: Updated service composition
        """
        llogger = local_logger.LocalLogger()
        llogger.log_method_call(self.__class__.__name__, sys._getframe().f_code.co_name)
        table_data = [['Version', 'Services']]
        service_object = list(self._services.items())
        table_data.append([str(self._version), ""])
        for _, service_val in service_object:
            table_data.append(["", str(service_val.id) + " - " + str(service_val.tag)])
        table = SingleTable(table_data)
        table.title = "Composition Definition"
        return table.table
