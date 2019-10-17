import numpy as np
import pymc3.distributions as pm_dists


class Distribution(object):
    """Statistical distribution

    Used as a base for describing the distributions used to describe the possible values of the input variables.

    These Distribution's can also be converted to pymc3 Distributions if the pymc3
    optimiser is used.

    Parameters
    ----------

    Returns
    -------

    """

    def __init__(self, *args, pymc3_distribution=None, **kwargs):
        self.pymc3_distribution = pymc3_distribution
        self.args = args
        self.kwargs = kwargs

        if self.pymc3_distribution is not None:
            self.distribution = self.to_pymc3()

    def __str__(self):
        r = self.distribution._repr_latex_()
        return r if r is not None else ""

    def __getattr__(self, item):
        if item in self.kwargs:
            return self.kwargs[item]

    def evaluate(self, n):
        return self.distribution.random(size=n)

    def to_pymc3(self):
        """Allows for the custom translation to pymc3

        Parameters
        ----------

        Returns
        -------
        pymc3.Distribution
            A pymc3 distrbution
        """
        if self.pymc3_distribution is None:
            raise NotImplementedError("Cannot convert to pymc3")
        return self.pymc3_distribution.dist(*self.args, **self.kwargs)

    @classmethod
    def from_pymc3(cls, dist):
        """Distribution's created with this method will take the same parameters
        as their pymc3 equivalents

        Parameters
        ----------
        dist :
            A pymc3 distribution

        Returns
        -------
        type
            Factory for creating new instances of Distribution which wrap
            a pymc3 distribution

        """

        def create_dist(*args, **kwargs):
            return cls(*args, pymc3_distribution=dist, **kwargs)

        return create_dist


Scalar = Distribution.from_pymc3(pm_dists.Constant)
Normal = Distribution.from_pymc3(pm_dists.Normal)
LogNormal = Distribution.from_pymc3(pm_dists.Lognormal)
Uniform = Distribution.from_pymc3(pm_dists.Uniform)


class Bound(Distribution):
    def __init__(self, distribution, *args, **kwargs):
        # Extract the bounded distribution as it is handled slightly different
        self._bounded_dist = distribution
        super(Bound, self).__init__(*args, **kwargs)

        self.distribution = self.to_pymc3()

    def to_pymc3(self):
        if len(self._bounded_dist.args):
            raise ValueError(
                "Use kwargs for specifying parameters for bounded distributions"
            )
        bound = pm_dists.Bound(
            self._bounded_dist.distribution.__class__, *self.args, **self.kwargs
        )
        return bound.dist(**self._bounded_dist.kwargs)


class Function(Distribution):
    def evaluate(self, n):
        f = self.kwargs["function"]
        return np.array([f() for i in range(n)])
