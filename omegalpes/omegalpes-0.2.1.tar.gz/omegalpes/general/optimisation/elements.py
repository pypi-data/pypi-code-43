#! usr/bin/env python3
#  -*- coding: utf-8 -*-

"""
**This module includes the optimization elements (quantities, constraints and
objectives) formulated in LP or MILP**

 - Quantity : related to the decision variable or parameter
 - Constraint : related to the optimization problem constraints
 - Objective : related to the objective function

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

import datetime
from pulp import LpContinuous

__docformat__ = "restructuredtext en"


class Quantity:
    """
    **Description**

        Class that defines what is a quantity. A quantity can wether be a
        decision variable or a parameter, depending on the opt parameter

    **Attributes**

     - name (str) : the name of the quantity
     - description (str) :  a description of the meaning of the quantity
     - vtype (PuLP) : the variable type, depending on PuLP

        * LpBinary (binary variable)
        * LpInteger (integer variable)
        * LpContinuous (continuous variable)
     - vlen (int) : size of the variable
     - unit (str) : unit of the quantity
     - opt (binary)

        * True: this is an optimization variable
        * False: this is a constant - a parameter
     - value (float, list, dict) : value (unused if opt=True)
     - ub, lb : upper and lower bounds
     - parent (OptObject) : the quantity belongs to this unit

    .. note::
        Make sure that all the modifications on Quantity are made before
        adding the unit to the Model
    """

    def __init__(self, name="var0", opt=True, unit="s.u", vlen=None,
                 value=None, description="", vtype=LpContinuous,
                 lb=None, ub=None, parent=None):
        """

        :param name: (str) name of the quantity
        :param opt: (binary) optimisation parameter
        :param unit: (str) unit of the quantity
        :param vlen: (int) size of the quantity value
        :param value: (float, list or dict) value of the quantity
        :param description: (str) description of the quantity
        :param vtype: (type) the variable type according to PuLP
        :param lb: (float or int) : lower bound of the value of the quantity
        :param ub: (float or int) : upper bound of the value of the quantity
        :param parent: (OptObject) parent unit
        """

        self.name = name
        if vlen is None:
            try:
                vlen = len(value)
            except TypeError:
                vlen = 1

        if parent is None:
            print('Warning : Parent argument of {0} is None'.format(self.name))

        self.vlen = vlen
        self.description = description
        self.unit = unit
        self.lb = lb
        self.ub = ub
        self.vtype = vtype
        self.value = {}

        if not isinstance(vlen, int):
            raise TypeError('vlen should be of type int !')

        if isinstance(opt, bool):
            # The optimisation parameter is a boolean
            if isinstance(value, (int, float)):
                # The value is an int or a float
                self.opt = opt
                if value:
                    # If the value is not None, the opt parameter should be
                    # False
                    self.opt = False
                if vlen <= 1:
                    self.value = value
                else:
                    # vlen should be 1 for ints and floats values
                    raise ValueError(
                        'value\'s size is given as vlen = {0}, but the value '
                        'is actually a {1}'.format(vlen, type(value)))

            elif isinstance(value, list):
                # The value is a list
                if value:
                    # If value is not None, the opt parameter is a list of
                    # False
                    self.opt = []
                    for i in range(vlen):
                        self.opt.append(False)
                if len(value) == vlen:
                    self.value = value
                else:
                    # vlen should be the list length
                    raise ValueError(
                        'value\'s size ({0}) should be vlen ({1})'.format(
                            len(value), vlen))

            elif isinstance(value, dict):
                # The value is a dict
                if any(isinstance(n, int or float) for n in (list(
                        value.values()))):
                    # At least one value of the dict is specified
                    self.opt = {}
                    # The opt parameter is a dict of False
                    self.opt.update({i: False for i in list(value.keys())})
                    print('At least one value is specified in the dict '
                          'value : the opt parameter is set as a dict of '
                          'False with the value keys')
                else:
                    self.opt = {}
                    self.opt.update({i: opt for i in list(value.keys())})

                if len(value) == vlen:
                    self.value = value
                else:
                    # vlen should be the dict value size
                    raise ValueError(
                        'value\'s size ({0}) should be vlen ({1})'.format(
                            len(value), vlen))

            elif value is None:
                if not opt:
                    # The quantity should have a specified value if
                    # opt=False OR opt should be set to True if the Quantity
                    #  is a decision variable
                    raise Exception('If the Quantity.opt == False, '
                                    'Quantity.value cannot be None. '
                                    'Value is required, or opt must be set '
                                    'to True !')
                elif vlen >= 2:
                    # if opt=True, the value is given the default value 0,
                    # or a list of 0 if vlen>=2
                    self.opt = {i: opt for i in range(vlen)}
                    self.value = {i: 0 for i in range(vlen)}

                else:
                    self.opt = opt
                    self.value = 0

            else:
                # Value should be either an int, a float, a list, a dict or
                # None
                raise TypeError('Unknown type for argument \'value\'')

        elif isinstance(opt, (list, dict)):
            raise Exception('Not implemented yet...')

        else:
            # opt should be a boolean, a list or a dict
            raise TypeError('Unknown type for argument \'opt\'')

        self.parent = parent
        self._add_quantity_list()

    def __str__(self):
        # String special method
        return str(self.value)

    def __repr__(self):
        # Repr special method
        if isinstance(self.opt, bool):
            exp = '<OMEGALPES.general.optimisation.elements.Quantity : (' \
                  'name:\'{0}\', opt:{1}, vlen:{1})> \n'.format(self.name,
                                                                self.opt,
                                                                self.vlen)
        elif isinstance(self.opt, list):
            exp = '<OMEGALPES.general.optimisation.elements.Quantity : (' \
                  'name:\'{0}\', opt[0]:{1}, vlen:{2})> \n'.format(self.name,
                                                                   self.opt[0],
                                                                   self.vlen)

        elif isinstance(self.opt, dict):
            exp = '<OMEGALPES.general.optimisation.elements.Quantity : (' \
                  'name:\'{0}\', opt:{1}, vlen:{2})> \n'.format(self.name,
                                                                list(
                                                                    self.opt.values()),
                                                                self.vlen)
        return exp

    def __float__(self):
        # Special method float (only works for int and float values,
        # not list and dict ones)
        return float(self.value)

    def _add_quantity_list(self):
        if self.parent:
            if self not in self.parent._quantities_list:
                self.parent._quantities_list.append(self)
        else:
            Warning("the quantity {} should have a parent otherwise "
                    "the quantity won't be added to the parent "
                    "_quantities_list".format(self.name))


class Constraint:
    """
    **Description**

        Class that defines a constraint object

    **Attributes**

     - name: name of the constraint
     - description: a description of the constraint
     - active:
       False = non-active constraint;
       True = active constraint
     - exp: (str) : expression of the constraint
     - parent: (unit) : this constraint belongs to this unit

    .. note::
        Make sure that all the modifications on Constraints are made before
        adding the unit to the Model (OptimisationModel.addUnit()).

    """

    def __init__(self, exp, name='CST0', description='', active=True,
                 parent=None):
        """

        :param exp: (str) expression of the constraint
        :param name: (str) name of the constraint
        :param description: (str) description of the constrain
        :param active: (bool) is the constraint active or not
        :param parent: (OptObject) parent unit
        """
        self.name = name
        self.description = description
        self.exp = exp
        self.active = active
        self.parent = parent
        self._add_cst_list()

    def _add_cst_list(self):
        if self.parent:
            if self not in self.parent._constraints_list:
                self.parent._constraints_list.append(self)
        else:
            Warning("the constraint {} should have a parent otherwise "
                    "the constraint won't be added to the parent "
                    "_constraints_list".format(self.name))

    def _deactivate_constraint(self):
        """ An constraint can be deactivated in order to debug (only!)
        """
        self.active = False


class DynamicConstraint(Constraint):
    """
    **Description**

        Defining a constraint depending on the time.
        NB : Mandatory for PuLP
    """

    def __init__(self, exp_t, t_range='for t in time.I', name='DCST0',
                 description='dynamic constraint', active=True, parent=None):
        """

        :param exp_t (str): constraint expression time-dependant
        :param t_range (str): time range defining when the constraint is set
        :param name (str): name of the constraint
        :param description (str): description of the constraint
        :param active (bool): is the constraint activated or deactivated
        :param parent: unit containing the constraint
        """
        if t_range[0] == ' ':
            # If the t_range starts with an empty space, it is deleted
            t_range = t_range[1:]
        exp = exp_t + ' ' + t_range

        Constraint.__init__(self, exp, name, description, active, parent)

        self.exp_t = exp_t
        self.t_range = t_range


class ExternalConstraint(Constraint):
    """
    **Description**

        Defining a special type of constraint: the external constraint

         - This constraint does not translate a physical constraint
         - This constraint defines an external constraint, which could be
           relaxed

    """

    def __init__(self, exp, name='ExCST0', description='', active=True,
                 parent=None):
        Constraint.__init__(self, exp, name, description, active, parent)
        self._add_ext_cst_list()

    def _add_ext_cst_list(self):
        if self.parent:
            if self not in self.parent._external_constraints_list:
                self.parent._external_constraints_list.append(self)
            else:
                Warning("the external constraint {} should have a parent "
                        "otherwise the constraint won't be added to the parent "
                        "_external_constraints_list".format(self.name))

    def deactivate_constraint(self):
        """ An external constraint can be deactivated :
             - To compare scenarios
             - To try a less constrained problem
        """
        self.active = False


class ExtDynConstraint(DynamicConstraint, ExternalConstraint):
    """
    **Description**

        Defining a constraint both external and dynamic
        (see: DynamicConstraint, ExternalConstraint)
    """

    def __init__(self, exp_t, t_range='for t in time.I', name='EDCST0',
                 active=True, description='Non-physical and dynamic constraint',
                 parent=None):
        ExternalConstraint.__init__(self, exp='', name=name,
                                    description=description,
                                    active=active, parent=parent)
        DynamicConstraint.__init__(self, exp_t=exp_t, t_range=t_range,
                                   name=name,
                                   description=description, active=active,
                                   parent=parent)


class HourlyDynamicConstraint(DynamicConstraint):
    """
    **Description**

        Class that defines an dynamic contraint for a time range

        Ex: Constraint applying between 7am and 10pm

        ex_cst = HourlyDynamicConstraint(exp_t, time, init_h=7, final_h=22,
        name='ex_cst')

    **Attributes**

     - name (str) : name of the constraint
     - exp_t (str) : expression of the constraint
     - init_h (int) : hour of beginning of the constraint [0-23]
     - final_h (int) : hour of end of the constraint [1-24]
     - description (str) : description of the constraint
     - active (bool) : defines if the constraint is active or not
     - parent (OptObject) : parent of the constraint
    """

    def __init__(self, exp_t, time, init_h: int = 0, final_h: int = 24,
                 name='HDCST0', description='hourly dynamic constraint',
                 active=True, parent=None):

        if init_h > final_h:
            raise ValueError('final_h {0} should be greater than init_h '
                             '{1}'.format(final_h, init_h))
        if final_h > 24:
            raise ValueError('final_h {} should be lower than '
                             '24'.format(final_h))

        index_list = []  # Initializing the list of index

        # For all days in the time periods, select the hour range
        for day in time.get_days:
            starting_date = datetime.datetime(year=day.year, month=day.month,
                                              day=day.day, hour=init_h)

            if final_h == 24:
                end = day + datetime.timedelta(days=1)

            else:
                end = datetime.datetime(year=day.year, month=day.month,
                                        day=day.day, hour=final_h)

            try:
                index_date = time.get_index_for_date_range(
                    starting_date=starting_date, end=end)
                index_list += index_date

            except ValueError:
                pass  # Exception when no values for the last day for instance

        t_range = 'for t in {}'.format(index_list)

        DynamicConstraint.__init__(self, exp_t, t_range=t_range, name=name,
                                   description=description, active=active,
                                   parent=parent)


class Objective:
    """
     **Description**

        Class that defines an optimisation objective

     **Attributes**

      - name (str) :
      - description (str) :
      - active (bool) :
      - exp (str) :
      - weight (float) : weighted factor of the objective
      - parent (unit)
      - unit (str) : unit of the cost expression

     .. note::
        Make sure that all the modifications on Objectives are made before
        adding the unit to the OptimisationModel, otherwise, it won't be taken
        into account

     """

    def __init__(self, exp, name='OBJ0', description='', active=True, weight=1,
                 unit='s.u.', parent=None):
        self.name = name
        self.exp = exp
        self.description = description
        self.active = active
        self.weight = weight
        self.parent = parent
        self.unit = unit
        self._add_objective_list()

    def _add_objective_list(self):
        if self.parent:
            if self not in self.parent._objectives_list:
                self.parent._objectives_list.append(self)
        else:
            Warning("the objective {} should have a parent otherwise "
                    "the objective won't be added to the parent "
                    "_objectives_list".format(self.name))
