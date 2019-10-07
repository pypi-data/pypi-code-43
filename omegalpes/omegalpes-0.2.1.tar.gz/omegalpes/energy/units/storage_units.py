#! usr/bin/env python3
#  coding=utf-8 #

"""
**This module defines the storage units**

 The storage_units module defines various kinds of storage units with
 associated attributes and methods, from simple to specific ones.

 It includes :
    - StorageUnit : simple storage unit inheriting from EnergyUnit,
      with storage specific attributes. It includes the objective "minimize
      capacity".
    - Thermocline storage : a thermal storage that need to cycle (i.e.
      reach SOC_max) every period of Tcycle

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

from pulp import LpBinary

from .energy_units import VariableEnergyUnit
from ...general.optimisation.elements import DynamicConstraint, \
    ExternalConstraint, ExtDynConstraint, Constraint
from ...general.optimisation.elements import Objective
from ...general.optimisation.elements import Quantity

__docformat__ = "restructuredtext en"


class StorageUnit(VariableEnergyUnit):
    """
    **Description**

        Simple Storage unit

    **Attributes**

     * capacity (Quantity): maximal energy that can be stored
     * e (Quantity): energy at time t in the storage
     * set_soc_min (DynamicConstraint): constraining the energy to be
       above the value : soc_min*capacity
     * set_soc_max (DynamicConstraint): constraining the energy to be
       below the value : soc_max*capacity
     * pc (Quantity) : charging power
     * pd (Quantity) : discharging power
     * u_c (Quantity) : binary variable describing the charge of the
       storage unit : 0 : Not charging & 1 : charging
     * calc_e (DynamicConstraint) : energy calculation at time t ;
       relation power/energy
     * calc_p (DynamicConstraint) : power calculation at time t ; power
       flow equals charging power minus discharging power
     * on_off_stor (DynamicConstraint) : making u[t] matching with
       storage modes (on/off)
     * def_max_charging (DynamicConstraint) : defining the max charging
       power, avoiding charging and discharging at the same time
     * def_max_discharging (DynamicConstraint) : defining the max
       discharging power, avoiding charging and discharging at the same time
     * def_min_charging (DynamicConstraint) : defining the min charging
       power, avoiding charging and discharging at the same time
     * def_min_discharging (DynamicConstraint) : defining the min
       discharging power, avoiding charging and discharging at the same time
     * set_e_0 (ExternalConstraint) : set the energy state for t=0
     * e_f (Quantity) : energy in the storage at the end of the time
       horizon, i.e. after the last time step
     * e_f_min (Constraint) : e_f value is constrained above
       soc_min*capacity
     * e_f_max (Constraint) : e_f value is constrained below
       soc_max*capacity
     * set_e_f (Constraint) : when e_f is given, it is set in the
       same way the energy is, but after the last time step
     * calc_e_f (Constraint) : when e_f is not given,
       it is calculated in the same way the energy is, but after the last
       time step
     * ef_is_e0 (ExternalConstraint) : Imposing ef=e0 on the time period.
     * cycles (ExternalDynamicConstraint) : setting a cycle constraint
       e[t] = e[t+cycles/dt]

    """

    def __init__(self, time, name, pc_min=1e-5, pc_max=1e+5,
                 pd_min=1e-5, pd_max=1e+5, capacity=None, e_0=None,
                 e_f=None, soc_min=0, soc_max=1, eff_c=1, eff_d=1,
                 self_disch=0, self_disch_t=0, ef_is_e0=False, cycles=None,
                 energy_type=None):
        """
        :param time: TimeUnit describing the studied time period
        :param name: name of the storage unit
        :param pc_min: minimal charging power [kW]
        :param pc_max: maximal charging power [kW]
        :param pd_min: minimal discharging power [kW]
        :param pd_max: maximal discharging power [kW]
        :param capacity: maximal energy that can be stored [kWh]
        :param e_0: initial level of energy [kWh]
        :param e_f: final level of energy [kWh]
        :param soc_min: minimal state of charge [pu]
        :param soc_max: maximal state of charge [pu]
        :param eff_c: charging efficiency
        :param eff_d: discharging efficiency
        :param self_disch: part of the capacity that is self-discharging [pu/h]
        :param self_disch_t: part of the energy that is self-discharging [pu/h]
        :param ef_is_e0: binary describing whether the storage is working at
        constant energy during the entire time period (e_0=e_f) or not.
        :param cycles: number of hours between cycling (e[t] = e[t+cycles/dt]
        :param energy_type: energy type the storage unit is used with
        """

        VariableEnergyUnit.__init__(self, time, name, flow_direction='in',
                                    p_min=-pd_max, e_min=-1e+5, p_max=pc_max,
                                    energy_type=energy_type)

        # --- Checking the state of charge boundaries of the storage system ---
        if isinstance(soc_min, (float, int)) and isinstance(soc_max, (float,
                                                                      int)):
            if soc_min > soc_max:
                raise ValueError('You cannot have soc_min > soc_max')
            elif soc_min > 1 or soc_min < 0 or soc_max > 1 or soc_max < 0:
                raise ValueError('The soc_min and soc_max values are '
                                 'expressed as percentages of the capacity and '
                                 'must be set between 0 and 1')
        if soc_min is None or soc_max is None:
            raise ValueError('soc_min and soc_max should not be None')

        self.capacity = Quantity(name='capacity', unit='kWh', value=capacity,
                                 lb=0, vlen=1, parent=self)

        self.e = Quantity(name='e', opt=True,
                          description='energy at t in the storage',
                          unit='kWh', vlen=time.LEN,
                          lb=0, ub=capacity, parent=self)

        if isinstance(soc_min, (int, float)):
            self.set_soc_min = DynamicConstraint(
                exp_t='{0}_e[t] >= {1} * {0}_capacity'.format(self.name,
                                                              soc_min),
                name='set_soc_min', parent=self)

        elif isinstance(soc_min, list):
            self.set_soc_min = DynamicConstraint(
                exp_t='{0}_e[t] >= {1}[t] * {0}_capacity'.format(self.name,
                                                                 soc_min),
                name='set_soc_min', parent=self)

        if isinstance(soc_max, (int, float)):
            self.set_soc_max = DynamicConstraint(
                exp_t='{0}_e[t] <= {1} * {0}_capacity'.format(self.name,
                                                              soc_max),
                name='set_soc_max', parent=self)

        elif isinstance(soc_max, list):
            self.set_soc_max = DynamicConstraint(
                exp_t='{0}_e[t] <= {1}[t] * {0}_capacity'.format(self.name,
                                                                 soc_max),
                name='set_soc_max', parent=self)

        # --- Charging and discharging powers ---
        self.pc = Quantity(name='pc', opt=True, unit='kW', vlen=time.LEN, lb=0,
                           ub=pc_max,
                           parent=self)
        self.pd = Quantity(name='pd', opt=True, unit='kW', vlen=time.LEN, lb=0,
                           ub=pd_max,
                           parent=self)

        self.uc = Quantity(name="uc", vtype=LpBinary, vlen=time.LEN, opt=True,
                           description='binary variable 0:No charging & '
                                       '1:charging',
                           parent=self)

        # CONSTRAINTS
        # Relation power/energy
        if 0 <= self_disch <= 1 and 0 <= self_disch_t <= 1:
            self.calc_e = \
                DynamicConstraint(name='calc_e',
                                  t_range=' for t in time.I[:-1]',
                                  exp_t='{0}_e[t+1] - {0}_e[t]*(1-{1}*time.DT)'
                                        ' - time.DT * ({0}_pc[t]*{3}- '
                                        '{0}_pd[t]*1/{4}- {2}*'
                                        '{0}_capacity) == 0'
                                  .format(self.name, self_disch_t, self_disch,
                                          eff_c, eff_d), parent=self)

        else:
            raise ValueError('self_disch & self_disch_t should have values '
                             'between 0 and 1 and are set to {0} and {1}'
                             .format(self_disch, self_disch_t))

        # Power flow equals charging power minus discharging power
        self.calc_p = DynamicConstraint(
            exp_t='{0}_p[t] == {0}_pc[t] - {0}_pd[t]'.format(self.name),
            t_range='for t in time.I', name='calc_p', parent=self)

        # For storage, as the power can be both positive and negative,
        # an other constraint is needed to make u[t] match with on/off
        self.on_off_stor = DynamicConstraint(
            exp_t='{0}_pc[t] + {0}_pd[t] - {0}_u[t] * {eps}'
                  ' >= 0'.format(self.name, eps=0.001),
            t_range='for t in time.I',
            name='on_off_stor', parent=self)

        # Limits to avoid charging and discharging at the same time
        self.def_max_charging = DynamicConstraint(
            exp_t='{0}_pc[t] - {0}_uc[t] * {1} <= 0'.format(self.name, pc_max),
            t_range='for t in time.I',
            name='def_max_charging', parent=self)

        self.def_max_discharging = DynamicConstraint(
            exp_t='{0}_pd[t] - (1 - {0}_uc[t]) * {1} <= 0'.format(self.name,
                                                                  pd_max),
            t_range='for t in time.I',
            name='def_max_discharging', parent=self)

        self.def_min_charging = DynamicConstraint(
            exp_t='{0}_pc[t] - {0}_uc[t] * {1} >= 0'.format(self.name, pc_min),
            t_range='for t in time.I',
            name='def_min_charging', parent=self)

        self.def_min_discharging = DynamicConstraint(
            exp_t='{0}_pd[t] + ({0}_uc[t] - {0}_u[t]) * {1} '
                  '>= 0'.format(self.name, pd_min), t_range='for t in time.I',
            name='def_min_discharging', parent=self)

        # --- Constraints for initial and final states of charge ---
        # Setting the state of charge for t=0
        if e_0 is not None:
            self.set_e_0 = ExternalConstraint(name='set_e_0',
                                              exp='{0}_e[0] == {1}'
                                              .format(self.name, e_0),
                                              parent=self)

        # e_f should be in between the boundaries
        # [soc_min*capacity; soc_max*capacity]
        # (even when the capacity is not defined), and the result of the
        # last charging/ discharging powers and losses applied the energy at
        # the last timestep.
        if e_f is not None:
            self.e_f = Quantity(name='e_f', opt=False, value=e_f,
                                description='energy in the storage at the '
                                            'end of the time horizon, i.e.'
                                            ' after the last time step',
                                unit='kWh', vlen=1, lb=0, ub=capacity,
                                parent=self)

            if isinstance(soc_min, (int, float)):
                self.e_f_min = Constraint(
                    exp='{0}_e_f >= {1} * {0}_capacity'.format(self.name,
                                                               soc_min),
                    name='e_f_min', parent=self)

            elif isinstance(soc_min, list):
                self.e_f_min = Constraint(
                    exp='{0}_e_f >= {1}[{2}] * {0}_capacity'.format(
                        self.name, soc_min, time.I[-1]),
                    name='set_soc_min', parent=self)

            if isinstance(soc_max, (int, float)):
                self.e_f_max = Constraint(
                    exp='{0}_e_f <= {1} * {0}_capacity'.format(self.name,
                                                               soc_max),
                    name='e_f_max', parent=self)

            elif isinstance(soc_max, list):
                self.e_f_max = Constraint(
                    exp='{0}_e_f <= {1}[{2}] * {0}_capacity'.format(
                        self.name, soc_max, time.I[-1]),
                    name='set_soc_max', parent=self)

            self.set_e_f = Constraint \
                (name='set_e_f',
                 exp='{0}_e_f-{0}_e[{1}] == {2}*({0}_pc[{1}]*{3}-'
                     '{0}_pd[{1}]*1/{4}-{5}*{0}_e[{1}]-{6}*{0}_capacity)'
                 .format(self.name, time.I[-1], time.DT, eff_c,
                         eff_d, self_disch_t, self_disch), parent=self)
        else:
            self.e_f = Quantity(name='e_f', opt=True,
                                description='energy in the storage at the end '
                                            'of the time horizon, i.e. after '
                                            'the last time step', unit='kWh',
                                vlen=1, lb=0, ub=capacity, parent=self)
            if isinstance(soc_min, (int, float)):
                self.e_f_min = Constraint(
                    exp='{0}_e_f >= {1} * {0}_capacity'.format(self.name,
                                                               soc_min),
                    name='e_f_min', parent=self)

            elif isinstance(soc_min, list):
                self.e_f_min = Constraint(
                    exp='{0}_e_f >= {1}[{2}] * {0}_capacity'.format(
                        self.name, soc_min, time.I[-1]),
                    name='set_soc_min', parent=self)

            if isinstance(soc_max, (int, float)):
                self.e_f_max = Constraint(
                    exp='{0}_e_f <= {1} * {0}_capacity'.format(self.name,
                                                               soc_max),
                    name='e_f_max', parent=self)

            elif isinstance(soc_max, list):
                self.e_f_max = Constraint(
                    exp='{0}_e_f <= {1}[{2}] * {0}_capacity'.format(
                        self.name, soc_max, time.I[-1]),
                    name='set_soc_max', parent=self)

            # e_f calculation
            self.calc_e_f = Constraint \
                (name='calc_e_f',
                 exp='{0}_e_f-{0}_e[{1}] == {2}*({0}_pc[{1}]*{3}-'
                     '{0}_pd[{1}]*1/{4}-{5}*{0}_e[{1}]-{6}*{0}_capacity)'
                 .format(self.name, time.I[-1], time.DT, eff_c,
                         eff_d, self_disch_t, self_disch), parent=self)

        # Impose ef_is_e0 on the time period
        if ef_is_e0:
            if e_f is None or e_0 is None or e_f == e_0:
                self.ef_is_e0 = ExternalConstraint(
                    exp='{0}_e[0] == {0}_e_f'.format(self.name),
                    name='ef_is_e0', parent=self)
            else:
                raise ValueError('When ef_is_e0 is set to True, e_f OR e_0 '
                                 'should remain set to None')

        if cycles is not None:
            if type(cycles) == int:
                delta_t = cycles / time.DT
                self.set_cycles = ExtDynConstraint(
                    name='set_cycles',
                    exp_t='{0}_e[t] == {0}_e[t+{1}]'.format(self.name,
                                                            delta_t),
                    t_range='for t in time.I[:-{0}]'.format(delta_t),
                    parent=self)
            else:
                raise TypeError('cycles should be an integer : number of '
                                'hours between cycling (e[t] = e[t+cycles/dt]')

    # OBJECTIVES
    def minimize_capacity(self, weight=1):

        """
        :param weight: Weight coefficient for the objective
        """
        def_capacity = DynamicConstraint(exp_t='{0}_e[t] <= {0}_capacity'
                                         .format(self.name),
                                         t_range='for t in time.I',
                                         name='def_capacity', parent=self)

        min_capacity = Objective(name='min_capacity',
                                 exp='{0}_capacity'.format(self.name),
                                 weight=weight,
                                 parent=self)

        setattr(self, 'def_capacity', def_capacity)
        setattr(self, 'min_capacity', min_capacity)


class ThermoclineStorage(StorageUnit):
    """
    **Description**

        Class ThermoclineStorage : class defining a thermocline heat storage,
        inheriting from StorageUnit.

    **Attributes**

        * is_soc_max (Quantity) : indicating if the storage is fully charged
          0:No 1:Yes
        * def_is_soc_max_inf (DynamicConstraint) : setting the right value
          for is_soc_max
        * def_is_soc_max_sup (DynamicConstraint) : setting the right value
          for is_soc_max
        * force_soc_max (ExtDynConstraint) : The energy has to be at least
          once at its maximal value during the period Tcycl.
    """

    def __init__(self, time, name, pc_min=1e-5, pc_max=1e+5,
                 pd_min=1e-5, pd_max=1e+5,
                 capacity=None, e_0=None, e_f=None, soc_min=0,
                 soc_max=1, eff_c=1, eff_d=1, self_disch=0, Tcycl=120,
                 ef_is_e0=False):
        """
        :param time: TimeUnit describing the studied time period
        :param name: name of the storage unit
        :param pc_min: minimal charging power [kW]
        :param pc_max: maximal charging power [kW]
        :param pd_min: minimal discharging power [kW]
        :param pd_max: maximal discharging power [kW]
        :param capacity: maximal energy that can be stored [kWh]
        :param e_0: initial level of energy [kWh]
        :param e_f: final level of energy [kWh]
        :param soc_min: minimal state of charge [pu]
        :param soc_max: maximal state of charge [pu]
        :param eff_c: charging efficiency
        :param eff_d: discharging efficiency
        :param self_disch: part of the soc that is self-discharging [pu]
        :param Tcycl: period over which the storage is cycling (reaching at
        least once it max state of charge) [hours]
        :param ef_is_e0: binary describing whether the storage is working at
        constant energy during the entire time period (e_0=e_f) or not.
        :param cycles: number of hours between cycling (e[t] = e[t+cycles/dt]
         """
        StorageUnit.__init__(self, time, name=name, pc_min=pc_min,
                             pc_max=pc_max, pd_min=pd_min, pd_max=pd_max,
                             capacity=capacity, e_0=e_0, e_f=e_f,
                             soc_min=soc_min, soc_max=soc_max, eff_c=eff_c,
                             eff_d=eff_d, self_disch=self_disch,
                             ef_is_e0=ef_is_e0, energy_type='Heat')

        # DECISION VARIABLES AND PARAMETERS
        # Creation of quantities needed for the Thermocline model
        self.is_soc_max = Quantity(name='is_soc_max', opt=True, vlen=time.LEN,
                                   vtype=LpBinary,
                                   description='indicates if the storage is '
                                               'fully charged 0:No 1:Yes',
                                   parent=self)

        # CONSTRAINTS
        # Thermocline constraints for charge and discharge
        # Set when we are at the maximal state of charge (soc_max) or not
        epsilon = 0.1

        self.def_is_soc_max_inf = DynamicConstraint(
            exp_t='{0}_capacity * {0}_is_soc_max[t] >= ({0}_e[t] - '
                  '{0}_capacity + {1})'.format(self.name, epsilon),
            t_range='for t in time.I', name='def_is_soc_max_inf', parent=self)

        self.def_is_soc_max_sup = DynamicConstraint(
            exp_t='{0}_capacity * {0}_is_soc_max[t] <= '
                  '{0}_e[t]'.format(self.name), t_range='for t in time.I',
            name='def_is_soc_max_sup', parent=self)

        # The soc has to be at least one time at soc_max during 5 days
        self.force_soc_max = ExtDynConstraint(
            exp_t='lpSum({0}_is_soc_max[k] for k in range(t-{1}+1, t)) '
                  '>= 1'.format(self.name, round(Tcycl / time.DT)),
            t_range='for t in time.I[{0}:]'.format(round(Tcycl / time.DT)),
            name='force_soc_max', parent=self)
