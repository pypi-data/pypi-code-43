#! usr/bin/env python3
#  -*- coding: utf-8 -*-

"""
**This module defines the production units**

The production_units module defines various kinds of production units with
associated attributes and methods.

It includes :
 - ProductionUnit : simple production unit inheriting from EnergyUnit and
   with an outer flow direction. The outside co2 emissions, the starting cost,
   the operating cost, the minimal operating time, the minimal non-operating
   time, the maximal increasing ramp and the maximal decreasing ramp can be
   filled.

   Objectives are also available :

    * minimize starting cost, operating cost, total cost
    * minimize production, co2_emissions, time of use
    * maximize production

 - FixedProductionUnit : Production unit with a fixed production profile.
 - VariableProductionUnit : Production unit with a variation of power between
   pmin et pmax.

And also :
 - SeveralProductionUnit: Production unit based on a fixed production curve
   enabling to multiply several times (nb_unit) the same production curve
 - SeveralImaginaryProductionUnit: Production unit based on a fixed
   production curve enabling to multiply several times (nb_unit) the same
   production curve. Be careful, the solution may be imaginary as nb_unit
   can be continuous. The accurate number of the production unit should be
   calculated later
 - SquareProductionUnit: Production unit with a fixed value and fixed
   duration.
 - ShiftableProductionUnit: Production unit with shiftable production
   profile.

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
from pulp import LpBinary, LpInteger, LpContinuous

from .energy_units import *
from ...general.optimisation.elements import Constraint, DynamicConstraint, \
    ExtDynConstraint
from ...general.optimisation.elements import Objective
from ...general.optimisation.elements import Quantity

__docformat__ = "restructuredtext en"


class ProductionUnit(EnergyUnit):
    """
    **Description**

        Simple Production unit

    **Attributes**

     * co2_out: outside co2 emissions
     * starting_cost: the starting cost
     * operating_cost: the operating cost
     * min_time_on : the minimal operating time
     * min_time_off : the minimal non-operating time
     * max_ramp_up : the  maximal increasing ramp
     * max_ramp_down ; the maximal decreasing ramp
    """

    def __init__(self, time, name, p=None, p_min=1e-5, p_max=1e+5, e_min=0,
                 e_max=1e6, co2_out=None, starting_cost=None,
                 operating_cost=None, min_time_on=None, min_time_off=None,
                 max_ramp_up=None, max_ramp_down=None, availability_hours=None,
                 energy_type=None, verbose=True, no_warn=True):

        EnergyUnit.__init__(self, time, name, flow_direction='out', p=p,
                            p_min=p_min, p_max=p_max, e_min=e_min, e_max=e_max,
                            co2_out=co2_out, starting_cost=starting_cost,
                            operating_cost=operating_cost,
                            min_time_on=min_time_on,
                            min_time_off=min_time_off, max_ramp_up=max_ramp_up,
                            max_ramp_down=max_ramp_down,
                            availability_hours=availability_hours,
                            energy_type=energy_type,
                            verbose=verbose, no_warn=no_warn)

    def minimize_production(self, weight=1):
        """

        :param weight: Weight coefficient for the objective
        """
        self.minimize_energy(weight=weight)
        self.min_energy.name = 'min_production'

    def maximize_production(self, weight=1):
        """

        :param weight: Weight coefficient for the objective
        """
        self.minimize_energy(weight=-1 * weight)
        self.min_energy.name = 'max_production'


class FixedProductionUnit(FixedEnergyUnit, ProductionUnit):
    """
    **Description**

        Production unit with a fixed production profile.

    **Attributes**

     * p : instantaneous power production known by advance (kW)
     * energy_type : type of energy ('Electrical', 'Heat', ...)


    """

    def __init__(self, time, name: str, p: list = None, co2_out=None,
                 starting_cost=None, operating_cost=None, energy_type=None,
                 verbose=True):
        ProductionUnit.__init__(self, time=time, name=name, verbose=verbose)
        FixedEnergyUnit.__init__(self, time, name=name, p=p,
                                 flow_direction='out',
                                 starting_cost=starting_cost,
                                 operating_cost=operating_cost, co2_out=co2_out,
                                 energy_type=energy_type,
                                 verbose=False)


class VariableProductionUnit(VariableEnergyUnit, ProductionUnit):
    """
    **Description**

        Production unit with a variation of power between pmin et pmax.

    **Attributes**

     * pmax : maximal instantaneous power production (kW)
     * pmin : minimal instantaneous power production (kW)
     * energy_type : type of energy ('Electrical', 'Heat', ...)

    """

    def __init__(self, time, name, pmin=1e-5, pmax=1e+5, e_min=0,
                 e_max=1e6, co2_out=None, starting_cost=None,
                 operating_cost=None, min_time_on=None, min_time_off=None,
                 max_ramp_up=None, max_ramp_down=None, energy_type=None,
                 verbose=True, no_warn=True):
        ProductionUnit.__init__(self, time=time, name=name, verbose=verbose)
        VariableEnergyUnit.__init__(self, time, name=name,
                                    flow_direction='out', p_min=pmin,
                                    p_max=pmax, e_min=e_min, e_max=e_max,
                                    starting_cost=starting_cost,
                                    operating_cost=operating_cost,
                                    min_time_on=min_time_on,
                                    min_time_off=min_time_off,
                                    max_ramp_up=max_ramp_up,
                                    max_ramp_down=max_ramp_down,
                                    co2_out=co2_out, energy_type=energy_type,
                                    verbose=False,
                                    no_warn=no_warn)


class SeveralProductionUnit(VariableProductionUnit, SeveralEnergyUnit):
    """
    **Description**

        Production unit based on a fixed production curve enabling to multiply
        several times (nb_unit) the same production curve.
        nb_unit is an integer variable.

    **Attributes**

     * fixed_prod : fixed production curve

    """

    def __init__(self, time, name, fixed_prod, pmin=1e-5, pmax=1e+5, e_min=0,
                 e_max=1e6, nb_unit_min=0, nb_unit_max=None, co2_out=None,
                 starting_cost=None, operating_cost=None, max_ramp_up=None,
                 max_ramp_down=None, energy_type=None,
                 verbose=True, no_warn=True):
        VariableProductionUnit.__init__(self, time=time, name=name,
                                        verbose=verbose)
        SeveralEnergyUnit.__init__(self, time, name=name,
                                   fixed_power=fixed_prod, pmin=pmin,
                                   pmax=pmax, imaginary=False, e_min=e_min,
                                   e_max=e_max, nb_unit_min=nb_unit_min,
                                   nb_unit_max=nb_unit_max,
                                   flow_direction='out',
                                   starting_cost=starting_cost,
                                   operating_cost=operating_cost,
                                   max_ramp_up=max_ramp_up,
                                   max_ramp_down=max_ramp_down,
                                   co2_out=co2_out, energy_type=energy_type,
                                   verbose=False,
                                   no_warn=no_warn)


class SeveralImaginaryProductionUnit(VariableProductionUnit, SeveralEnergyUnit):
    """
    **Description**

        Production unit based on a fixed production curve enabling to multiply
        several times (nb_unit) the same production curve.
        Be careful, the solution may be imaginary as nb_unit can be
        continuous. The accurate number of the production unit should be
        calculated later.

    **Attributes**

     * fixed_prod : fixed production curve

    """

    def __init__(self, time, name, fixed_prod, pmin=1e-5, pmax=1e+5, e_min=0,
                 e_max=1e6, nb_unit_min=0, nb_unit_max=None, co2_out=None,
                 starting_cost=None, operating_cost=None, max_ramp_up=None,
                 max_ramp_down=None, energy_type=None,
                 verbose=True, no_warn=True):
        VariableProductionUnit.__init__(self, time=time, name=name,
                                        verbose=verbose)
        SeveralEnergyUnit.__init__(self, time, name=name,
                                   fixed_power=fixed_prod, pmin=pmin,
                                   pmax=pmax, imaginary=True, e_min=e_min,
                                   e_max=e_max, nb_unit_min=nb_unit_min,
                                   nb_unit_max=nb_unit_max,
                                   flow_direction='out',
                                   starting_cost=starting_cost,
                                   operating_cost=operating_cost,
                                   max_ramp_up=max_ramp_up,
                                   max_ramp_down=max_ramp_down,
                                   co2_out=co2_out, energy_type=energy_type,
                                   verbose=False,
                                   no_warn=no_warn)


class SquareProductionUnit(SquareEnergyUnit, VariableProductionUnit):
    """
    **Description**

        | Production unit with a fixed value and fixed duration.
        | Only the time of beginning can be modified.
        | Operation can be mandatory or not.

    **Attributes**

     * p : instantaneous power production (kW)
     * duration : duration of the power delivery (hours)
     * mandatory : indicates if the power delivery is mandatory or not
     * energy_type : type of energy ('Electrical', 'Heat', ...)

    """

    def __init__(self, time, name, p_square, duration, n_square,
                 t_between_sq, co2_out=None, starting_cost=None,
                 operating_cost=None, energy_type=None,
                 verbose=True, no_warn=True):
        duration /= time.DT
        if duration < 1:
            raise ValueError('The duration of operation of the '
                             'SquareProductionUnit should be longer than the '
                             'time step.')
        VariableProductionUnit.__init__(self, time=time, name=name,
                                        verbose=verbose)
        SquareEnergyUnit.__init__(self, time, name=name, p_square=p_square,
                                  n_square=n_square, t_square=duration,
                                  t_between_sq=t_between_sq,
                                  flow_direction='out',
                                  starting_cost=starting_cost,
                                  operating_cost=operating_cost,
                                  co2_out=co2_out, energy_type=energy_type,
                                  verbose=False,
                                  no_warn=no_warn)


class ShiftableProductionUnit(ShiftableEnergyUnit, VariableProductionUnit):
    """
    **Description**

        Production unit with shiftable production profile.

    **Attributes**

     * power_values : production profile to shift (kW)
     * mandatory : indicates if the production is mandatory : True
       or not : False
     * starting_cost : cost of the starting of the production
     * operating_cost : cost of the operation (€/kW)
     * energy_type : type of energy ('Electrical', 'Heat', ...)

    """

    def __init__(self, time, name: str, power_values, mandatory=True,
                 co2_out=None, starting_cost=None, operating_cost=None,
                 energy_type=None, verbose=True):

        VariableProductionUnit.__init__(self, time=time, name=name,
                                        verbose=verbose)
        ShiftableEnergyUnit.__init__(self, time, name=name,
                                     flow_direction='out',
                                     power_values=power_values,
                                     mandatory=mandatory, co2_out=co2_out,
                                     starting_cost=starting_cost,
                                     operating_cost=operating_cost,
                                     energy_type=energy_type,
                                     verbose=False)
