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

from ..logger import local_logger


class Swarm:
    """
    Class for abstracting a SwarmRob swarm
    """

    def __init__(self, swarm_uuid, master):
        """
            Initialization method of a swarm
        :param swarm_uuid:
        :param master:
        """
        llogger = local_logger.LocalLogger()
        llogger.log_method_call(self.__class__.__name__, sys._getframe().f_code.co_name)
        if swarm_uuid is None:
            self._uuid = uuid.uuid4().hex
        else:
            self._uuid = swarm_uuid
        self._worker_list = dict()
        self._master = master
        self._advertise_address = None
        if self._master is not None:
            self._master.swarm_uuid = self._uuid
            self._advertise_address = master.advertise_address

    @property
    def uuid(self):
        return self._uuid

    @property
    def advertise_address(self):
        return self._advertise_address

    @property
    def master(self):
        return self._master

    def add_worker_to_list(self, worker):
        """
            Add a worker to the swarm
        :param worker: worker that should be added to the swarm
        :return:
        """
        llogger = local_logger.LocalLogger()
        llogger.log_method_call(self.__class__.__name__, sys._getframe().f_code.co_name)
        if worker is None:
            return
        self._worker_list.update({str(worker.uuid): worker})

    def remove_worker_from_list(self, worker_uuid):
        """
            Remove a worker from the swarm
        :param worker_uuid: uuid of a worker that should be removed from the swarm
        :return:
        """
        llogger = local_logger.LocalLogger()
        llogger.log_method_call(self.__class__.__name__, sys._getframe().f_code.co_name)
        if worker_uuid is None:
            return False
        try:
            del self._worker_list[str(worker_uuid)]
            return True
        except KeyError:
            return False

    def get_worker(self, worker_uuid):
        """
            Returns the worker with the given uuid
        :param worker_uuid: uuid of the worker
        :return: Worker
        """
        llogger = local_logger.LocalLogger()
        llogger.log_method_call(self.__class__.__name__, sys._getframe().f_code.co_name)
        return self._worker_list.get(worker_uuid)

    def get_worker_count(self):
        """
            Returns the amount of workers that are registered in this swarm
        :return: int
        """
        llogger = local_logger.LocalLogger()
        llogger.log_method_call(self.__class__.__name__, sys._getframe().f_code.co_name)
        return len(self._worker_list)

    def get_worker_list(self):
        """
            Returns a list containing all worker registered in this swarm
        :return: list
        """
        return list(self._worker_list.items())

    def has_worker_with_name(self, name):
        """
            Checks if a worker with the given name is already registered
        :param name: name of the worker
        :return: True when a worker with that name has been found
        """
        llogger = local_logger.LocalLogger()
        llogger.log_method_call(self.__class__.__name__, sys._getframe().f_code.co_name)
        for _, worker in list(self._worker_list.items()):
            if worker.hostname == name:
                return True
        return False

    def get_unique_worker_hostname(self, name):
        """
            Generates a unique hostname, that can be assigned to a worker
        :return:
        """
        llogger = local_logger.LocalLogger()
        llogger.log_method_call(self.__class__.__name__, sys._getframe().f_code.co_name)
        if name != self._master.hostname and self.has_worker_with_name(name) is False:
            return name
        counter = 1
        unique_name = name + '_' + str(counter)
        while self.has_worker_with_name(unique_name) and unique_name != self._master.hostname:
            counter += 1
            unique_name = name + '_' + str(counter)
        return unique_name
