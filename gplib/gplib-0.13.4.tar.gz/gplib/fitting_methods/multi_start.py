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


class MultiStart(FittingMethod):
    """

    """

    def __init__(self, obj_fun, ls_method="Powell", max_fun_call=5000):

        if ls_method in ["Newton-CG", "dogleg", "trust-ncg"]:
            raise NotImplementedError("Hessian not implemented for {}".format(
                ls_method
            ))
        self.grad_needed = ls_method in [
            "CG", "BFGS", "Newton-CG", "L-BFGS-B",
            "TNC", "SLSQP", "dogleg", "trust-ncg"
        ]
        self.bounded_search = ls_method in [
            "L-BFGS-B", "TNC", "SLSQP"
        ]
        self.max_fun_call = max_fun_call
        self.max_ls_fun_call = int(max_fun_call * 0.9)
        self.ls_method = ls_method
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

        def measurement_wrapper(opt_params):
            """
            measurement wrapper to optimize hyperparameters

            :param opt_params:
            :type opt_params:
            :return:
            :rtype:
            """
            assert current['fun_calls'] < self.max_fun_call,\
                "Funcall limit reached"
            assert current['ls_fun_calls'] < self.max_ls_fun_call,\
                "LS Funcall limit reached"

            current['fun_calls'] += 1
            current['ls_fun_calls'] += 1

            model.set_param_values(
                opt_params,
                optimizable_only=True,
                trans=True
            )
            result = self.obj_fun(
                model=model,
                folds=folds,
                grad_needed=self.grad_needed
            )
            if self.grad_needed:
                value, gradient = result
            else:
                value = result

            if value < current['best']['value']:
                current['best']['params'] = model.get_param_values(
                    optimizable_only=False,
                    trans=False
                )
                current['best']['value'] = value
                current['best']['ls_fun_call'] = current['ls_fun_calls']
                current['best']['fun_call'] = current['fun_calls']
                current['best']['opt_params'] = opt_params.tolist()

            if self.grad_needed:
                return value, gradient

            return value

        ls_method = self.ls_method
        if self.ls_method == "Powell":
            def mod_powell(fun, x0, args=(), **kwargs):
                """

                :return:
                :rtype:
                """
                rand_perm = np.random.permutation(len(x0))
                direc = np.eye(len(x0))
                direc = direc[rand_perm]

                spo.fmin_powell(fun, x0, args, disp=kwargs['disp'], direc=direc)
            ls_method = mod_powell

        bounds = None
        if self.bounded_search:
            bounds = model.get_param_bounds(trans=True, optimizable_only=True)

        start = time.time()

        def_opt_params = np.array(model.get_def_params(
            optimizable_only=True,
            trans=True
        )[0])
        current_opt_params = np.array(model.get_param_values(
            optimizable_only=True,
            trans=True
        ))

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
                'opt_params': current_opt_params.tolist(),
                'restart': 0
            }
        }

        if model.get_param_n(optimizable_only=True) < 1:
            return log

        while log['fun_calls'] < self.max_fun_call:
            # run optimization
            current = {
                'fun_calls': log['fun_calls'],
                'ls_fun_calls': 0,
                'best': {
                    'params': model.get_param_values(
                        optimizable_only=False,
                        trans=False
                    ),
                    'value': np.inf,
                    'ls_fun_call': 0,
                    'fun_call': log['fun_calls'],
                    'opt_params': current_opt_params.tolist()
                }
            }
            try:
                spo.minimize(
                    measurement_wrapper,
                    current_opt_params, method=ls_method,
                    jac=self.grad_needed, bounds=bounds,
                    options={
                        'disp': False
                    }
                )
            except (AssertionError, np.linalg.linalg.LinAlgError) as ex:
                if verbose:
                    print(ex)

            log['fun_calls'] = current['fun_calls']
            log['restarts'] += 1
            if current['best']['value'] < log['best']['value']:
                log['improvements'] += 1
                log['best'] = current['best']
                log['best']['restart'] = log['restarts']

            if np.random.uniform() < 0.1:
                current_opt_params = def_opt_params
                jitter_sd = 10.
            else:
                current_opt_params = np.array(log['best']['opt_params'])
                jitter_sd = 1.
            current_opt_params += np.random.normal(
                loc=0.0,
                scale=jitter_sd,
                size=len(current_opt_params)
            )
            model.set_param_values(
                current_opt_params,
                optimizable_only=True,
                trans=True
            )

        end = time.time()

        log['time'] = end - start

        assert log['best']['fun_call'], "No params were found"

        model.set_param_values(
            log['best']['params'],
            optimizable_only=False,
            trans=False
        )

        return log
