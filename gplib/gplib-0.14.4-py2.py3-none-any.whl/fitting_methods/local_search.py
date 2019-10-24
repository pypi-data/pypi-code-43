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
import scipy.optimize as spo

from .fitting_method import FittingMethod
from ..parameters.parameter import Parameter


class LocalSearch(FittingMethod):
    """

    """
    def __init__(self, obj_fun, method="Powell", max_fun_call=500, group=None,
                 nested_fit_method=None):

        self.obj_fun = obj_fun
        self.group = Parameter.OPT_GROUP
        if group is not None:
            self.group = group
        self.nested_fit_method = nested_fit_method
        self.max_fun_call = max_fun_call

        if method in ["Newton-CG", "dogleg", "trust-ncg"]:
            raise NotImplementedError("Hessian not implemented for {}".format(
                method
            ))
        self.grad_needed = method in [
            "CG", "BFGS", "Newton-CG", "L-BFGS-B",
            "TNC", "SLSQP", "dogleg", "trust-ncg"
        ]
        self.bounded_search = method in [
            "L-BFGS-B", "TNC", "SLSQP"
        ]
        self.method = method

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

        def measurement_wrapper(opt_params):
            """
            measurement wrapper to optimize hyperparameters

            :param opt_params:
            :type opt_params:
            :return:
            :rtype:
            """
            assert log['fun_calls'] < max_fun_call,\
                "Funcall limit reached"

            model.set_param_values(
                opt_params,
                only_group=self.group,
                trans=True
            )
            log['fun_calls'] += 1
            if self.nested_fit_method is not None:
                nested_log = self.nested_fit_method.fit(
                    model,
                    folds,
                    budget=(max_fun_call - log['fun_calls']),
                    verbose=verbose
                )
                log['fun_calls'] += (nested_log['fun_calls'] - 1)
                result = nested_log['best']['value']
            else:
                result = self.obj_fun(
                    model=model,
                    folds=folds,
                    grad_needed=self.grad_needed
                )
            if self.grad_needed:
                value, gradient = result
            else:
                value = result

            if value < log['best']['value']:
                log['improvements'] += 1
                log['best']['params'] = model.get_param_values(
                    trans=False
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

            if self.grad_needed:
                return value, gradient

            return value

        method = self.method
        if self.method == "Powell":
            def mod_powell(fun, x0, args=(), **kwargs):
                """

                :return:
                :rtype:
                """
                rand_perm = np.random.permutation(len(x0))
                direc = np.eye(len(x0))
                direc = direc[rand_perm]

                spo.fmin_powell(fun, x0, args, disp=kwargs['disp'], direc=direc)
            method = mod_powell

        bounds = None
        if self.bounded_search:
            bounds = model.get_param_bounds(trans=True, only_group=self.group)

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

        current_opt_params = np.array(model.get_param_values(
            only_group=self.group,
            trans=True
        ))

        try:
            if model.get_param_n(only_group=self.group) < 1:
                measurement_wrapper(opt_params=current_opt_params)
            else:
                spo.minimize(
                    measurement_wrapper,
                    current_opt_params, method=method,
                    jac=self.grad_needed, bounds=bounds,
                    options={
                        'disp': False
                    }
                )
        except (AssertionError, np.linalg.linalg.LinAlgError) as ex:
            if verbose:
                print(ex)

        end = time.time()

        log['time'] = end - start

        assert log['best']['fun_call'], "No params were found"

        model.set_param_values(
            log['best']['params'],
            trans=False
        )

        return log
