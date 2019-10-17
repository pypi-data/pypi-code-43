from logging import getLogger

import numpy as np
import pymc3 as pm
import theano.tensor as tt

from scmcallib.finder.base import BaseFinder
from scmcallib.utils import prepare_dataframe

logger = getLogger(__name__)


class PyMC3Runner(tt.Op):
    """Runner class which is compatible with pymc3.

    We build a wrapper to define our magicc call as a theano operator.
    This is because pymc3 builds on theano operators, it only understands these. See here
    http://deeplearning.net/software/theano/sandbox/how_to_make_ops.html and https://docs.pymc.io/advanced_theano.html
    """

    otypes = [tt.dvector]

    def __init__(self, calibrator, parameters):
        self.calibrator = calibrator
        self.parameters = parameters
        self.itypes = [p.type for p in parameters]

    def perform(self, node, inputs, outputs):
        """the method that is used when calling the Op"""

        # Extract the params and their values
        params = {n.name: float(i) for n, i in zip(node.inputs, inputs)}

        # Run SCM
        scm_outputs = self.get_scm_values(params)
        outputs[0][0] = np.array(scm_outputs)  # output the log-likelihood

    def __call__(self, *args, **kwargs):
        # Expand out the parameters

        return super(PyMC3Runner, self).__call__(*self.parameters)

    def get_scm_values(self, params):
        """Call the SCM and process the results.

        These results are compared against the target timeseries to determine the likelihood

        Parameters
        ----------
        params : dict of parameters to pass to the scm


        Returns
        -------
        pd.Series

        """
        params.update(self.calibrator.parameter_set.config_parameters)
        try:
            results = self.calibrator.scm.run(params)
        except ValueError:
            # Skip this parameter combination
            logger.exception("Could not run scm")
            return np.inf
        results = prepare_dataframe(results)

        # We need to make sure that the ordering is correct. Both dfs are first reindexed using the same index,
        # which is the intersection of the two indices. Then the columns from the target are extracted from the
        # modelled timeseries (maintaining order). A KeyError is raised if the modelled timeseries doesn't
        # have a column specified in the target timeseries
        target = self.calibrator.target
        ts = results.loc[target.index]
        ts -= ts.loc[slice(*self.calibrator.reference_period)].mean()

        # TODO: use filtering from point_estimate

        return ts[target.columns].values.ravel()


class DistributionFinder(BaseFinder):
    """Calibrates a model to give a posterior distribution set of parameters

    This class provides a wrapper to help calibrate a SCM to observation/model data using Monte Carlo Markov Chains (MCMCs).
     An example of setting up a model to calibrate MAGICC7 to global mean temperature observations. Note that calibration
     is slow, requiring many 1000 runs of the SCM.


    Examples
    --------

    .. code-block:: python

        from scmcallib import ParameterSet, DistributionFinder, Normal
        from scmcallib.scm import AR5IR_SCM

        param_set = ParameterSet()
        param_set.set('a1', Normal(mu=1.5, sd=0.1))

        with AR5IR() as scm:
            calibrator = DistributionFinder(param_set, scm=scm)
            calibrator.set_target(observed=observed_gmt)

            results = calibrator.sample(draws=100, tune=50, chains=4)


    Attributes
    ----------
    sampler: pymc3.Model
        The underlying pymc3 model which performs the calibration

    """

    def __init__(self, parameter_set, scm, **kwargs):
        super(DistributionFinder, self).__init__(parameter_set, **kwargs)
        self.scm = scm
        self._runner = None
        self.trace = None

        self.sampler = self.get_sampler()

    def get_sampler(self):
        """Get the pymc3 sampler (model in pymc3 speak) for self's parameter set

        Returns
        -------
        pymc3.Model
            Model created from the parameters and their distributions from ``self.parameter_set``
        """
        # model = pm.Model(theano_config={'compute_test_value': 'off'})
        with pm.Model() as pymc3_model:
            for name, prior in self.parameter_set.tune_parameters.items():
                pymc3_model.Var(name, prior.to_pymc3())

        return pymc3_model

    def sample(self, **kwargs):
        """Sample the posterior

        Any additional arguments are passed onto `pymc3.sample`

        Parameters
        ----------
        kwargs :
            Additional arguments to pass to pymc3.sample.

        Returns
        -------
        pymc3.backends.base.MultiTrace
            TODO: Refactor to a scmcallib results object

        """
        with self.sampler:
            self.trace = pm.sample(**kwargs)

        return self.trace

    def plot(self):
        if self.trace is None:
            raise ValueError("Distribution has not been sampled yet")

        pm.traceplot(self.trace)

    def set_target(self, observed, distribution=pm.Normal, df_kwargs=None, **kwargs):
        """Define the observational data to be modelled

        Parameters
        ----------
        observed :
            Observational/model data to which the SCM should be calibrated
        distribution :
            The pymc3 Distribution which models the uncertainties of the observations. Should typically be pymc3.Normal.
            (Default value = pm.Normal)
        df_kwargs :
            Options to pass to ``create_iam_dataframe`` if using arraylike values for ``observed``. (Default value = None)
        kwargs :
            Other options to pass to the pymc3 distribution
        """
        df_kwargs = {} if df_kwargs is None else df_kwargs

        if "iter_over" in df_kwargs or "iter_over" in kwargs:
            raise NotImplementedError(
                "iter_over for DistributionFinder.set_target not implemented"
            )

        super(DistributionFinder, self).set_target(observed, **df_kwargs)

        if not issubclass(distribution, pm.Distribution):
            raise ValueError("distribution must be a subclass of pm.Distribution")

        if "mu" in kwargs:
            raise ValueError("Cannot pass a value for mu to DistributionFinder.runner")

        self._runner = PyMC3Runner(
            calibrator=self, parameters=self.sampler.deterministics
        )
        self.sampler.Var(
            "output",
            distribution.dist(mu=self._runner(), **kwargs),
            data=observed.values.ravel(),
        )

    def summary(self):
        return pm.summary(self.trace)
