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

import jsonpickle
from terminaltables import SingleTable

from ..logger import local_logger

WORKER_STATUS_TITLE = "Status of Worker"
WORKER_STATUS_LIST = "Worker Status List"
SWARM_LIST_TITLE = "List of master swarms"
SWARM_STATUS_TITLE = "Status of Swarm"
SERVICE_STATUS_LIST = "Service Status List"


def worker_daemon_status_to_table(worker_status):
    """
        Formats the worker status as a Table
    :param worker_status: Table of the worker status
    :return:
    """
    llogger = local_logger.LocalLogger()
    llogger.log_call(sys._getframe().f_code.co_name)
    table_data = [['UUID', 'Swarm UUID', 'Advertise Address']]
    for _, val in list(dict(worker_status).items()):
        table_data.append([str(val.uuid), str(val.swarm_uuid), str(val.advertise_address)])
    table = SingleTable(table_data)
    table.title = WORKER_STATUS_TITLE
    return table.table


def worker_status_to_table(worker_info):
    """
    Transforms the worker status into a user-friendly table.
    Example:
        >>> worker_status_to_table({TODO})
    Args:
        worker_info: The WorkerInfo object
    Returns:
        worker_status_stable (terminaltables.SingleTable): A worker status represented as a table
    """
    llogger = local_logger.LocalLogger()
    llogger.log_call(sys._getframe().f_code.co_name)

    table_data = [['UUID', 'Swarm UUID', 'AdvertiseAddress', 'Assigned Services', 'Running Services']]
    running_container_list = []
    for service in worker_info.services:
        if str(service.status) != 'exited':
            running_container_list.append(service)
    table_data.append([str(worker_info.uuid), str(worker_info.swarm_uuid), str(worker_info.advertise_address),
                       str(len(worker_info.services)), str(len(running_container_list))])

    swarm_status_table = SingleTable(table_data)
    swarm_status_table.title = WORKER_STATUS_TITLE
    return swarm_status_table.table


def swarm_status_to_worker_list(swarm_status):
    """
    Extracts the worker list of the swarm status and transforms it into a user-friendly list representation.
    Example:
        >>> swarm_status_to_worker_list({TODO})
    Args:
        swarm_status: Swarm status
    Returns:
        worker_list_as_string (string): List of workers
    """
    llogger = local_logger.LocalLogger()
    llogger.log_call(sys._getframe().f_code.co_name)
    worker_list = list(dict(swarm_status._worker_list).items())

    table_data = [['UUID', 'Hostname', 'AdvertiseAddress', 'Assigned Services', 'Running Services']]
    for worker_list_key, worker_list_val in worker_list:
        worker = jsonpickle.decode(worker_list_val.get_info_as_json())
        running_container_list = []
        for service in worker.services:
            if str(service.status) != 'exited':
                running_container_list.append(service)
        table_data.append([str(worker_list_key), str(worker.hostname), str(worker.advertise_address),
                           str(len(worker.services)), str(len(running_container_list))])
    table = SingleTable(table_data)
    table.title = WORKER_STATUS_LIST
    return table.table


def swarm_status_to_table(swarm_status):
    """
    Transforms the swarms status into a user-friendly table.
    Example:
        >>> swarm_status_to_table({TODO})
    Args:
        swarm_status: The swarm status
    Returns:
        swarm_status_stable (terminaltables.SingleTable): A swarm status represented as a table
    """
    llogger = local_logger.LocalLogger()
    llogger.log_call(sys._getframe().f_code.co_name)
    table_data = [['GUID', 'AdvertiseAddress', 'Number of Workers']]
    table_data.append([str(swarm_status._uuid), str(swarm_status._advertise_address),
                       str(len(swarm_status._worker_list))])

    swarm_status_table = SingleTable(table_data)
    swarm_status_table.title = SWARM_STATUS_TITLE
    return swarm_status_table.table


def service_list_to_table(worker_info):
    """
    Transforms the worker status into a user-friendly table.
    Example:
        >>> service_list_to_table({TODO})
    Args:
        worker_info: The workerInfo object
    Returns:
        services_status_stable (terminaltables.SingleTable): A services status represented as a table
    """
    llogger = local_logger.LocalLogger()
    llogger.log_call(sys._getframe().f_code.co_name)
    table_data = [['ID', 'Name', 'Image', 'Status']]

    for service in worker_info.services:
        table_data.append([str(service.id), str(service.name), str(service.image), str(service.status)])

    worker_status_table = SingleTable(table_data)
    worker_status_table.title = SERVICE_STATUS_LIST
    return worker_status_table.table
