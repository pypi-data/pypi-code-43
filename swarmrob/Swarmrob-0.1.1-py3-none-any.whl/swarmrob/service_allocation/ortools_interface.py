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

from __future__ import division

import sys

import numpy

from ..logger import local_logger


def allocate_services_to_workers(services=None, workers=None, hardware_matrix=None, cost_matrix=None,
                                 capacity_matrix=None):
    """
        Allocate services to workers using the push-relabel algorithm specified URL
    :param services: Services that should be allocated
    :param workers: Workers that should carry out the services
    :param hardware_matrix: Binary matrix where each entry specifies if a service i can be executed on a worker j
    :param cost_matrix: Matrix where each entry describes the cost for running a service i on a specific worker j
    :param capacity_matrix: Matrix where each entry describes the capacity of a worker
    :return:
    """
    llogger = local_logger.LocalLogger()
    llogger.log_call(sys._getframe().f_code.co_name)
    if workers is None or services is None or len(services) == 0:
        return None
    if len(workers) > 1:
        return _allocate_dynamic(services, workers, hardware_matrix, cost_matrix, capacity_matrix)
    elif len(workers) == 1:
        return _allocate_static(services, workers)
    else:
        llogger.debug("No workers available. So no service could be assigned to a worker")
        return None


def _allocate_static(services, workers):
    llogger = local_logger.LocalLogger()
    llogger.log_call(sys._getframe().f_code.co_name)
    if len(workers) != 1:
        return None
    service_allocation_dict = dict()
    llogger.debug("Only one worker available. Allocation mode = static")
    service_list = list()
    for z in range(len(services)):
        service_list.append(services[z])
        llogger.debug('Worker %s assigned to service %s.', list(workers.values())[0], services[z])
    service_allocation_dict.update({list(workers.values())[0]: service_list})
    return service_allocation_dict


def _allocate_dynamic(services, workers, hardware_matrix, cost_matrix, capacity_matrix):
    llogger = local_logger.LocalLogger()
    llogger.log_call(sys._getframe().f_code.co_name)
    if len(workers) < 1:
        return None
    if not _are_matrices_valid(len(services), len(workers), hardware_matrix, cost_matrix, capacity_matrix):
        llogger.error("Invalid matrices")
        return None
    if capacity_matrix is None:
        capacity_matrix = numpy.ones((len(services), len(workers)), dtype=numpy.int).tolist()
    start_nodes, end_nodes, capacities, costs, supply = _get_min_cost_flow_params(len(workers), len(services),
                                                                                  hardware_matrix, cost_matrix,
                                                                                  capacity_matrix)
    min_cost_flow = _create_simple_min_flow_cost(start_nodes, end_nodes, capacities, costs, supply)
    return _solve_using_min_flow_cost(min_cost_flow, services, workers)


def _are_matrices_valid(service_count, worker_count, hardware_matrix, cost_matrix, capacity_matrix):
    if hardware_matrix is None or cost_matrix is None:
        return False
    if len(hardware_matrix) != service_count or len(cost_matrix) != service_count:
        return False
    for i in range(len(hardware_matrix)):
        if len(hardware_matrix[i]) != worker_count or len(cost_matrix[i]) != worker_count:
            return False
    if capacity_matrix is not None:
        if len(capacity_matrix) != service_count:
            return False
        for i in range(len(capacity_matrix)):
            if len(capacity_matrix[i]) != worker_count:
                return False
    return True


def _get_min_cost_flow_params(worker_count, service_count, hardware_matrix, cost_matrix, capacity_matrix):
    llogger = local_logger.LocalLogger()
    llogger.log_call(sys._getframe().f_code.co_name)

    llogger.debug("Matrix of Hardware:\n %s", numpy.asarray(hardware_matrix))
    llogger.debug("Matrix of Costs:\n %s", numpy.asarray(cost_matrix))
    llogger.debug("Matrix of Capacity:\n %s", numpy.asarray(capacity_matrix))

    supply = _generate_supply(worker_count, service_count)
    wc, sn_arcs_out_of_source, en_arcs_out_of_source, cap_arcs_out_of_source, costs_arcs_out_of_source\
        = _generate_source_worker_arcs(worker_count)
    sn_arcs_leading_into_sink, en_arcs_leading_into_sink, cap_arcs_leading_into_sink, costs_arcs_leading_into_sink\
        = _generate_service_sink_arcs(wc, worker_count, service_count)
    sn_arcs_between_worker_and_service, en_arcs_between_worker_and_service, costs_arcs_between_worker_and_service,\
        cap_arcs_between_worker_and_service = _generate_worker_service_arcs(worker_count, hardware_matrix, cost_matrix,
                                                                            capacity_matrix)

    start_nodes = _combine_to_list(sn_arcs_out_of_source, sn_arcs_between_worker_and_service, sn_arcs_leading_into_sink)
    end_nodes = _combine_to_list(en_arcs_out_of_source, en_arcs_between_worker_and_service, en_arcs_leading_into_sink)
    capacities = _combine_to_list(cap_arcs_out_of_source, cap_arcs_between_worker_and_service,
                                  cap_arcs_leading_into_sink)
    costs = _combine_to_list(costs_arcs_out_of_source, costs_arcs_between_worker_and_service,
                             costs_arcs_leading_into_sink)

    llogger.debug("Start nodes: %s", start_nodes)
    llogger.debug("End nodes: %s", end_nodes)
    llogger.debug("Capacities: %s", capacities)
    llogger.debug("Costs: %s", costs)
    llogger.debug("Supplies: %s", supply)
    return start_nodes, end_nodes, capacities, costs, supply


def _generate_source_worker_arcs(worker_count):
    llogger = local_logger.LocalLogger()
    llogger.log_call(sys._getframe().f_code.co_name)
    sn_arcs_out_of_source = [0]
    en_arcs_out_of_source = [1]
    cap_arcs_out_of_source = [1]
    costs_arcs_out_of_source = [0]
    wc = 2
    for work_c in range(2, worker_count + 1):
        sn_arcs_out_of_source.append(0)
        en_arcs_out_of_source.append(wc)
        cap_arcs_out_of_source.append(1)
        costs_arcs_out_of_source.append(0)
        wc = work_c + 1
    return wc, sn_arcs_out_of_source, en_arcs_out_of_source, cap_arcs_out_of_source, costs_arcs_out_of_source


def _generate_service_sink_arcs(wc, worker_count, service_count):
    llogger = local_logger.LocalLogger()
    llogger.log_call(sys._getframe().f_code.co_name)
    en_arcs_leading_into_sink = [service_count + 1 + worker_count]
    cap_arcs_leading_into_sink = [1]
    costs_arcs_leading_into_sink = [0]
    sn_arcs_leading_into_sink = [wc]
    for sc in range(wc + 1, service_count + wc):
        sn_arcs_leading_into_sink.append(sc)
        en_arcs_leading_into_sink.append(service_count + wc)
        cap_arcs_leading_into_sink.append(1)
        costs_arcs_leading_into_sink.append(0)
    return sn_arcs_leading_into_sink, en_arcs_leading_into_sink, cap_arcs_leading_into_sink,\
        costs_arcs_leading_into_sink


def _generate_worker_service_arcs(worker_count, hardware_matrix, cost_matrix, capacity_matrix):
    llogger = local_logger.LocalLogger()
    llogger.log_call(sys._getframe().f_code.co_name)
    sn_arcs_between_worker_and_service = []
    en_arcs_between_worker_and_service = []
    cap_arcs_between_worker_and_service = []
    costs_arcs_between_worker_and_service = []
    it = numpy.nditer(numpy.asarray(hardware_matrix), order='F', flags=['multi_index'])
    while not it.finished:
        llogger.debug("%d <%s>" % (it[0], it.multi_index))
        if it[0] == 1:
            column = int(it.multi_index[1])
            row = int(it.multi_index[0])
            llogger.debug("Current Worker: %i ; Current Service: %i", column + 1, row + worker_count + 1)
            sn_arcs_between_worker_and_service.append(column + 1)
            en_arcs_between_worker_and_service.append(row + worker_count + 1)
            costs_arcs_between_worker_and_service.append(cost_matrix[row][column])
            cap_arcs_between_worker_and_service.append(capacity_matrix[row][column])
        it.iternext()
    return sn_arcs_between_worker_and_service, en_arcs_between_worker_and_service,\
        costs_arcs_between_worker_and_service, cap_arcs_between_worker_and_service


def _combine_to_list(arcs_a, arcs_b, arcs_c):
    llogger = local_logger.LocalLogger()
    llogger.log_call(sys._getframe().f_code.co_name)
    nodes = list(arcs_a)
    nodes.extend(arcs_b)
    nodes.extend(arcs_c)
    return nodes


def _generate_supply(worker_count, service_count):
    llogger = local_logger.LocalLogger()
    llogger.log_call(sys._getframe().f_code.co_name)
    supply = [worker_count]
    supply.extend((worker_count + service_count) * [0])
    supply.append(0 - service_count)
    return supply


def _solve_using_min_flow_cost(min_cost_flow, services, workers):
    llogger = local_logger.LocalLogger()
    llogger.log_call(sys._getframe().f_code.co_name)
    size_of_workers = len(workers) + 1
    worker_value_list = list(workers.values())
    source = 0
    sink = size_of_workers + len(services)
    service_dict = dict()
    if min_cost_flow.SolveMaxFlowWithMinCost() == min_cost_flow.OPTIMAL:
        llogger.debug('Total cost = %s', min_cost_flow.OptimalCost())
        for arc in range(min_cost_flow.NumArcs()):
            if min_cost_flow.Tail(arc) != source and min_cost_flow.Head(arc) != sink:
                if min_cost_flow.Flow(arc) > 0:
                    service_dict = _append_service_to_allocation(services[min_cost_flow.Head(arc) - size_of_workers],
                                                                 worker_value_list[min_cost_flow.Tail(arc) - 1],
                                                                 min_cost_flow.UnitCost(arc), service_dict)
        return service_dict
    else:
        llogger.debug('There was an issue with the min cost flow input.')
        return None


def _append_service_to_allocation(service, worker, costs, service_allocation_dict):
    llogger = local_logger.LocalLogger()
    llogger.log_call(sys._getframe().f_code.co_name)
    llogger.debug('Worker %s assigned to service %s.  Cost = %d' % (worker, service, costs))
    if worker not in service_allocation_dict:
        service_allocation_dict.update({worker: list()})
    service_allocation_dict[worker].append(service)
    return service_allocation_dict


def _create_simple_min_flow_cost(start_nodes, end_nodes, capacities, costs, supply):
    llogger = local_logger.LocalLogger()
    llogger.log_call(sys._getframe().f_code.co_name)
    # Import the ortools inside the method because it can only be instantiated on x64-based systems
    from ortools.graph import pywrapgraph

    # Instantiate a SimpleMinCostFlow solver.
    min_cost_flow = pywrapgraph.SimpleMinCostFlow()
    # Add each arc.
    for i in range(len(start_nodes)):
        min_cost_flow.AddArcWithCapacityAndUnitCost(start_nodes[i], end_nodes[i],
                                                    capacities[i], costs[i])
    # Add node supplies.
    for i in range(len(supply)):
        min_cost_flow.SetNodeSupply(i, supply[i])

    return min_cost_flow
