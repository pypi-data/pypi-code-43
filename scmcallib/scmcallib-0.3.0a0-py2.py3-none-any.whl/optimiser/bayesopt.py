import numpy as np
from bayes_opt import BayesianOptimization


from .base import BaseOptimiser


class OptimiserBayesOpt(BaseOptimiser):
    name = "bayesopt"

    def get_param_bounds(self, parameter_set, include_bounds):
        # TODO: put in utils?
        param_bounds = {}
        for name, p in parameter_set.tune_parameters.items():
            if not include_bounds:
                param_bounds[name] = (-np.inf, np.inf)
                continue

            samples = p.distribution.random(size=10000)
            best_guess = samples.mean()
            param_bounds[name] = (
                p.kwargs.get("lower", best_guess + (best_guess - samples.min()) * 1.05),
                p.kwargs.get("upper", best_guess - (best_guess - samples.max()) * 1.05),
            )

        return param_bounds

    def find_best_fit(
        self, evaluator, parameter_set, include_bounds=True, verbose=0, **kwargs
    ):
        kwargs.setdefault("init_points", 100)
        kwargs.setdefault("n_iter", 10)
        kwargs.setdefault("acq", "ei")
        kwargs.setdefault("xi", 0.02)

        param_bounds = self.get_param_bounds(parameter_set, include_bounds)

        bo = BayesianOptimization(f=evaluator, pbounds=param_bounds, verbose=verbose)

        bo.maximize(**kwargs)

        return self.process_minimisation_results(bo)

    def process_minimisation_results(self, bo):
        bo.x = bo.max["params"]
        # BayesOpt doesn't converge in the same sense I don't think, need to check
        # with Nick
        bo.success = True

        return bo
