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

from ..logger import local_logger


class DockerContainerList(list):
    """
    DockerContainerList manages all containers run by the current worker and swarm
    """
    def __init__(self, *args):
        """
            Initialises parent class
        :param *args: list initialization params
        """
        llogger = local_logger.LocalLogger()
        llogger.log_method_call(self.__class__.__name__, sys._getframe().f_code.co_name)
        list.__init__(self, *args)

    def get_running_containers(self):
        """
            Creates a list of all running containers run by the worker and returns it
        :return: List of all running containers
        """
        llogger = local_logger.LocalLogger()
        llogger.log_method_call(self.__class__.__name__, sys._getframe().f_code.co_name)
        self.reload_containers()
        container_list = []
        for container in self:
            if str(container.status) != 'exited':
                container_list.append(container)
        return container_list

    def reload_containers(self):
        """
            Reloads the information about all containers inside this list
        :return:
        """
        llogger = local_logger.LocalLogger()
        llogger.log_method_call(self.__class__.__name__, sys._getframe().f_code.co_name)
        for container in self:
            container.reload()

    def stop_all_containers(self):
        """
            Stops all containers run by the current worker and swarm
        :return:
        """
        llogger = local_logger.LocalLogger()
        llogger.log_method_call(self.__class__.__name__, sys._getframe().f_code.co_name)
        containers = self.get_running_containers()
        for container in containers:
            container.kill()
        return len(containers)
