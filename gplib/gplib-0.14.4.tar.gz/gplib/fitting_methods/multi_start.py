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
from ..parameters.parameter import Parameter


class MultiStart(FittingMethod):
    """

    """

    def __init__(self, obj_fun, max_fun_call=500, group=None,
                 nested_fit_method=None):

        self.obj_fun = obj_fun
        self.group = Parameter.OPT_GROUP
        if group is not None:
            self.group = group
        self.nested_fit_method = nested_fit_method
        self.max_fun_call = max_fun_call

    def fit(self, model, folds, budget=None, verbose=False):
        """

        :param model:
        :type model:
        :param folds:
        :type folds:
        :param budget:
        :type budget:
        :param verbose:
        :type verbose:
        :return:
        :rtype:
        """
        if budget is None or self.max_fun_call < budget:
            max_fun_call = self.max_fun_call
        else:
            max_fun_call = budget

        start = time.time()

        log = {
            'fun_calls': 0,
            'improvements': 0,
            'restarts': 0,
            'time': 0,
            'best': {
                'params': model.get_param_values(
                    trans=False
                ),
                'value': np.inf,
                'fun_call': 0,
                'nested': None
            }
        }

        param_grid = model.get_grid(
            limit=max_fun_call,
            only_group=self.group,
            trans=True
        )
        current_opt_params = np.array(model.get_param_values(
            only_group=self.group,
            trans=True
        ))
        best_opt_params = current_opt_params

        while log['fun_calls'] < max_fun_call:
            # run optimization
            value = np.inf
            model.set_param_values(
                current_opt_params,
                only_group=self.group,
                trans=True
            )
            log['fun_calls'] += 1
            try:
                if self.nested_fit_method is not None:
                    nested_log = self.nested_fit_method.fit(
                        model,
                        folds,
                        budget=(max_fun_call - log['fun_calls']),
                        verbose=verbose
                    )
                    log['fun_calls'] += (nested_log['fun_calls'] - 1)
                    value = nested_log['best']['value']
                else:
                    value = self.obj_fun(
                        model=model,
                        folds=folds,
                        grad_needed=False
                    )
            except (AssertionError, np.linalg.linalg.LinAlgError) as ex:
                if verbose:
                    print(ex)

            log['restarts'] += 1
            if value < log['best']['value']:
                log['improvements'] += 1
                log['best']['params'] = model.get_param_values(
                    trans=False
                )
                best_opt_params = model.get_param_values(
                    only_group=self.group,
                    trans=True
                )
                log['best']['value'] = value
                log['best']['fun_call'] = log['fun_calls']
                if self.nested_fit_method is not None:
                    log['best']['nested'] = {
                        'name': self.nested_fit_method.__class__.__name__,
                        'fun_calls': nested_log['fun_calls'],
                        'improvements': nested_log['improvements'],
                        'restarts': nested_log['restarts'],
                        'time': nested_log['time'],
                        'best_fun_call': nested_log['best']['fun_call'],
                        'nested': nested_log['best']['nested']
                    }

            if len(param_grid) < 1:
                break

            if np.random.uniform() < 0.1:
                current_opt_params = np.array(
                    param_grid[np.random.randint(len(param_grid))]
                )
                jitter_sd = 10.
            else:
                current_opt_params = np.array(best_opt_params)
                jitter_sd = 1.
            current_opt_params += np.random.normal(
                loc=0.0,
                scale=jitter_sd,
                size=len(current_opt_params)
            )

        end = time.time()

        log['time'] = end - start

        assert log['best']['fun_call'], "No params were found"

        model.set_param_values(
            log['best']['params'],
            trans=False
        )

        return log
