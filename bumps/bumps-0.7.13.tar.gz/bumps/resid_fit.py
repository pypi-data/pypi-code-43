import numpy as np
from .curve import _parse_pars, _assign_pars, _plot_resids

class Resid(object):
    """
    [Experimental]  provide a wrapper for functions that return a residual only.
    """
    def __init__(self, fn, name="", **kwargs):
        self.name = name # if name else fn.__name__ + " "
        self.labels = ["point", "residual", "residual"]

        pars, state = _parse_pars(fn, init=kwargs, skip=0, name=name)

        # Make parameters accessible as model attributes
        _assign_pars(self, pars)
        #_assign_pars(state, self)  # ... and state variables as well

        # Remember the function, parameters, and number of parameters
        # Note: we are remembering the parameter names and not the
        # parameters themselves so that the caller can tie parameters
        # together using model1.par = model2.par.  Otherwise we would
        # need to override __setattr__ to intercept assignment to the
        # parameter attributes and redirect them to the a _pars dictionary.
        # ... and similarly for state if we decide to make them attributes.
        self._function = fn
        self._pnames = list(sorted(pars.keys()))
        self._state = state
        self._cached_theory = None
        self._numpoints = None

    def update(self):
        self._cached_theory = None

    def parameters(self):
        return dict((p, getattr(self, p)) for p in self._pnames)

    def numpoints(self):
        # Note: don't know the number of points until we compute the residuals.
        # Can't get it from the length x since we don't have x.
        if self._numpoints is None:
            r = self.residuals()
            self._numpoints = np.prod(r.shape)
        return self._numpoints

    def residuals(self):
        if self._cached_theory is None:
            kw = dict((p, getattr(self, p).value) for p in self._pnames)
            kw.update(self._state)
            resid = self._function(**kw)
            self._cached_theory = resid
        return self._cached_theory

    def nllf(self):
        r = self.residuals()
        return 0.5 * np.sum(r ** 2)

    def save(self, basename):
        data = self.residuals()
        np.savetxt(basename + '.dat', data)

    def plot(self, view=None):
        from .plotutil import coordinated_colors

        colors = (coordinated_colors(),)
        resid = self.residuals()
        x = np.arange(1, len(resid)+1)
        _plot_resids(x, resid, colors=colors, labels=self.labels, view=view)
