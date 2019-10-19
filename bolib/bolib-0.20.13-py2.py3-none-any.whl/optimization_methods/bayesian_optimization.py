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

import gplib

from .random_grid import RandomGrid
from .sequential_optimization import SequentialOptimization


class BayesianOptimization(SequentialOptimization):
    """

    """
    def __init__(self, model, fitting_method, validation, af):
        """

        """

        self.orig_model = model
        self.fitting_method = fitting_method
        self.validation = validation
        self.af = af

        super(BayesianOptimization, self).__init__()

    def next_sample(self, data, bounds):
        """

        :param data:
        :type data:
        :param bounds:
        :type bounds:
        :return:
        :rtype:
        """
        transformation = gplib.dm.DataTransformation(
            {
                'X': np.array(bounds, dtype=np.float).T,
                'Y': data['Y']
            }
        )
        t_data = transformation.transform(data)
        t_bounds = [(0., 1.) for _ in range(len(bounds))]

        fit_log = self.fitting_method.fit(
            model=self.orig_model,
            folds=self.validation.get_folds(t_data),
        )
        model = self.orig_model.get_posterior(t_data)

        self.af.set_model(model)
        self.af.set_data(t_data)

        # TODO Use better optimization methods
        optimization_method = RandomGrid()

        # Send next sample to Evaluate
        result = spo.minimize(
            self.af.evaluate,
            None,
            bounds=t_bounds,
            method=optimization_method.minimize,
            options={
                'maxiter': 20000
            }
        )

        x_sel = transformation.transform_key(result.x, 'X', inv=True)
        af_sel = result.fun

        return x_sel, {
            'x_sel': x_sel,
            'af_sel': af_sel,
            'fit_log': fit_log
        }
