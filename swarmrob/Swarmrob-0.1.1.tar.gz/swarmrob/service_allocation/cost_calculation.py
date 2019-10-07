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

import jsonpickle
import sympy

from ..logger import evaluation_logger
from ..logger import local_logger


PRECISION = 4


class CostCalculation:
    """
    Implemented cost function class with the default cost function that is described in the paper
    """
    def __init__(self):
        self.cpu_cost_weight = 0.25
        self.vram_cost_weight = 0.25
        self.swap_cost_weight = 0.25
        self.image_download_cost_weight = 0.25

    def calculate_costs_and_check_hardware_in_thread(self, column_id, service, worker, queue):
        """
            Wrapper method for the cost function
        :param column_id: ID of the cost matrix column
        :param service: Related service object
        :param worker: Related worker object
        :param queue: Thread result queue
        :return:
        """
        if column_id is None or column_id < 0 or service is None or worker is None or queue is None:
            return
        llogger = local_logger.LocalLogger()
        llogger.log_method_call(self.__class__.__name__, sys._getframe().f_code.co_name)
        llogger.debug("%s@%s", worker.uuid, worker.advertise_address)
        cost_and_hardware_column = dict()
        hardware_row_for_service = worker.check_hardware(jsonpickle.encode(service))
        cost_row_for_service = self._calculate_costs(worker, service)
        cost_and_hardware_column.update({"cost": cost_row_for_service})
        cost_and_hardware_column.update({"hw": hardware_row_for_service})
        thread_return = dict()
        thread_return.update({column_id: cost_and_hardware_column})
        llogger.debug(thread_return)
        queue.put(thread_return)

    def _calculate_costs(self, worker, service):
        """
            Implemented cost calculation method
        :param service: Related service object
        :param worker: Related worker object
        :return:
        """
        llogger = local_logger.LocalLogger()
        llogger.log_method_call(self.__class__.__name__, sys._getframe().f_code.co_name)
        cpu_usage_of_worker, vram_usage_of_worker, swap_usage_of_worker, size_of_docker_image, bandwidth_in_percent = \
            self._get_usage_of_worker(worker, service)
        cpu_costs, vram_costs, swap_costs, image_download_costs = self._calculate_partial_costs(cpu_usage_of_worker,
                                                                                                vram_usage_of_worker,
                                                                                                swap_usage_of_worker,
                                                                                                size_of_docker_image,
                                                                                                bandwidth_in_percent
                                                                                                )
        overall_costs = self._calculate_overall_costs(cpu_costs, vram_costs, swap_costs, image_download_costs)
        evaluation_logger.EvaluationLogger().write(
                        [service.id, worker.hostname, cpu_usage_of_worker, vram_usage_of_worker, swap_usage_of_worker,
                         bandwidth_in_percent, cpu_costs * self.cpu_cost_weight, vram_costs * self.vram_cost_weight,
                         swap_costs * self.swap_cost_weight, image_download_costs * self.image_download_cost_weight,
                         overall_costs], evaluation_logger.LogType.COSTS)
        return int(overall_costs)

    def _calculate_overall_costs(self, cpu_costs, vram_costs, swap_costs, image_download_costs):
        llogger = local_logger.LocalLogger()
        llogger.log_method_call(self.__class__.__name__, sys._getframe().f_code.co_name)
        cc, ccw, vc, vcw, sc, scw, idc, idcw = sympy.symbols("cc ccw vc vcw sc scw idc idcw")
        overall_costs_expr = (cc * ccw) + (vc * vcw) + (sc * scw) + (idc * idcw)
        return round(overall_costs_expr.subs(
            {cc: cpu_costs, ccw: self.cpu_cost_weight, vc: vram_costs, vcw: self.vram_cost_weight, sc: swap_costs,
             scw: self.swap_cost_weight, idc: image_download_costs, idcw: self.image_download_cost_weight}),
            PRECISION)

    def _calculate_partial_costs(self, cpu_usage_of_worker, vram_usage_of_worker, swap_usage_of_worker,
                                 size_of_docker_image, bandwidth_in_percent):
        llogger = local_logger.LocalLogger()
        llogger.log_method_call(self.__class__.__name__, sys._getframe().f_code.co_name)
        # CPU-Usage Equation
        cuow = sympy.symbols("cuow")
        cpu_cost_expr = (10 * pow(cuow, 4)) * pow(10, 4)
        cpu_costs = round(cpu_cost_expr.subs({cuow: cpu_usage_of_worker}), PRECISION)
        # VRAM-Usage Equation
        vuow = sympy.symbols("vuow")
        vram_cost_expr = (10 * pow(vuow, 4)) * pow(10, 4)
        vram_costs = round(vram_cost_expr.subs({vuow: vram_usage_of_worker}), PRECISION)
        # SWAP-Usage Equation
        suow = sympy.symbols("suow")
        swap_cost_expr = (10 * pow(suow, 1)) * pow(10, 4)
        swap_costs = round(swap_cost_expr.subs({suow: swap_usage_of_worker}), PRECISION)
        # Image-Download Equation
        sodi, bw = sympy.symbols("sodi bw")
        image_cost_expr = (10 * pow((1 - bw), 10)) * pow(10, 4)
        image_download_costs = round(image_cost_expr.subs({sodi: size_of_docker_image, bw: bandwidth_in_percent}),
                                     PRECISION)
        return cpu_costs, vram_costs, swap_costs, image_download_costs

    def _get_usage_of_worker(self, worker, service):
        llogger = local_logger.LocalLogger()
        llogger.log_method_call(self.__class__.__name__, sys._getframe().f_code.co_name)
        image_tag = service.tag
        try:
            splitted_tag = image_tag.split(":")
            if len(splitted_tag) > 1:
                repository = image_tag.split(":")[0]
            else:
                repository = None
        except KeyError:
            repository = None
        max_download = 125000000
        cpu_usage_of_worker = worker.get_cpu_usage() / 100
        vram_usage_of_worker = worker.get_vram_usage() / 100
        swap_usage_of_worker = worker.get_swap_ram_usage() / 100
        size_of_docker_image = worker.get_remaining_image_download_size(image_tag)

        bandwidth = worker.get_bandwidth(repository)
        llogger.debug("CPU-Usage: %s", cpu_usage_of_worker)
        llogger.debug("VRAM-Usage: %s", vram_usage_of_worker)
        llogger.debug("SWAP-Usage: %s", swap_usage_of_worker)

        bandwidth_in_percent = bandwidth / max_download
        llogger.debug("Bandwith in Bytes: %s", bandwidth)
        llogger.debug("Bandwidth in Percent: %s", bandwidth_in_percent)
        return cpu_usage_of_worker, vram_usage_of_worker, swap_usage_of_worker,\
            size_of_docker_image, bandwidth_in_percent
