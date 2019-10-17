import scipy.optimize


from .base import BaseOptimiser
from ..distributions import Bound


class OptimiserScipy(BaseOptimiser):
    name = "scipy"

    def find_best_fit(self, evaluator, parameter_set, include_bounds=True, **kwargs):
        if "x0" in kwargs:
            x0 = kwargs.pop("x0")
        else:
            x0 = parameter_set.evaluate(1).iloc[0, :].to_dict()

        if include_bounds:
            bounds = []
            for name, p in parameter_set.tune_parameters.items():
                if isinstance(p, Bound):
                    bounds.append((p.kwargs.get("lower"), p.kwargs.get("upper")))
                else:
                    bounds.append((None, None))
            kwargs["bounds"] = bounds

        def scipy_evaluator(*args, **kwargs):
            # We want to maximise all metrics for consistency,
            # but scipy only has minimise
            return -evaluator(*args, **kwargs)

        minima = self.minimise(scipy_evaluator, parameter_set, x0, **kwargs)

        return self.process_minimisation_results(minima, parameter_set)

    def minimise(self, evaluator, parameter_set, x0, **kwargs):
        def run_function(x):
            param_dict = {n: v for n, v in zip(parameter_set.names, x)}

            return evaluator(**param_dict)

        return scipy.optimize.minimize(
            run_function, [x0[k] for k in parameter_set.names], **kwargs
        )

    def process_minimisation_results(self, res, parameter_set):
        coeffs = {k: res.x[i] for i, k in enumerate(parameter_set.names)}
        res.x = coeffs

        return res
