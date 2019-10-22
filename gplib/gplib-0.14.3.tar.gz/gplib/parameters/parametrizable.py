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

import numpy as np

class Parametrizable(object):
    """

    """

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

        raise NotImplementedError("Not Implemented. This is an interface.")

    def get_param_values(self, only_group=None, trans=False):
        """

        :param only_group:
        :type only_group:
        :param trans:
        :type trans:
        :return:
        :rtype:
        """

        raise NotImplementedError("Not Implemented. This is an interface.")

    def get_param_bounds(self, only_group=None, trans=False):
        """

        :param only_group:
        :type only_group:
        :param trans:
        :type trans:
        :return:
        :rtype:
        """

        raise NotImplementedError("Not Implemented. This is an interface.")

    def get_def_params(self, only_group=None, trans=False):
        """

        :param only_group:
        :type only_group:
        :param trans:
        :type trans:
        :return:
        :rtype:
        """
        grid = self.get_grid(only_group=only_group, trans=trans)

        if len(grid) < 1:
            return []

        def_params = np.array(np.meshgrid(*grid))
        def_params = def_params.T.reshape(-1, len(grid))

        return def_params.tolist()

    def get_param_keys(self, recursive=True, only_group=None):
        """

        :param recursive:
        :type recursive:
        :param only_group:
        :type only_group:
        :return:
        :rtype:
        """

        raise NotImplementedError("Not Implemented. This is an interface.")

    def get_param_n(self, only_group=None):
        """

        :param only_group:
        :type only_group:
        :return:
        :rtype:
        """

        raise NotImplementedError("Not Implemented. This is an interface.")

    def get_grid(self, only_group=None, trans=False):
        """

        :param only_group:
        :type only_group:
        :param trans:
        :type trans:
        :return:
        :rtype:
        """

        raise NotImplementedError("Not Implemented. This is an interface.")
