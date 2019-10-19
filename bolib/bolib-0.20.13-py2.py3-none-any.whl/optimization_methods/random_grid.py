# -*- coding: utf-8 -*-
#
#    Copyright 2019 Ibai Roman
#
#    This file is part of BOlib.
#
#    BOlib is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    BOlib is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with BOlib. If not, see <http://www.gnu.org/licenses/>.

import numpy as np
import scipy.optimize as spo

from .optimization_method import OptimizationMethod


class RandomGrid(OptimizationMethod):
    """

    """

    def minimize(self, fun, x0, args=(),
                 bounds=(), maxiter=200,
                 x0_square_size=1e-05, x0_square_samples=0.1,
                 **unknown_options):
        """

        :param fun:
        :type fun:
        :param x0:
        :type x0:
        :param args:
        :type args:
        :param bounds:
        :type bounds:
        :param maxiter:
        :type maxiter:
        :param x0_square_size:
        :type x0_square_size:
        :param x0_square_samples:
        :type x0_square_samples:
        :param unknown_options:
        :type unknown_options:
        :return:
        :rtype:
        """

        # Sample more points around x0
        x_t1 = self.random_sample(
            bounds,
            int(maxiter * (1.0-x0_square_samples))
        )

        y_t1 = fun(x_t1)

        x0 = x_t1[np.argmin(y_t1), :]

        x_t2 = self.random_sample(
            [
                (
                    x0_i - (x0_square_size * (bounds_i[1]-bounds_i[0])),
                    x0_i + (x0_square_size * (bounds_i[1]-bounds_i[0]))
                )
                for x0_i, bounds_i in zip(x0, bounds)
            ],
            int(maxiter * x0_square_samples)
        )

        y_t2 = fun(x_t2)

        x_t = np.vstack((x_t1, x_t2))
        y_t = np.vstack((y_t1, y_t2))

        best = np.argmin(y_t)

        x_best = x_t[best, :][None, :]
        y_best = y_t[best, 0]

        return spo.OptimizeResult(
            fun=y_best,
            x=x_best,
            nit=1,
            nfev=maxiter,
            success=True
        )
