from collections import Iterable
from datetime import datetime
from logging import getLogger

from dateutil import parser
from openscm.scmdataframe import ScmDataFrameBase

from scmcallib.scm import get_scm
from scmcallib.scm.base import BaseSCM
from scmcallib.utils import create_iam_dataframe, prepare_dataframe

logger = getLogger(__name__)


def _get_scm(scm, scm_kwargs, config_params):
    if isinstance(scm, BaseSCM):
        return scm

    scm_kwargs = {} if scm_kwargs is None else scm_kwargs
    return get_scm(scm)(**scm_kwargs, **config_params)


class BaseFinder(object):
    """Base class for the different methodologies for obtaining parameter sets to emulate a target timeseries

    Parameters
    ----------
    parameter_set :
        An instance of scmcallib.parameterset.ParameterSet which is used to define the constraints
        on the model. The free parameters will be updated to find the combination of parameters which best match the
        target data set using `set_target`.
    scm :
        The name of the SCM to generate parameters. Options are one of the following: ['ar5ir', 'magicc6',
        'magicc7']
    reference_period :
        A tuple of (start_year, end_year) or an integer representing the year to use as the
        reference period. All values used within the emulation are calculated as anomalies wrt this period. For tuples,
        is reference period is open, i.e. (2000, 2010) includes both 2000 and 2010 in the calculation of anomalies.
    scm_kwargs :
        A dictionary of kwargs to pass to the SCM instance

    """

    def __init__(self, parameter_set, reference_period=(2000, 2010)):
        self.parameter_set = parameter_set

        self._set_reference_period(reference_period)

        self.target = None
        self.extra_meta = None
        self.iter_over = tuple()
        self.iter_over_values = None

    def _set_reference_period(self, reference_period):
        if not isinstance(reference_period, Iterable):
            reference_period = (reference_period,)

        if len(reference_period) > 2:
            raise ValueError(
                "reference_period should be either one or two values which can be cast to a datetime"
            )

        def parse_datetime(v, first=True):
            if isinstance(v, datetime):
                return v
            elif isinstance(v, int):
                return datetime(v, 1, 1) if first else datetime(v, 12, 31)
            else:
                return parser.isoparse(v)

        if len(reference_period) == 2:
            self.reference_period = (
                parse_datetime(reference_period[0], first=True),
                parse_datetime(reference_period[1], first=False),
            )
        else:
            self.reference_period = (
                parse_datetime(reference_period[0], first=True),
                parse_datetime(reference_period[0], first=False),
            )

    def set_target(self, observed, iter_over=None, **kwargs):
        """Specify the target timeseries

        During optimisation the SCM output will be compared to these data.

        The ScmDataFrame must contain unique combinations of variable and regions. Other metadata are ignored, except in the case where
        `iter_over` is specified. In that case `observed` must contain unique combinations of 'variable', 'region' and the columns
        which are being iterated over.

        Parameters
        ----------
        observed : ScmDataFrame or arraylike
            Observational/model data to which the SCM should be calibrated. This can be an ScmDataFrame or an arraylike.
            If using an arraylike object, additional ``kwargs`` may be needed.
        iter_over: str or list of str:
            Specify which metadata values to iterate over allowing for multiple model configurations to be run per optimiser step.
        kwargs :
            Other options to convert an array to a ScmDataFrame. See ``create_iam_dataframe`` for available options.

        """
        if not isinstance(observed, ScmDataFrameBase):
            observed = create_iam_dataframe(observed, **kwargs)

        if iter_over is not None:
            iter_over = self.iter_over = (
                [iter_over] if isinstance(iter_over, str) else list(iter_over)
            )
            assert all([c in observed.meta for c in iter_over])

        df = prepare_dataframe(observed, self.iter_over)
        self.extra_meta = observed.meta.set_index(df.columns.names)
        if df.isna().any(axis=None):
            logger.warning("removing timesteps with NaN values from target")
            df = df.dropna()

        if iter_over:
            self.iter_over_values = observed.meta[iter_over].drop_duplicates()
            self.iter_over_values = self.iter_over_values.to_dict("records")
            logger.info("iterating over {} each fit".format(self.iter_over_values))
        ref_period = df.loc[slice(*self.reference_period)]

        if len(ref_period) == 0:
            raise ValueError(
                "No target values within the reference period. Check dates of the target timeseries"
            )
        ref_mean = ref_period.mean()
        if ref_mean.isna().any():
            raise ValueError(
                "NaN mean over the reference period. Check dates/values of the target timeseries"
            )
        self.target = df - ref_mean
