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

from terminaltables import SingleTable

from ..logger import local_logger


class Service:
    """
    Class that abstracts a service of the EDF
    """

    def __init__(self, id=None, tag=None):
        """
        Initialization of a Service object
        """
        llogger = local_logger.LocalLogger()
        llogger.log_method_call(self.__class__.__name__, sys._getframe().f_code.co_name)
        self._id = id
        self._tag = tag
        self._environment = dict()
        self._deploy = dict()
        self._dependsOn = set()
        self._volumes = dict()
        self._devices = list()

    def __str__(self):
        return self._id

    def add_env(self, env_key, env_value):
        """
            Add a key/value pair of an environment variable to the service
        :param env_key: Key of the environment variable
        :param env_value: Value of the environment variable
        :return:
        """

        llogger = local_logger.LocalLogger()
        llogger.log_method_call(self.__class__.__name__, sys._getframe().f_code.co_name)
        if env_key is None or env_value is None or env_key == '' or env_value == '':
            return
        self._environment.update({os.path.expandvars(str(env_key)): os.path.expandvars(str(env_value))})

    def add_deployment(self, deployment_key, deployment_value):
        """
            Add a deployment configuration to the service
        :param deployment_key: Key of the deployment configuration
        :param deployment_value: Value of the deployment configuration
        :return:
        """
        llogger = local_logger.LocalLogger()
        llogger.log_method_call(self.__class__.__name__, sys._getframe().f_code.co_name)
        if deployment_key is None or deployment_value is None or deployment_key == '' or deployment_value == '':
            return
        self._deploy.update({os.path.expandvars(str(deployment_key)): os.path.expandvars(str(deployment_value))})

    def add_dependency(self, dependency_value):
        """
            Add a service dependency to the service
        :param dependency_value: Value of the dependency
        :return:
        """
        llogger = local_logger.LocalLogger()
        llogger.log_method_call(self.__class__.__name__, sys._getframe().f_code.co_name)
        if dependency_value is None or dependency_value == '':
            return
        self._dependsOn.add(str(dependency_value))

    def add_volume(self, volume_source, volume_dest, mode='rw'):
        """
            Add a volume to the service (e.g. /home/host/test:/home/container/test)
        :param volume_source: Source of the volume on the host system
        :param volume_dest: Destination of the volume on the virtualized system
        :param mode: Access permissions of the volume (Default: rw)
        :return:
        """
        llogger = local_logger.LocalLogger()
        llogger.log_method_call(self.__class__.__name__, sys._getframe().f_code.co_name)
        if volume_source is None or volume_dest is None or volume_source == '' or volume_dest == ''\
                or mode is None or mode is '':
            return
        self._volumes.update({os.path.expandvars(str(volume_source)): dict(
            {'bind': os.path.expandvars(str(volume_dest)), 'mode': mode})})

    def add_device(self, device_source, device_dest, mode='rwm'):
        """
            Add a device to the service (e.g. /dev/usb1:/dev/usb1)
        :param device_source: Source of the device on the host system
        :param device_dest: Destination of the device on the virtualized system
        :param mode: Access permissions of the device (Default: rwm)
        :return:
        """
        llogger = local_logger.LocalLogger()
        llogger.log_method_call(self.__class__.__name__, sys._getframe().f_code.co_name)
        if device_source is None or device_dest is None or device_source == '' or device_dest == ''\
                or mode is None or mode is '':
            return
        for i in range(len(self._devices)):
            device = self._devices[i].split(":")
            if device[0] == device_source or device[1] == device_dest:
                self._devices[i] = os.path.expandvars(str(device_source) + ":" + str(device_dest) + ":" + str(mode))
                return
        self._devices.append(os.path.expandvars(str(device_source) + ":" + str(device_dest) + ":" + str(mode)))

    @property
    def id(self):
        return self._id

    @property
    def tag(self):
        return self._tag

    def are_dependencies_started(self, started_services):
        """
            Checks if all required dependencies have been started
        :param started_services: list of key of started services
        :return:
        """
        if started_services is None:
            if len(self._dependsOn) == 0:
                return True
            return False
        for dependency in self._dependsOn:
            if dependency not in started_services:
                return False
        return True

    def format_service_definition_as_table(self):
        """
            Format service definition as table
        :return: Service definition as table object
        """
        llogger = local_logger.LocalLogger()
        llogger.log_method_call(self.__class__.__name__, sys._getframe().f_code.co_name)
        table_data = [['Type', 'Value']]
        table_data.append(['ID', self._id])
        table_data.append(['Tag', self._tag])
        table_data.append(['', ''])
        table_data = self.add_env_to_table(table_data)
        table_data = self.add_volumes_to_table(table_data)
        table_data = self.add_devices_to_table(table_data)
        table_data = self.add_dependencies_to_table(table_data)
        table = SingleTable(table_data)
        table.title = "Service Definition"
        return table.table

    def add_env_to_table(self, table_data):
        """
            Format environment variables and add them to a parent table
        :param table_data: Table data of the parent table
        :return: Service definition as table object
        """
        llogger = local_logger.LocalLogger()
        llogger.log_method_call(self.__class__.__name__, sys._getframe().f_code.co_name)
        environments = self._environment
        table_data.append(["Environment", "$KEY=$VALUE"])
        if len(list(environments.items())) == 0:
            table_data.append(["", "No environment variables specified"])
        for key, val in list(environments.items()):
            table_data.append(["", "-" + str(key) + "=" + str(val)])
        return table_data

    def add_volumes_to_table(self, table_data):
        """
            Format volumes and add them to a parent table
        :param table_data: Table data of the parent table
        :return: Service definition as table object
        """
        llogger = local_logger.LocalLogger()
        llogger.log_method_call(self.__class__.__name__, sys._getframe().f_code.co_name)
        volumes = self._volumes
        table_data.append(["Volumes", "$SOURCE:$DESTINATION:$MODE"])
        if len(list(volumes.items())) == 0:
            table_data.append(["", "No volumes specified"])
        for key, val in list(volumes.items()):
            table_data.append(["", "-" + str(key) + ":" + str(val["bind"]) + ":" + str(val["mode"])])
        return table_data

    def add_devices_to_table(self, table_data):
        """
            Format devices and add them to a parent table
        :param table_data:  Table data of the parent table
        :return: Service definition as table object
        """
        llogger = local_logger.LocalLogger()
        llogger.log_method_call(self.__class__.__name__, sys._getframe().f_code.co_name)
        devices = self._devices
        table_data.append(["Devices", "$SOURCE:$DESTINATION:$MODE"])
        if len(devices) == 0:
            table_data.append(["", "No devices specified"])
        for device in devices:
            table_data.append(["", "-" + device])
        return table_data

    def add_dependencies_to_table(self, table_data):
        """
            Format dependencies and add them to a parent table
        :param table_data: Table data of the parent table
        :return: Service definition as table object
        """
        llogger = local_logger.LocalLogger()
        llogger.log_method_call(self.__class__.__name__, sys._getframe().f_code.co_name)
        depends_on = self._dependsOn
        table_data.append(["DependsOn", "$SERVICE"])
        if len(depends_on) == 0:
            table_data.append(["", "No dependencies specified"])
        for dependency in depends_on:
            table_data.append(["", "-" + dependency])
        return table_data
