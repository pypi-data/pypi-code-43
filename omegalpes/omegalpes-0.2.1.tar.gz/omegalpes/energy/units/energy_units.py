#! usr/bin/env python3
#  -*- coding: utf-8 -*-

"""
**This module defines the energy units of OMEGAlpes. The production,
consumption and storage unit will inherit from it.**

 The energy_units module defines the basic attributes and methods of an
 energy unit in OMEGAlpes.

 It includes the following attributes and quantities:
    - p : instantaneous power of the energy unit (kW)
    - p_min : minimal power (kW)
    - p_max : maximal power (kW)
    - e_tot : total energy during the time period (kWh)
    - e_min : minimal energy of the unit (kWh)
    - e_max : maximal energy of the unit (kWh)
    - u : binary describing if the unit is operating or not at t (delivering or
      consuming P)

..
    Copyright 2018 G2Elab / MAGE

    Licensed under the Apache License, Version 2.0 (the "License");
    you may not use this file except in compliance with the License.
    You may obtain a copy of the License at

         http://www.apache.org/licenses/LICENSE-2.0

    Unless required by applicable law or agreed to in writing, software
    distributed under the License is distributed on an "AS IS" BASIS,
    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
    See the License for the specific language governing permissions and
    limitations under the License.
"""
import warnings

import numpy as np
from pulp import LpBinary, LpInteger, LpContinuous

from ..io.poles import Epole
from ...general.optimisation.elements import Quantity, Constraint, \
    DynamicConstraint, HourlyDynamicConstraint, ExtDynConstraint, Objective
from ...general.optimisation.core import OptObject

__docformat__ = "restructuredtext en"


class EnergyUnit(OptObject):
    """
        **Description**

        Module dedicated to the parent class (EnergyUnit) of :

         - production units
         - consumption units
         - storage units
    """

    def __init__(self, time, name, flow_direction='in', p=None, p_min=-1e+4,
                 p_max=1e+4, e_min=-1e6, e_max=1e6, starting_cost=None,
                 operating_cost=None, min_time_on=None, min_time_off=None,
                 max_ramp_up=None, max_ramp_down=None, co2_out=None,
                 availability_hours=None, energy_type=None,
                 no_warn=True, verbose=True):

        OptObject.__init__(self, name=name, description='Energy unit',
                           verbose=verbose)

        self.parent = None
        self.time = time  # Time unit
        self.energy_type = energy_type

        self.set_e_min = None
        self.set_e_max = None

        if isinstance(p_max, (int, float)):
            p_ub = max(0, p_max)  # Could be 0 when turn off
            max_e = p_ub * time.DT * time.LEN
        elif isinstance(p_max, list):
            p_ub = [max(0, p) for p in p_max]  # Could be 0 when turn off
            max_e = max(p_ub) * time.DT * time.LEN

        if isinstance(p_min, (int, float)):
            p_lb = min(0, p_min)  # Could be 0 when turn off
        elif isinstance(p_min, list):
            p_lb = [min(0, p) for p in p_min]  # Could be 0 when turn off

        self.p = Quantity(name='p',
                          description='instantaneous power of the energy unit',
                          value=p, lb=p_lb, ub=p_ub, vlen=time.LEN, unit='kW',
                          parent=self)

        self.e_tot = Quantity(name='e_tot',
                              description='total energy during the time period',
                              lb=e_min, ub=e_max, vlen=1, unit='kWh',
                              parent=self)

        self.calc_e_tot = Constraint(name='calc_e_tot', parent=self,
                                     exp='{0}_e_tot == time.DT * lpSum({0}_p[t]'
                                         ' for t in time.I)'.format(self.name))

        if isinstance(self, VariableEnergyUnit):
            if max_e > e_max and not isinstance(self, ShiftableEnergyUnit):
                if not no_warn:
                    warnings.warn("Your EnergyUnit {0} won't be able to "
                                  "operate every time steps at its maximal "
                                  "power {1}.".format(name, max_e /
                                                      (time.DT * time.LEN)),
                                  UserWarning)

            # CONSTRAINTS
            self.u = Quantity(name='u',
                              description='indicates if the unit is operating '
                                          'at t',
                              vtype=LpBinary, vlen=time.LEN, parent=self)

            if isinstance(p_max, (int, float)):
                self.on_off_max = DynamicConstraint(
                    exp_t='{0}_p[t] <= {0}_u[t] * {p_M}'.format(self.name,
                                                                p_M=p_max),
                    t_range='for t in time.I', name='on_off_max', parent=self)
            elif isinstance(p_max, list):
                self.on_off_max = DynamicConstraint(
                    exp_t='{0}_p[t] <= {0}_u[t] * {p_M}[t]'.format(self.name,
                                                                   p_M=p_max),
                    t_range='for t in time.I', name='on_off_max', parent=self)

            if isinstance(p_min, (int, float)):
                self.on_off_min = DynamicConstraint(
                    exp_t='{0}_p[t] >= {0}_u[t] * {p_m}'.format(self.name,
                                                                p_m=p_min),
                    t_range='for t in time.I', name='on_off_min',
                    parent=self)
            elif isinstance(p_min, list):
                self.on_off_min = DynamicConstraint(
                    exp_t='{0}_p[t] >= {0}_u[t] * {p_m}[t]'.format(self.name,
                                                                   p_m=p_min),
                    t_range='for t in time.I', name='on_off_min',
                    parent=self)

        # Poles of the energy unit
        self.poles = {1: Epole(self.p, flow_direction, energy_type)}

        self._add_opt_parameters(starting_cost, operating_cost, co2_out)
        self._add_ext_constraints(min_time_on, min_time_off, max_ramp_up,
                                  max_ramp_down, availability_hours)

    def _set_optobject_as_attr(self, optobject: OptObject, attribute_name=None):
        if isinstance(optobject, OptObject):
            if attribute_name:
                self.__setattr__(attribute_name, optobject)
            else:
                self.__setattr__(optobject.name, optobject)

        else:
            raise TypeError('In the add_optobject method, the object should '
                            'be an OptObject class and {0} is a '
                            '{1}'.format(optobject, type(optobject)))

    # Optional parameters
    def _add_opt_parameters(self, starting_cost, operating_cost, co2_out):
        self.start_up = None
        self.switch_off = None
        self.starting_cost = None
        self.operating_cost = None
        self.co2_emissions = None

        # Starting cost
        if starting_cost is not None:
            self.add_starting_cost(starting_cost)

        # Operating cost
        if operating_cost is not None:
            self.add_operating_cost(operating_cost)

        # CO2 emissions
        if co2_out is not None:
            self.add_co2_emissions(co2_out)

    def _add_start_up(self):
        time = self.time
        # Add a variable for start up
        self.start_up = Quantity(name='start_up',
                                 description='The EnergyUnit is '
                                             'starting :1 or not :0',
                                 vtype=LpBinary, vlen=time.LEN, parent=self)

        # When u[t] = 0 and u[t+1] = 1, start_up[t+1] = 1
        self.def_start_up = DynamicConstraint(
            exp_t='{0}_u[t+1] - {0}_u[t] <= '
                  '{0}_start_up[t+1]'.format(self.name),
            t_range='for t in time.I[:-1]', name='def_start_up', parent=self)

        # Else start_up[t+1] = 0
        self.def_no_start_up = DynamicConstraint(
            exp_t='{0}_start_up[t+1] <= ({0}_u[t+1] - {0}_u[t]'
                  ' + 1)/2'.format(self.name),
            t_range='for t in time.I[:-1]',
            name='def_no_start_up', parent=self)

        # Def initial start_up
        self.def_init_start_up = Constraint(
            exp='{0}_start_up[0] == {0}_u[0]'.format(self.name),
            name='def_init_start_up', parent=self)

    def _add_switch_off(self):
        time = self.time
        if self.start_up is None:
            self._add_start_up()

        # Add a variable for switch off
        self.switch_off = Quantity(name='switch_off',
                                   description='The EnergyUnit is '
                                               'switching off :1 or not :0',
                                   vtype=LpBinary, vlen=time.LEN,
                                   parent=self)

        # When u[t} = 1 and u[t+1] = 0, switch_off[t+1] = 0
        self.def_switch_off = DynamicConstraint(
            exp_t='{0}_switch_off[t+1] == {0}_start_up[t+1] '
                  '+ {0}_u[t] - {0}_u[t+1]'.format(self.name),
            t_range='for t in time.I[:-1]',
            name='def_switch_off', parent=self)

        # Set initial switch_off to 0
        self.def_init_switch_off = Constraint(
            exp='{0}_switch_off[0] == 0'.format(self.name),
            name='def_init_switch_off', parent=self)

    def add_starting_cost(self, start_cost: float):
        """
        Add a starting cost associated to the energy unit based on the value
        start_cost.
        Each time the energy unit is starting (or restarting)

            i.e. not functioning time t and functioning time t+1
            ( When start_up[t+1] = 1 corresponding to u[t] = 0 and u[t+1] = 1)

        the start_cost value is added to the starting_costs.

        :param start_cost: float: cost corresponding to the start-up of the
            energy unit
        """
        if self.starting_cost is None:
            if self.start_up is None:
                self._add_start_up()

            # Adding starting cost
            self.starting_cost = Quantity(name='starting_cost',
                                          description='Dynamic cost for the '
                                                      'start'
                                                      ' of EnergyUnit',
                                          lb=0, vlen=self.time.LEN, parent=self)

            # Defining how the starting cost is calculated
            self.calc_start_cost = DynamicConstraint(
                exp_t='{0}_starting_cost[t] == {1} * {0}_start_up[t]'.format(
                    self.name, start_cost),
                t_range='for t in time.I[:-1]', name='calc_start_cost',
                parent=self)

        else:
            raise ValueError("The EnergyUnit {} already has a "
                             "starting cost defined.".format(self.name))

    def add_operating_cost(self, operating_cost: float):
        """
        Add an operating cost associated to the energy unit based on the value
        operating_cost.
        For each time step the energy unit is running the operating_cost
        value is multiplied by the power production or consumption and
        added to the operating_costs.

        :param operating_cost: float: cost corresponding operation of the
            energy unit. To be multiplied by the power at each time step
        """
        if self.operating_cost is None:
            # Adding operating cost
            self.operating_cost = Quantity(name='operating_cost',
                                           description='Dynamic cost for the '
                                                       'operation '
                                                       'of the EnergyUnit',
                                           lb=0,
                                           vlen=self.time.LEN, parent=self)

            if isinstance(operating_cost, (int, float)):
                self.calc_operating_cost = DynamicConstraint(
                    name='calc_operating_cost',
                    exp_t='{0}_operating_cost[t] == {1} * '
                          '{0}_p[t] * time.DT'.format(self.name,
                                                      operating_cost),
                    t_range='for t in time.I', parent=self)

            elif isinstance(operating_cost, list):
                if len(operating_cost) != self.time.LEN:
                    raise IndexError(
                        "Your operating cost should be the size of the time "
                        "period.")
                else:
                    self.calc_operating_cost = DynamicConstraint(
                        name='calc_operating_cost',
                        exp_t='{0}_operating_cost[t] == {1}[t] * '
                              '{0}_p[t] * time.DT'.format(self.name,
                                                          operating_cost),
                        t_range='for t in time.I', parent=self)
            else:
                raise TypeError('The operating_cost should be an int, a float '
                                'or a list.')
        else:
            raise ValueError("The EnergyUnit {} already has an "
                             "operating cost defined.".format(self.name))

    def add_co2_emissions(self, co2_out: float):
        """
        Add an CO2 emissions associated to the energy unit based on the value
        co2_out.
        For each time step the energy unit is running the co2_out
        value is multiplied by the power production or consumption and
        added to the co2_emissions of the energy unit.

        :param co2_out: float: co2 emissions corresponding to the operation
            of the energy unit. To be multiplied by the power at each
            time step
        """
        if self.co2_emissions is None:
            # Adding CO2 emissions from production/consumption
            self.co2_emissions = Quantity(
                name='co2_emissions', description='Dynamic CO2 emissions '
                                                  'generated by the EnergyUnit',
                lb=0, vlen=self.time.LEN, parent=self)

            if isinstance(co2_out, (int, float)):
                self.calc_co2_emissions = DynamicConstraint(
                    exp_t='{0}_co2_emissions[t] == {1} * '
                          '{0}_p[t] * time.DT'.format(self.name, co2_out),
                    name='calc_co2_emissions', parent=self)
            elif isinstance(co2_out, list):
                if len(co2_out) != self.time.LEN:
                    raise IndexError(
                        "Your CO2 emissions (CO2_out should be the size of the "
                        "time period.")
                else:
                    self.calc_co2_emissions = DynamicConstraint(
                        exp_t='{0}_co2_emissions[t] == {1}[t] * '
                              '{0}_p[t] * time.DT'.format(self.name, co2_out),
                        name='calc_co2_emissions', parent=self)
            else:
                raise TypeError('co2_out should be an int, a float or a list.')
        else:
            raise ValueError("The EnergyUnit {} already has CO2 "
                             "emissions defined.".format(self.name))

    # External constraints
    def _add_ext_constraints(self, min_time_on, min_time_off, max_ramp_up,
                             max_ramp_down, availability_hours):
        self.set_max_ramp_up = None
        self.set_max_ramp_down = None
        self.set_min_up_time = None
        self.set_min_down_time = None
        self.set_availability = None

        # Adding a maximal ramp up
        if max_ramp_up is not None:
            self.add_max_ramp_up(max_ramp_up)

        # Adding a maximal ramp down
        if max_ramp_down is not None:
            self.add_max_ramp_down(max_ramp_down)

        # Adding a minimum time on
        if min_time_on is not None:
            self.add_min_time_on(min_time_on)

        # Adding a minimum time off
        if min_time_off is not None:
            self.add_min_time_off(min_time_off)

        # Adding a number of available hours of operation
        if availability_hours is not None:
            self.add_availability(availability_hours)

    def add_max_ramp_up(self, max_ramp_up: float):
        """
        Add a maximal ramp value between two consecutive power values
        increasing

        :param max_ramp_up: float: maximal ramp value between two consecutive
            power values increasing
        """
        if self.set_max_ramp_up is None:
            self.set_max_ramp_up = ExtDynConstraint(
                exp_t='{0}_p[t+1] - {0}_p[t] <= {1}'.format(self.name,
                                                            max_ramp_up),
                t_range='for t in time.I[:-1]', name='set_max_ramp_up',
                parent=self)
        else:
            raise ValueError("The EnergyUnit {} already has a maximal "
                             "ramp up defined.".format(self.name))

    def add_max_ramp_down(self, max_ramp_down: float):
        """
        Add a maximal ramp value between two consecutive power values
        decreasing

        :param max_ramp_down: float: maximal ramp value between two consecutive
            power values decreasing
        """
        if self.set_max_ramp_down is None:
            self.set_max_ramp_down = ExtDynConstraint(
                exp_t='{0}_p[t] - {0}_p[t+1] <= {1}'.format(self.name,
                                                            max_ramp_down),
                t_range='for t in time.I[:-1]', name='set_max_ramp_down',
                parent=self)
        else:
            raise ValueError("The EnergyUnit {} already has a maximal "
                             "ramp down".format(self.name))

    def add_min_time_on(self, min_time_on: float):
        """
        Add a minimal time during which the energy unit should function once
        it is started-up

        :param min_time_on: float: minimal time during which the energy unit
            should function once it is started-up
        """
        if self.set_min_up_time is None:
            if self.start_up is None:
                self._add_start_up()

            # When the unit starts, it should be on during min_time_on
            self.set_min_up_time = ExtDynConstraint(
                exp_t='{0}_u[t] >= lpSum({0}_start_up[i] for i in range('
                      'max(t - {1} + 1, 0), t))'.format(self.name, min_time_on),
                t_range='for t in time.I', name='set_min_up_time', parent=self)
        else:
            raise ValueError("The EnergyUnit {} already has a "
                             "minimum time on.".format(self.name))

    def add_min_time_off(self, min_time_off: float):
        """
        Add a minimal time during which the energy unit has to remain off
        once it is switched off

        :param min_time_off: float: minimal time during which the energy unit
            has to remain off once it is switched off
        """
        if self.set_min_down_time is None:
            if self.switch_off is None:
                self._add_switch_off()
            # When the unit switches off, it should be off during min_time_off
            self.set_min_down_time = ExtDynConstraint(
                exp_t='1 - {0}_u[t] >= lpSum({0}_switch_off[i] for i in range('
                      'max(t - {1} + 1, 0), t))'.format(self.name,
                                                        min_time_off),
                t_range='for t in time.I', name='set_min_down_time',
                parent=self)

        else:
            raise ValueError("The EnergyUnit {} already has a "
                             "minimum time down.".format(self.name))

    def add_availability(self, av_hours: int):
        """
        Add a number of hours of availability of the energy unit during the
        study period

        :param av_hours: int: number of hours of availability of the energy
            unit during the study period
        """
        if self.set_availability is None:
            self.set_availability = Constraint(
                exp='lpSum({dt} * {name}_u[t] for t in time.I) <= '
                    '{av_h}'.format(dt=self.time.DT, name=self.name,
                                    av_h=av_hours),
                name='set_availability', parent=self)
        else:
            raise ValueError("The EnergyUnit {} already has hours of "
                             "availability defined.".format(self.name))

    def add_operating_time_range(self, operating_time_range=[[int, int]]):
        """
        Add a range of hours during which the energy unit can be operated

        example: [[10, 12], [14, 17]]
        
        :param operating_time_range: [[first hour of functioning : int,
        hour to stop (not in functioning): int]]
        """

        if operating_time_range[0][0] == 0:
            pass

        else:
            set_start_time_range = HourlyDynamicConstraint(
                exp_t='{name}_u[t] == 0'.format(name=self.name),
                time=self.time,
                init_h=0,
                final_h=operating_time_range[0][0] - 1,
                name='set_operating_init_time_range_{}'.format(
                    operating_time_range[0][0]),
                parent=self)
            setattr(self, 'set_start_time_range_{}'.format(
                operating_time_range[0][0]),
                    set_start_time_range)

        if len(operating_time_range) != 1:
            set_time_range = []
            for i in range(1, len(operating_time_range)):
                print(operating_time_range[i - 1][1])
                print(operating_time_range[i][0] - 1)
                set_time_range.append(HourlyDynamicConstraint(
                    exp_t='{name}_u[t] == 0'.format(name=self.name),
                    time=self.time,
                    init_h=operating_time_range[i - 1][1],
                    final_h=operating_time_range[i][0] - 1,
                    name='set_time_range_{}_{}'.format(
                        operating_time_range[i - 1][1],
                        operating_time_range[i][0]),
                    parent=self))
                setattr(self,
                        'set_time_range_{}_{}'.format(
                            operating_time_range[i - 1][1],
                            operating_time_range[i][0]),
                        set_time_range[i - 1])

        if operating_time_range[-1][1] == 23:
            pass
        else:
            set_end_time_range = HourlyDynamicConstraint(
                exp_t='{name}_u[t] == 0'.format(name=self.name),
                time=self.time,
                init_h=operating_time_range[-1][1],
                final_h=23,
                name='set_operating_final_time_range_{}'.format(
                    operating_time_range[0][1]),
                parent=self)
            setattr(self,
                    'set_end_time_range_{}'.format(operating_time_range[0][1]),
                    set_end_time_range)

    def set_energy_limits_on_time_period(self, e_min=0, e_max=None,
                                         start='YYYY-MM-DD HH:MM:SS',
                                         end='YYYY-MM-DD HH:MM:SS',
                                         period_index=None):
        """
        Add an energy limit during a defined time period

        :param e_min: Minimal energy set during the time period (int or float)
        :param e_max: Maximal energy set during the time period (int or float)
        :param start: Date of start of the time period  YYYY-MM-DD HH:MM:SS (
            str)
        :param end: Date of end of the time period   YYYY-MM-DD HH:MM:SS (str)
        """
        if period_index is None:
            if start == 'YYYY-MM-DD HH:MM:SS':
                index_start = ''
            else:
                index_start = self.time.get_index_for_date(start)

            if end == 'YYYY-MM-DD HH:MM:SS':
                index_end = ''
            else:
                index_end = self.time.get_index_for_date(end)

            period_index = 'time.I[{start}:{end}]'.format(start=index_start,
                                                          end=index_end)

        if e_min != 0:
            self.set_e_min = Constraint(
                exp='time.DT * lpSum({0}_p[t] for t in {1}) '
                    '>= {2}'.format(self.name, period_index, e_min),
                name='set_e_min', parent=self)

        if e_max is not None:
            if e_max > self.e_tot.ub:
                self.e_tot.ub = e_max

            self.set_e_max = Constraint(
                exp='time.DT * lpSum({0}_p[t] for t in {1}) '
                    '<= {2}'.format(self.name, period_index, e_max),
                name='set_e_max', parent=self)

    # OBJECTIVES #
    def minimize_starting_cost(self, weight=1):
        """
        Objective to minimize the starting costs

        :param weight: Weight coefficient for the objective
        """
        if self.starting_cost is not None:
            self.min_start_cost = Objective(name='min_start_cost',
                                            exp='lpSum({0}_starting_cost[t] '
                                                'for t '
                                                'in time.I)'
                                            .format(self.name), weight=weight,
                                            parent=self)
        else:
            raise ValueError("You should add a starting cost before trying "
                             "to minimize_starting_cost.")

    def minimize_operating_cost(self, weight=1):
        """
        Objective to minimize the operating costs

        :param weight: Weight coefficient for the objective
        """
        if self.operating_cost is not None:
            self.min_operating_cost = Objective(name='min_operating_cost',
                                                exp='lpSum({'
                                                    '0}_operating_cost[t] '
                                                    'for t in time.I)'
                                                .format(self.name),
                                                weight=weight, parent=self)
        else:
            raise ValueError("You should add an operating cost before trying "
                             "to minimize_operating_cost.")

    def minimize_costs(self, weight=1):
        """
        Objective to minimize the costs (starting and operating costs)

        :param weight: Weight coefficient for the objective
        """
        if self.starting_cost is not None:
            self.minimize_starting_cost(weight)

        if self.operating_cost is not None:
            self.minimize_operating_cost(weight)

    def minimize_energy(self, weight=1):
        """
        Objective to minimize the energy of the energy unit

        :param weight: Weight coefficient for the objective
        """
        self.min_energy = Objective(name='min_energy',
                                    exp='lpSum({0}_p[t] for t in time.I)'
                                    .format(self.name), weight=weight,
                                    parent=self)

    def minimize_time_of_use(self, weight=1):
        """
        Objective to minimize the time of running of the energy unit

        :param weight: Weight coefficient for the objective
        """
        self.min_time_of_use = Objective(name='min_time_of_use',
                                         exp='lpSum({0}_u[t] for t in time.I)'
                                         .format(self.name), weight=weight,
                                         parent=self)

    def minimize_co2_emissions(self, weight=1):
        """
        Objective to minimize the co2 emissions of the energy unit

        :param weight: Weight coefficient for the objective
        """
        self.min_co2_emissions = Objective(name='min_CO2_emissions',
                                           exp='lpSum({0}_co2_emissions[t] '
                                               'for t in time.I)'.format(
                                               self.name),
                                           weight=weight, parent=self)


class FixedEnergyUnit(EnergyUnit):
    """
    **Description**

        Energy unit with a fixed power profile.

    **Attributs**

        * p : instantaneous power known by advance (kW)
        * energy_type : type of energy ('Electrical', 'Heat', ...)

    """

    def __init__(self, time, name: str, p: list, flow_direction='in',
                 starting_cost=None, operating_cost=None, co2_out=None,
                 energy_type=None, verbose=True):
        if p is None:
            raise TypeError(
                "You have to define the power profile (p) for the "
                "FixedEnergyUnit !")

        e_tot = sum(p) * time.DT

        EnergyUnit.__init__(self, time=time, name=name, p=p, p_min=min(p),
                            p_max=max(p), e_min=e_tot, e_max=e_tot,
                            flow_direction=flow_direction,
                            starting_cost=starting_cost,
                            operating_cost=operating_cost, min_time_on=None,
                            min_time_off=None, max_ramp_up=None,
                            max_ramp_down=None, co2_out=co2_out,
                            availability_hours=None, energy_type=energy_type,
                            verbose=verbose, no_warn=True)


class VariableEnergyUnit(EnergyUnit):
    def __init__(self, time, name, flow_direction='in', p_min=-1e+4,
                 p_max=1e+4, e_min=-1e6, e_max=1e6, starting_cost=None,
                 operating_cost=None, min_time_on=None, min_time_off=None,
                 max_ramp_up=None, max_ramp_down=None, co2_out=None,
                 availability_hours=None, energy_type=None,
                 verbose=True, no_warn=True):
        EnergyUnit.__init__(self, time, name, flow_direction=flow_direction,
                            p=None, p_min=p_min, p_max=p_max, e_min=e_min,
                            e_max=e_max, starting_cost=starting_cost,
                            operating_cost=operating_cost,
                            min_time_on=min_time_on,
                            min_time_off=min_time_off, max_ramp_up=max_ramp_up,
                            max_ramp_down=max_ramp_down, co2_out=co2_out,
                            availability_hours=availability_hours,
                            energy_type=energy_type,
                            verbose=verbose, no_warn=no_warn)


class SquareEnergyUnit(VariableEnergyUnit):
    def __init__(self, time, name, p_square, n_square, t_between_sq, t_square=1,
                 flow_direction='in', starting_cost=None, operating_cost=None,
                 co2_out=None, energy_type=None,
                 verbose=True, no_warn=True):
        """

        :param time:
        :param name:
        :param p_square: Power of the square
        :param n_square: Number of squares
        :param t_square: Duration of a square [h]
        :param t_between_sq: Duration between squares [h]
        :param flow_direction:
        :param e_min:
        :param e_max:
        :param starting_cost:
        :param operating_cost:
        :param min_time_on:
        :param min_time_off:
        :param max_ramp_up:
        :param max_ramp_down:
        :param co2_out:
        :param availability_hours:
        :param energy_type:
        """
        if not isinstance(t_square, int):
            raise TypeError('t_squre should be an integer, but is '
                            'a {}'.format(type(t_square)))

        energy = n_square * t_square * p_square

        if n_square == 1:
            min_time_on = None
            min_time_off = None
            av_h = t_square
        else:
            min_time_on = t_square
            min_time_off = t_between_sq
            av_h = None

        VariableEnergyUnit.__init__(self, time, name,
                                    flow_direction=flow_direction,
                                    p_min=p_square, p_max=p_square,
                                    e_min=energy,
                                    e_max=energy, starting_cost=starting_cost,
                                    operating_cost=operating_cost,
                                    min_time_on=min_time_on,
                                    min_time_off=min_time_off, max_ramp_up=None,
                                    max_ramp_down=None, co2_out=co2_out,
                                    availability_hours=av_h,
                                    energy_type=energy_type,
                                    verbose=verbose,
                                    no_warn=no_warn)


class ShiftableEnergyUnit(VariableEnergyUnit):
    """
    **Description**

        EnergyUnit with shiftable power profile.

    **Attributs**

        * power_values : power profile to shift (kW)
        * mandatory : indicates if the power is mandatory (True) or not (False)
        * starting_cost : cost of the starting of the EnergyUnit
        * operating_cost : cost of the operation (€/kW)
        * energy_type : type of energy ('Electrical', 'Heat', ...)

    """

    def __init__(self, time, name: str, flow_direction, power_values,
                 mandatory=True, co2_out=None, starting_cost=None,
                 operating_cost=None, energy_type=None,
                 verbose=True):
        # Crop the power profile
        while power_values[0] == 0:
            power_values = power_values[1:]
        while power_values[-1] == 0:
            power_values = power_values[:-1]

        # Works if all values are strictly positives
        epsilon = 0.00001 * min(p > 0 for p in power_values)
        power_profile = [max(epsilon, p) for p in power_values]

        e_max = sum(power_profile) * time.DT

        if mandatory:
            e_min = e_max
        else:
            e_min = 0

        p_min = min(power_profile)
        p_max = max(power_profile)

        VariableEnergyUnit.__init__(self, time, name=name,
                                    flow_direction=flow_direction,
                                    p_min=p_min, p_max=p_max, e_min=e_min,
                                    e_max=e_max, starting_cost=starting_cost,
                                    operating_cost=operating_cost,
                                    min_time_on=None, min_time_off=None,
                                    max_ramp_up=None, max_ramp_down=None,
                                    co2_out=co2_out, availability_hours=None,
                                    energy_type=energy_type,
                                    verbose=verbose,
                                    no_warn=True)

        self._add_start_up()

        self.power_values = Quantity(name='power_values', opt=False,
                                     value=power_values, parent=self)

        for i, _ in enumerate(power_values):
            cst_name = 'def_{}_power_value'.format(i)

            exp_t = "{0}_p[t] >= {0}_power_values[{1}] * " \
                    "{0}_start_up[t-{1}]".format(self.name, i)

            cst = DynamicConstraint(name=cst_name, exp_t=exp_t,
                                    t_range="for t in time.I[{}:-1]".format(i),
                                    parent=self)
            setattr(self, cst_name, cst)


class TriangleEnergyUnit(ShiftableEnergyUnit):
    def __init__(self, time, name, flow_direction, p_peak, alpha_peak,
                 t_triangle, mandatory=True, starting_cost=None,
                 operating_cost=None, co2_out=None, energy_type=None,
                 verbose=True):

        if not isinstance(t_triangle, int):
            raise TypeError('t_triangle should be an integer, but is '
                            'a {}'.format(type(t_triangle)))

        t_peak = alpha_peak * t_triangle

        if alpha_peak == 0:
            ramp_1 = 0
            ramp_2 = - p_peak / (t_triangle - t_peak)
        elif alpha_peak == 1:
            ramp_1 = p_peak / t_peak
            ramp_2 = 0
        else:
            ramp_1 = p_peak / t_peak
            ramp_2 = - p_peak / (t_triangle - t_peak)

        t = np.arange(0, t_triangle)

        triangle_profile = np.piecewise(
            t, [t <= t_peak - 1, (t_peak - 1 < t) & (t < t_peak), t_peak <= t],
            [lambda t: ramp_1 * (2 * t + 1) / 2,
             lambda t: (ramp_1 * t * (t_peak - t)
                        + ramp_2 * (t + 1 - t_triangle) * (t + 1 - t_peak)
                        + p_peak) / 2,
             lambda t: ramp_2 * (2 * t + 1 - 2 * t_triangle) / 2])

        triangle_profile = [float(p) for p in triangle_profile]

        ShiftableEnergyUnit.__init__(self, time, name,
                                     flow_direction=flow_direction,
                                     power_values=list(triangle_profile),
                                     mandatory=mandatory, co2_out=co2_out,
                                     starting_cost=starting_cost,
                                     operating_cost=operating_cost,
                                     energy_type=energy_type,
                                     verbose=verbose,
                                     no_warn=True)


class SawtoothEnergyUnit(ShiftableEnergyUnit):
    def __init__(self, time, name, flow_direction, p_peak, p_low, alpha_peak,
                 t_triangle, t_sawtooth, mandatory=True, starting_cost=None,
                 operating_cost=None, co2_out=None, energy_type=None,
                 verbose=True):
        if not isinstance(t_triangle, int):
            raise TypeError('t_triangle should be an integer, but is '
                            'a {}'.format(type(t_triangle)))
        if not isinstance(t_sawtooth, int):
            raise TypeError('t_sawtooth should be an integer, but is '
                            'a {}'.format(type(t_sawtooth)))

        t_peak = alpha_peak * t_triangle

        if alpha_peak == 0:
            ramp_1 = 0
            ramp_2 = - p_peak / (t_triangle - t_peak)
        elif alpha_peak == 1:
            ramp_1 = p_peak / t_peak
            ramp_2 = 0
        else:
            ramp_1 = p_peak / t_peak
            ramp_2 = - p_peak / (t_triangle - t_peak)

        t = np.arange(0, t_triangle)

        triangle_profile = np.piecewise(
            t, [t <= t_peak - 1, (t_peak - 1 < t) & (t < t_peak), t_peak <= t],
            [lambda t: ramp_1 * (2 * t + 1) / 2,
             lambda t: (ramp_1 * t * (t_peak - t)
                        + ramp_2 * (t + 1 - t_triangle) * (t + 1 - t_peak)
                        + p_peak) / 2,
             lambda t: ramp_2 * (2 * t + 1 - 2 * t_triangle) / 2])

        for espace in range(t_sawtooth - 2 * t_triangle + 1):
            if (t_sawtooth - t_triangle) % (t_triangle + espace) == 0:
                N = int((t_sawtooth + espace) / (t_triangle + espace))
                break

        triangle = [float(P) for P in triangle_profile]

        sawtooth_profile = triangle + (N - 1) * (espace * [p_low] + triangle)

        ShiftableEnergyUnit.__init__(self, time, name,
                                     flow_direction=flow_direction,
                                     power_values=list(sawtooth_profile),
                                     mandatory=mandatory, co2_out=co2_out,
                                     starting_cost=starting_cost,
                                     operating_cost=operating_cost,
                                     energy_type=energy_type,
                                     verbose=verbose,
                                     no_warn=True)


class SeveralEnergyUnit(VariableEnergyUnit):
    """
    **Description**

        Energy unit based on a fixed power curve enabling to multiply
        several times (nb_unit) the same power curve.

        Be careful, if imaginary == True, the solution may be imaginary as
        nb_unit can be continuous. The accurate number of the power unit
        should be calculated later

    **Attributs**

        * fixed_power : fixed power curve

    """

    def __init__(self, time, name, fixed_power, pmin=1e-5, pmax=1e+5,
                 imaginary=False, e_min=0, e_max=1e6, nb_unit_min=0,
                 nb_unit_max=None, flow_direction='in', starting_cost=None,
                 operating_cost=None, max_ramp_up=None, max_ramp_down=None,
                 co2_out=None, energy_type=None,
                 verbose=True, no_warn=True):
        VariableEnergyUnit.__init__(self, time=time, name=name,
                                    flow_direction=flow_direction,
                                    p_min=pmin, p_max=pmax, e_min=e_min,
                                    e_max=e_max, starting_cost=starting_cost,
                                    operating_cost=operating_cost,
                                    min_time_on=None, min_time_off=None,
                                    max_ramp_up=max_ramp_up,
                                    max_ramp_down=max_ramp_down,
                                    co2_out=co2_out, availability_hours=None,
                                    energy_type=energy_type,
                                    verbose=verbose,
                                    no_warn=no_warn)

        self.power_curve = Quantity(name='power_curve', opt=False,
                                    value=fixed_power, vlen=time.LEN,
                                    parent=self)

        if imaginary:
            self.nb_unit = Quantity(name='nb_unit', opt=True,
                                    vtype=LpContinuous,
                                    lb=nb_unit_min, ub=nb_unit_max, vlen=1,
                                    parent=self)
            warnings.warn(
                'The solution may be imaginary as nb_unit is continuous')
        else:
            self.nb_unit = Quantity(name='nb_unit', opt=True, vtype=LpInteger,
                                    lb=nb_unit_min, ub=nb_unit_max, vlen=1,
                                    parent=self)

        self.calc_power_with_nb_unit_cst = DynamicConstraint(
            exp_t='{0}_p[t] == {0}_nb_unit * {0}_power_curve[t]'.format(
                self.name), name='calc_power_with_nb_unit',
            t_range='for t in time.I', parent=self)
