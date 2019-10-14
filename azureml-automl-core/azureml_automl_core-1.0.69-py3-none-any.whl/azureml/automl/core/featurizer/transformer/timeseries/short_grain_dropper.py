# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Drop grains from dataset."""
import logging
import pandas as pd

from typing import Any, List, Optional, cast
from warnings import warn

from automl.client.core.common import utilities
from automl.client.core.common.forecasting_exception import NotTimeSeriesDataFrameException
from automl.client.core.common.logging_utilities import function_debug_log_wrapped
from automl.client.core.common.time_series_data_frame import TimeSeriesDataFrame
from .forecasting_base_estimator import AzureMLForecastTransformerBase
from automl.client.core.common.exceptions import ConfigException, DataException,\
    ClientException
from automl.client.core.runtime.types import GrainType
from automl.client.core.common.forecasting_verify import Messages
from automl.client.core.common.constants import TimeSeries, TimeSeriesInternal


class ShortGrainDropper(AzureMLForecastTransformerBase):
    """Drop short series, or series not found in training set."""

    DROPPING_GRAIN_TEMPL = ("Dropping grain {}. Reason: the grain was not present in the training set "
                            "or was too short.")

    def __init__(self, logger: Optional[logging.Logger] = None, **kwargs: Any) -> None:
        """
        Constructor.

        :param target_rolling_window_size: The size of a target rolling window.
        :param target_lags: The size of a lag of a lag operator.
        :param n_cross_validations: The number of cross validations.
        :param max_horizon: The maximal horizon.
        :raises: ConfigException
        """
        super().__init__()
        self._grains_to_keep = []  # type: List[GrainType]
        self._short_grains = []  # type: List[GrainType]
        self._window_size = kwargs.get(TimeSeries.TARGET_ROLLING_WINDOW_SIZE, 0)  # type: int
        self._lags = kwargs.get(TimeSeries.TARGET_LAGS, [0])  # type: List[int]
        self._cv = kwargs.get(TimeSeriesInternal.CROSS_VALIDATIONS)  # type: Optional[int]
        self._max_horizon = kwargs.get(TimeSeries.MAX_HORIZON, TimeSeriesInternal.MAX_HORIZON_DEFAULT)  # type: int
        self._is_fit = False
        self._init_logger(logger)

    @function_debug_log_wrapped
    def fit(self, X: TimeSeriesDataFrame, y: Any = None) -> 'ShortGrainDropper':
        """
        Define the grains to be stored.

        If all the grains should be dropped, raises DataExceptions.
        :param X: The time series data frame to fit on.
        :param y: Ignored
        :raises: DataException
        """
        self._raise_wrong_type_maybe(X)

        min_points = utilities.get_min_points(self._window_size,
                                              self._lags,
                                              self._max_horizon,
                                              self._cv)
        for grain, df in X.groupby_grain():
            if df.shape[0] >= min_points:
                self._grains_to_keep.append(grain)
        if not self._grains_to_keep:
            raise DataException("All grains are too short please check the data or decrease target_lags, "
                                "target_rolling_window_size, n_cross_validations or max_horizon.")
        self._is_fit = True
        return self

    @function_debug_log_wrapped
    def transform(self, X: TimeSeriesDataFrame, y: Any = None) -> TimeSeriesDataFrame:
        """
        Drop grains, which were not present in training set, or were removed.

        If all the grains should be dropped, raises DataExceptions.
        :param X: The time series data frame to check for grains to drop.
        :param y: Ignored
        :raises: ClientException, DataException
        """
        if not self._is_fit:
            raise ClientException("ShortGrainDropper transform method called before fit.")
        self._raise_wrong_type_maybe(X)
        drop_grains = set()

        def do_keep_grain(df):
            """Do the filtering and add all values to set."""
            keep = df.name in self._grains_to_keep
            if not keep:
                drop_grains.add(df.name)
            return keep

        result = X.groupby_grain().filter(lambda df: do_keep_grain(df))
        for grain in drop_grains:
            print(self.DROPPING_GRAIN_TEMPL.format(grain))
        if(result.shape[0] == 0):
            raise DataException("All grains were removed because "
                                "they were too short for horizon, cv and lag settings.")
        return cast(TimeSeriesDataFrame, result)

    def _raise_wrong_type_maybe(self, X: Any) -> None:
        """Raise exception if X is not TimeSeriesDataFrame."""
        if not isinstance(X, TimeSeriesDataFrame):
            raise NotTimeSeriesDataFrameException(
                Messages.XFORM_INPUT_IS_NOT_TIMESERIESDATAFRAME)
