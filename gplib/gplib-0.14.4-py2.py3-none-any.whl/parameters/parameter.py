# -*- coding: utf-8 -*-
#
#    Copyright 2019 Ibai Roman
#
#    This file is part of GPlib.
#
#    GPlib is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    GPlib is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with GPlib. If not, see <http://www.gnu.org/licenses/>.

from .parametrizable import Parametrizable


class Parameter(Parametrizable):
    """

    """
    GRID_GROUP = 1
    OPT_GROUP = 2

    def __init__(self, name, transformation,
                 default_value, bounds=None):
        """

        :param name:
        :type name:
        :param transformation:
        :type transformation:
        :param default_value:
        :type default_value:
        :param bounds:
        :type bounds:
        """

        self.name = name
        self.transformation = transformation
        if hasattr(default_value, "__len__"):
            self.dims = len(default_value)
            self.array = self.dims > 1
            if hasattr(default_value[0], "__len__"):
                # default_value = [[1.], [1.], [1., 2.]]
                self.group = Parameter.GRID_GROUP
                self.current_value = [
                    default_value_i[0]
                    for default_value_i in default_value
                ]
                self.default_values = default_value
            else:
                # default_value = [1., 1., 1.]
                self.group = Parameter.OPT_GROUP
                self.current_value = default_value
                self.default_values = [[i] for i in default_value]
            if not self.array:
                self.current_value = self.current_value[0]
        else:
            # default_value = 1.
            self.group = Parameter.OPT_GROUP
            self.dims = 1
            self.array = False
            self.current_value = default_value
            self.default_values = [[default_value]]
        self.bounds = bounds
        if self.bounds is None:
            self.bounds = self.transformation.get_def_bounds()

    def set_param_values(self, params, only_group=None, trans=False):
        """

        :param params:
        :type params:
        :param only_group:
        :type only_group:
        :param trans:
        :type trans:
        :return:
        :rtype:
        """
        if only_group is not None and only_group != self.group:
            return

        assert len(params) == self.dims, \
            "length of {} is not correct".format(self.name)

        if trans:
            if self.array:
                params = self.transformation.inv_trans(params).tolist()
            else:
                params = self.transformation.inv_trans(params)

        if self.array:
            self.current_value = params
        else:
            self.current_value = params[0]

    def get_param_values(self, only_group=None, trans=False):
        """

        :param only_group:
        :type only_group:
        :param trans:
        :type trans:
        :return:
        :rtype:
        """
        if only_group is not None and only_group != self.group:
            return []

        assert self.current_value is not None, \
            "{} has not been initialized".format(self.name)

        current_value = self.current_value
        if trans:
            current_value = self.transformation.trans(current_value)
            if self.array:
                current_value = current_value.tolist()

        if self.array:
            return current_value
        return [current_value]

    def get_param_bounds(self, only_group=None, trans=False):
        """

        :param only_group:
        :type only_group:
        :param trans:
        :type trans:
        :return:
        :rtype:
        """
        if only_group is not None and only_group != self.group:
            return []

        current_bounds = self.bounds
        if trans:
            current_bounds = tuple(
                self.transformation.trans(bound)
                for bound in current_bounds
            )

        return [current_bounds] * self.dims

    def get_param_keys(self, recursive=True, only_group=None):
        """

        :param recursive:
        :type recursive:
        :param only_group:
        :type only_group:
        :return:
        :rtype:
        """

        if only_group is not None and only_group != self.group:
            return []

        if not recursive:
            return self.name

        if self.dims == 1:
            return [self.name]

        return [
            "{}_d{}".format(self.name, dim) for dim in range(self.dims)
        ]

    def get_param_n(self, only_group=None):
        """

        :param only_group:
        :type only_group:
        :return:
        :rtype:
        """
        if only_group is not None and only_group != self.group:
            return 0

        return self.dims

    def get_default_values(self, only_group=None, trans=False):
        """

        :param only_group:
        :type only_group:
        :param trans:
        :type trans:
        :return:
        :rtype:
        """
        if only_group is not None and only_group != self.group:
            return []

        default_values = self.default_values
        if trans:
            default_values = [
                self.transformation.trans(element).tolist()
                for element in default_values
            ]

        return default_values

    def get_group(self):
        """

        :return:
        :rtype:
        """
        return self.group

    def is_array(self):
        """

        :return:
        :rtype:
        """
        return self.array

    def grad_trans(self, df):
        """

        :param df:
        :type df:
        :return:
        :rtype:
        """

        return self.transformation.grad_trans(self.current_value, df)
