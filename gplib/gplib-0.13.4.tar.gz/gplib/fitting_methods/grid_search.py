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

import time

import numpy as np

from .fitting_method import FittingMethod


class GridSearch(FittingMethod):
    """

    """

    def __init__(self, obj_fun):

        self.obj_fun = obj_fun

    def fit(self, model, folds, verbose=False):
        """
        Optimize Hyperparameters

        :param model:
        :type model:
        :param folds:
        :type folds:
        :param verbose:
        :type verbose:
        :return:
        :rtype:
        """

        start = time.time()

        log = {
            'fun_calls': 0,
            'improvements': 0,
            'restarts': 0,
            'time': 0,
            'best': {
                'params': model.get_param_values(
                    optimizable_only=False,
                    trans=False
                ),
                'value': np.inf,
                'ls_fun_call': 0,
                'fun_call': 0,
                'opt_params': model.get_param_values(
                    optimizable_only=True,
                    trans=True
                ),
                'restart': 0
            }
        }

        for current_params in model.get_def_params(
                    optimizable_only=False,
                    trans=False
                ):
            # run optimization
            value = np.inf
            try:
                model.set_param_values(
                    current_params,
                    optimizable_only=False,
                    trans=False
                )
                value = self.obj_fun(
                    model=model,
                    folds=folds,
                    grad_needed=False
                )
            except (AssertionError, np.linalg.linalg.LinAlgError) as ex:
                if verbose:
                    print(ex)

            log['fun_calls'] += 1
            if value < log['best']['value']:
                log['improvements'] += 1
                log['best']['params'] = model.get_param_values(
                    optimizable_only=False,
                    trans=False
                )
                log['best']['value'] = value
                log['best']['ls_fun_call'] = 0
                log['best']['fun_call'] = log['fun_calls']
                log['best']['opt_params'] = model.get_param_values(
                    optimizable_only=True,
                    trans=True
                )
                log['best']['restart'] = log['restarts']

        end = time.time()

        log['time'] = end - start

        assert log['best']['fun_call'], "No params were found"

        model.set_param_values(
            log['best']['params'],
            optimizable_only=False,
            trans=False
        )

        return log
