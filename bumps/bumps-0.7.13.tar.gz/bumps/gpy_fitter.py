import numpy as np

try:
    import GPy
except ImportError:
    GPy = None

from . import fitters
from .fitters import MonitorRunner
from . import lsqerror

def _make_GPy_param(label, value, bounds):
    container = np.array([value], 'd')
    param = Gpy.Param(label, value)
    param.constrain_bounded(*bounds)
    return param

# TODO: proper support for parameter priors
def GPy_model(problem):
    """
    Wrap the Bumps problem as a GPy model
    """
    labels = problem.labels()
    values = problem.getp()
    bounds = problem.bounds()
    pars = [_make_GPy_param(label, value, range)
            for label, value, range in zip(labels, values, bounds)]
    class WrappedModel(Gpy.Model):
        def __init__(self):
            super(WrappedModel, self).__init__(name=problem.name)
            for p in pars:
                self.add_parameter(p)
        def log_likelihood(self):
            return -self.problem.nllf()
        def parameters_changed(self):
            problem.setp([par[0] for par in pars])
            for par, g in zip(pars, lsqerror.gradient(problem)):
                par.gradient[0] = g

# TODO: provide function to wrap GPy problem as a bumps model

class GPyFit(fitters.FitBase):
    name = "Gaussian-Process"
    id = "gp"
    settings = [('steps', 200)]

    def solve(self, monitors=None, mapper=None, **options):
        options = fitters._fill_defaults(options, self.settings)
        model = GPy_model(self.problem)
        self._update = MonitorRunner(problem=self.problem,
                                     monitors=monitors)
        model.optimize()
        #x = model.
        #x, fx, _ = snobfit(self.problem, self.problem.getp(),
        #                   self.problem.bounds(),
        #                   fglob=0, callback=self._monitor)
        return x, fx

    def _monitor(self, k, x, fx, improved):
        # TODO: snobfit does have a population...
        self._update(step=k, point=x, value=fx,
                     population_points=[x], population_values=[fx])

if GPy is not None:
    fitters.register()