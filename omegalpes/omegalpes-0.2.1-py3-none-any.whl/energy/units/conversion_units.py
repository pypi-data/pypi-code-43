#! usr/bin/env python3
#  -*- coding: utf-8 -*-

"""
**This module defines the conversion units, with at least a production unit
and a consumption unit and using one or several energy types**

The conversion_units module defines various classes of conversion units,
from generic to specific ones.

It includes :
 - ConversionUnit : simple conversion unit. It inherits from OptObject.
 - ElectricalToThermalConversionUnit : Electrical to thermal Conversion unit
   with an electricity consumption and a thermal production linked by and
   electrical to thermal ratio. It inherits from ConversionUnit
 - HeatPump : Simple Heat Pump with an electricity consumption, a heat
   production and a heat consumption. It has a theoretical coefficient of
   performance COP and inherits from ConversionUnit.

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

from .consumption_units import ConsumptionUnit, VariableConsumptionUnit
from .production_units import ProductionUnit, VariableProductionUnit
from ...general.optimisation.elements import Quantity, DynamicConstraint
from ...general.optimisation.core import OptObject

__docformat__ = "restructuredtext en"


class ConversionUnit(OptObject):
    """
    **Description**

        Simple Conversion unit

    **Attributes**

     * time : TimeUnit describing the studied time period
     * prod_units : list of the production units
     * cons_units : list of the consumption units
     * poles : dictionary of the poles of the conversion unit

    """

    def __init__(self, time, name, prod_units=None, cons_units=None,
                 verbose=True):
        OptObject.__init__(self, name=name, description='Conversion unit',
                           verbose=verbose)

        self.time = time
        self.prod_units = []  # Initialize an empty list for the
        # production units
        self.cons_units = []  # Initialize an empty list for the consumption
        # units
        self.poles = {}  # Initialize an empty dictionary for the poles

        # A conversion unit is created with at least a production unit and a
        # consumption unit
        if not prod_units:
            raise IndexError('You have to fill at least a production unit.')
        elif not isinstance(prod_units, list):
            raise TypeError('prod_units should be a list.')
        else:
            for prod_unit in prod_units:
                # prod_units should only contain ProductionUnit objects
                if not isinstance(prod_unit, ProductionUnit):
                    raise TypeError('The elements in prod_units have to be the'
                                    ' type "ProductionUnit".')
                else:
                    self._add_production_unit(prod_unit)

        if not cons_units:
            raise IndexError('You have to fill at least a consumption unit.')
        elif not isinstance(cons_units, list):
            raise TypeError('cons_units should be a list.')
        else:
            for cons_unit in cons_units:
                # cons_units should only contain ConsumptionUnit
                if not isinstance(cons_unit, ConsumptionUnit):
                    raise TypeError('The elements in cons_units have to be the'
                                    ' type "ConsumptionUnit".')
                else:
                    self._add_consumption_unit(cons_unit)

    def _add_production_unit(self, prod_unit):
        """
        :param prod_unit: production unit to be added to the
            production_units list
        """
        if prod_unit not in self.prod_units:
            poles_nb = len(self.poles)
            self.poles[poles_nb + 1] = prod_unit.poles[1]
            self.prod_units.append(prod_unit)
            prod_unit.parent = self
        else:
            print('Production unit {0} already in the production_units '
                  'list'.format(prod_unit.name))

    def _add_consumption_unit(self, cons_unit):
        """
        :param cons_unit: consumption unit to be added to the
            consumption_units list
        """
        if cons_unit not in self.cons_units:
            poles_nb = len(self.poles)
            self.poles[poles_nb + 1] = cons_unit.poles[1]
            self.cons_units.append(cons_unit)
            cons_unit.parent = self
        else:
            print('Consumption unit {0} already in the consumption_units '
                  'list'.format(cons_unit.name))


class ElectricalToThermalConversionUnit(ConversionUnit):
    """
    **Description**

        Electrical to thermal Conversion unit with an electricity consumption
        and a thermal production

    **Attributes**

     * thermal_production_unit : thermal production unit (thermal output)
     * elec_consumption_unit : electricity consumption unit (electrical
       input)
     * conversion : Dynamic Constraint linking the electrical input to
       the thermal output through the electrical to thermal ratio

    """

    def __init__(self, time, name, pmin_in_elec=1e-5, pmax_in_elec=1e+5,
                 p_in_elec=None, pmin_out_therm=1e-5, pmax_out_therm=1e+5,
                 p_out_therm=None, elec_to_therm_ratio=1,
                 verbose=True):
        """
        :param time: TimeUnit describing the studied time period
        :param name: name of the electrical to thermal conversion unit
        :param pmin_in_elec: minimal incoming electrical power
        :param pmax_in_elec: maximal incoming electrical power
        :param p_in_elec: power input for the electrical consumption unit
        :param pmin_out_therm: minimal power output (thermal)
        :param pmax_out_therm: maximal power output (thermal)
        :param p_out_therm: power output (thermal)
        :param elec_to_therm_ratio: electricity to thermal ratio <=1
        """

        if p_out_therm is None:
            self.thermal_production_unit = VariableProductionUnit(
                time, name + '_therm_prod', energy_type='Thermal',
                pmin=pmin_out_therm, pmax=pmax_out_therm,
                verbose=verbose)
        else:
            self.thermal_production_unit = ProductionUnit(
                time, name + '_therm_prod', energy_type='Thermal',
                p=p_out_therm, verbose=verbose)

        if p_in_elec is None:
            self.elec_consumption_unit = VariableConsumptionUnit(
                time, name + '_elec_cons', pmin=pmin_in_elec,
                pmax=pmax_in_elec, energy_type='Electrical',
                verbose=verbose)
        else:
            self.elec_consumption_unit = ConsumptionUnit(
                time, name + '_elec_cons', p=p_in_elec,
                energy_type='Electrical', verbose=verbose)

        ConversionUnit.__init__(self, time, name,
                                prod_units=[self.thermal_production_unit],
                                cons_units=[self.elec_consumption_unit])

        if isinstance(elec_to_therm_ratio, (int, float)):  # e2h_ratio is a
            # mean value
            if elec_to_therm_ratio <= 1:
                self.conversion = DynamicConstraint(
                    exp_t='{0}_p[t] == {1} * {2}_p[t]'.format(
                        self.thermal_production_unit.name,
                        elec_to_therm_ratio,
                        self.elec_consumption_unit.name),
                    t_range='for t in time.I', name='conversion', parent=self)
            else:
                raise ValueError('The elec_to_therm_ratio should be lower '
                                 'than 1 (therm_production<elec_consumption)')

        elif isinstance(elec_to_therm_ratio, list):  # e2h_ratio is a list of
            # values
            if len(elec_to_therm_ratio) == self.time.LEN:  # it must have the
                #  right size, i.e. the TimeUnit length.
                if all(e <= 1 for e in elec_to_therm_ratio):
                    self.conversion = DynamicConstraint(
                        exp_t='{0}_p[t] == {1}[t] * {2}_p[t]'.format(
                            self.thermal_production_unit.name,
                            elec_to_therm_ratio,
                            self.elec_consumption_unit.name),
                        t_range='for t in time.I', name='conversion',
                        parent=self)
                else:
                    raise ValueError('The elec_to_therm_ratio values should be '
                                     'lower than 1 (therm_production<elec_'
                                     'consumption)')
            else:
                raise IndexError('The length of the elec_to_therm_ratio '
                                 'vector should be of the same length as the '
                                 'TimeUnit of the studied period')

        elif isinstance(elec_to_therm_ratio, dict):  # e2h_ratio is a dict of
            # values
            if len(elec_to_therm_ratio) == self.time.LEN:
                if all(e <= 1 for e in elec_to_therm_ratio.values()):
                    self.conversion = DynamicConstraint(
                        exp_t='{0}_p[t] == {1}[t] * {2}_p[t]'.format(
                            self.thermal_production_unit.name,
                            elec_to_therm_ratio,
                            self.elec_consumption_unit.name),
                        t_range='for t in time.I', name='conversion',
                        parent=self)
                else:
                    raise ValueError('The elec_to_therm_ratio values should be '
                                     'lower than 1 (therm_production<elec_'
                                     'consumption)')
            else:
                raise IndexError('The length of the elec_to_therm_ratio '
                                 'dictionary should be of the same length as '
                                 'the TimeUnit of the studied period')
        else:
            raise TypeError(
                "Electricity to thermal ratio should be a mean value or a "
                "vector (list or dict) for each time period !")


class HeatPump(ConversionUnit):
    """
    **Description**

        Simple Heat Pump with an electricity consumption, a thermal production
        and a thermal consumption. It has a theoretical coefficient of
        performance COP and inherits from ConversionUnit.

    **Attributes**

     * thermal_production_unit : thermal production unit (condenser)
     * elec_consumption_unit : electricity consumption unit (electrical
       input)
     * thermal_consumption_unit : heay consumption unit (evaporator)
     * COP : Quantity describing the coefficient of performance of the
       heat pump
     * conversion : Dynamic Constraint linking the electrical input to
       the thermal output through the electrical to thermal ratio
     * power_flow : Dynamic constraint linking the thermal output to the
       electrical and thermal inputs in relation to the losses.

    """

    def __init__(self, time, name, pmin_in_elec=1e-5, pmax_in_elec=1e+5,
                 p_in_elec=None, pmin_in_therm=1e-5, pmax_in_therm=1e+5,
                 p_in_therm=None, pmin_out_therm=1e-5, pmax_out_therm=1e+5,
                 p_out_therm=None, cop=3, losses=0):
        """
        :param time: TimeUnit describing the studied time period
        :param name: name of the heat pump
        :param pmin_in_elec:  minimal incoming electrical power
        :param pmax_in_elec: maximal incoming electrical power
        :param p_in_elec: power input for the electrical consumption unit
        :param pmin_in_therm: minimal incoming thermal power
        :param pmax_in_therm: maximal incoming thermal power
        :param p_in_therm: power input for the thermal consumption unit
        :param pmin_out_therm: minimal power output (thermal)
        :param pmax_out_therm: maximal power output (thermal)
        :param p_out_therm: power output (thermal)
        :param cop: Coefficient Of Performance of the Heat Pump (cop>1)
        :param losses: losses as a percentage of thermal energy produced (p_out)
        """

        if p_out_therm is None:
            self.thermal_production_unit = VariableProductionUnit(
                time, name + '_therm_prod', energy_type='Thermal',
                pmin=pmin_out_therm, pmax=pmax_out_therm)
        else:
            self.thermal_production_unit = ProductionUnit(
                time, name + '_therm_prod', energy_type='Thermal',
                p=p_out_therm)

        if p_in_therm is None:
            self.thermal_consumption_unit = VariableConsumptionUnit(
                time, name + '_therm_cons', energy_type='Thermal',
                pmin=pmin_in_therm, pmax=pmax_in_therm)
        else:
            self.thermal_consumption_unit = ConsumptionUnit(
                time, name + '_therm_cons', energy_type='Thermal',
                p=p_in_therm)

        if p_in_elec is None:
            self.elec_consumption_unit = VariableConsumptionUnit(
                time, name + '_elec_cons', pmin=pmin_in_elec,
                pmax=pmax_in_elec, energy_type='Electrical')
        else:
            self.elec_consumption_unit = ConsumptionUnit(
                time, name, p=p_in_elec, energy_type='Electrical')

        ConversionUnit.__init__(self, time, name,
                                prod_units=[self.thermal_production_unit],
                                cons_units=[self.thermal_consumption_unit,
                                            self.elec_consumption_unit])

        self.COP = Quantity(name='COP', value=cop, parent=self)

        if isinstance(self.COP.value, (int, float)):  # The cop has a single
            #  value
            if self.COP.value >= 1:  # The cop value should be greater than 1
                self.conversion = DynamicConstraint(
                    exp_t='{0}_p[t] == {1} * {2}_p[t]'.format(
                        self.thermal_production_unit.name,
                        self.COP.value,
                        self.elec_consumption_unit.name),
                    t_range='for t in time.I', name='conversion', parent=self)

                self.power_flow = DynamicConstraint(
                    exp_t='{0}_p[t]*(1+{1}) == {2}_p[t] + {3}_p[t]'
                        .format(self.thermal_production_unit.name, losses,
                                self.thermal_consumption_unit.name,
                                self.elec_consumption_unit.name),
                    t_range='for t in time.I',
                    name='power_flow', parent=self)
            else:
                raise ValueError("The COP value should be greater than 1")

        elif isinstance(self.COP.value, list):  # The cop has a list of values
            if len(self.COP.value) == self.time.LEN:
                if all(c >= 1 for c in self.COP.value):
                    self.conversion = DynamicConstraint(
                        exp_t='{0}_p[t] == {1}[t] * {2}_p[t]'.format(
                            self.thermal_production_unit.name,
                            self.COP.value,
                            self.elec_consumption_unit.name),
                        t_range='for t in time.I', name='conversion',
                        parent=self)
                    self.power_flow = DynamicConstraint(
                        exp_t='{0}_p[t]*(1+{1}) == {2}_p[t] + {3}_p[t]'
                            .format(self.thermal_production_unit.name, losses,
                                    self.thermal_consumption_unit.name,
                                    self.elec_consumption_unit.name),
                        t_range='for t in time.I',
                        name='power_flow', parent=self)
                else:
                    raise ValueError("The COP values should be greater than 1")
            else:
                raise IndexError("The COP should have the same length as the "
                                 "studied time period")

        elif isinstance(self.COP.value, dict):  # The cop has a dict
            # referencing its values.
            if len(self.COP.value) == self.time.LEN:
                if all(c >= 1 for c in self.COP.value.values()):
                    self.conversion = DynamicConstraint(
                        exp_t='{0}_p[t] == {1}[t] * {2}_p[t]'.format(
                            self.thermal_production_unit.name,
                            self.COP.value,
                            self.elec_consumption_unit.name),
                        t_range='for t in time.I', name='conversion',
                        parent=self)
                    self.power_flow = DynamicConstraint(
                        exp_t='{0}_p[t]*(1+{1}) == {2}_p[t] + {3}_p[t]'
                            .format(self.thermal_production_unit.name, losses,
                                    self.thermal_consumption_unit.name,
                                    self.elec_consumption_unit.name),
                        t_range='for t in time.I',
                        name='power_flow', parent=self)
                else:
                    raise ValueError("The COP values should be greater than 1")
            else:
                raise IndexError("The COP should have the same length as the "
                                 "studied time period")
        else:
            raise TypeError(
                "The assigned cop should be a mean value or a vector "
                "(dict or list) over the studied time period !")
