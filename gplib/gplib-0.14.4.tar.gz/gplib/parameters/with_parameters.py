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


class WithParameters(Parametrizable):
    """

    """
    def __init__(self, hyperparameters):
        """

        :param hyperparameters:
        :type hyperparameters:
        """
        self.hyperparameters = hyperparameters

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

        assert (len(params) == self.get_param_n(
            only_group=only_group)),\
            "length of params is not correct"

        i = 0
        for hyperparameter in self.hyperparameters:
            number_of_params = \
                hyperparameter.get_param_n(only_group=only_group)
            param_slice = slice(i, i + number_of_params)
            hyperparameter.set_param_values(
                params[param_slice],
                only_group=only_group,
                trans=trans
            )
            i += number_of_params

    def get_param_values(self, only_group=None, trans=False):
        """

        :param only_group:
        :type only_group:
        :param trans:
        :type trans:
        :return:
        :rtype:
        """

        params = []
        for hyperparameter in self.hyperparameters:
            params += hyperparameter.get_param_values(
                only_group=only_group,
                trans=trans
            )

        return params

    def get_param_bounds(self, only_group=None, trans=False):
        """

        :param only_group:
        :type only_group:
        :param trans:
        :type trans:
        :return:
        :rtype:
        """

        bounds = []
        for hyperparameter in self.hyperparameters:
            bounds += hyperparameter.get_param_bounds(
                only_group=only_group,
                trans=trans
            )

        return bounds

    def get_param_keys(self, recursive=True, only_group=None):
        """

        :param recursive:
        :type recursive:
        :param only_group:
        :type only_group:
        :return:
        :rtype:
        """

        if not recursive:
            return self.__class__.__name__

        params = []

        for hyperparameter in self.hyperparameters:
            name = self.__class__.__name__
            params += [
                name + "_" + item for item in hyperparameter.get_param_keys(
                    only_group=only_group
                )
            ]

        return params

    def get_param_n(self, only_group=None):
        """

        :param only_group:
        :type only_group:
        :return:
        :rtype:
        """

        n_optimizable = 0

        for hyperparameter in self.hyperparameters:
            n_optimizable += hyperparameter.get_param_n(
                only_group=only_group
            )

        return n_optimizable

    def get_default_values(self, only_group=None, trans=False):
        """

        :param only_group:
        :type only_group:
        :param trans:
        :type trans:
        :return:
        :rtype:
        """

        grid = [
            grid
            for hyperparameter in self.hyperparameters
            for grid in hyperparameter.get_default_values(
                only_group=only_group,
                trans=trans
            )
        ]

        if len(grid) < 1:
            return []

        return grid

    def get_hyperparams(self):
        """

        :return:
        :rtype:
        """

        return self.hyperparameters

    def set_hyperparams(self, hyperparams):
        """

        :param hyperparams:
        :type hyperparams:
        :return:
        :rtype:
        """

        assert type(hyperparams) is list,\
            "hyperparams must be a list"
        self.hyperparameters = hyperparams

    def get_hyperparam(self, name):
        """

        :param name:
        :type name:
        :return:
        :rtype:
        """
        for hyperparameter in self.hyperparameters:
            hp_name = hyperparameter.get_param_keys(
                recursive=False,
                only_group=None
            )
            if name == hp_name:
                return hyperparameter

    def get_param_value(self, name):
        """

        :param name:
        :type name:
        :return:
        :rtype:
        """
        hyperparam = self.get_hyperparam(name)

        value = hyperparam.get_param_values(only_group=None)

        if hyperparam.is_array():
            return value

        return value[0]
