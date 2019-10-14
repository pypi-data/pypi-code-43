# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Fix the dtypes after the infertence."""
import logging
import numpy as np
import pandas as pd

from typing import Optional, cast

from automl.client.core.common.logging_utilities import function_debug_log_wrapped
from automl.client.core.common.constants import TimeSeriesInternal
from automl.client.core.common.time_series_data_frame import TimeSeriesDataFrame
from ..automltransformer import AutoMLTransformer


class RestoreDtypesTransformer(AutoMLTransformer):
    """Restore the dtypes of numerical data types."""

    def __init__(self,
                 tsdf: TimeSeriesDataFrame,
                 logger: Optional[logging.Logger] = None) -> None:
        """
        Construct for RestoreDtypesTransformer.

        :param tsdf: The initial time series data frame before
                     transforms application.
        :type tsdf: TimeSeriesDataFrame
        :param logger: The logger to be used in the pipeline.
        :type logger: Logger
        """
        super().__init__()
        self._init_logger(logger)
        self._target_column = tsdf.ts_value_colname  # type: Optional[str]
        # The actual fit have to happen in the constructor
        # because during fit-transform the dataframe will be modified
        # and the dtypes will be changed.
        col_na = set()
        for col in tsdf.columns:
            if all([pd.isna(val) for val in tsdf[col]]):
                col_na.add(col)
        if len(col_na) == tsdf.shape[1]:
            # Nothing to do, the types can not be determined.
            self._dtypes = None  # type: Optional[pd.Series]
            return
        x_no_na = tsdf[list(set(tsdf.columns.values).difference(col_na))]
        # The columns with NA may be detected incorrectly as float.
        if len(x_no_na) > 0:
            self._dtypes = x_no_na.dtypes
        else:
            # Fall back to regular mechanism.
            self._dtypes = tsdf.dtypes

    def fit(self,
            x: TimeSeriesDataFrame,
            y: np.ndarray = None) -> 'RestoreDtypesTransformer':
        """
        Fit function for RestoreDtypesTransformer.

        :param x: Input data.
        :type x: TimeSeriesDataFrame
        :param y: Unused.
        :type y: numpy.ndarray
        :return: Class object itself.
        """
        return self

    @function_debug_log_wrapped
    def transform(self,
                  x: TimeSeriesDataFrame) -> TimeSeriesDataFrame:
        """
        Transform the data frame.

        :param x: Input data.
        :type x: TimeSeriesDataFrame
        :return: The data frame with correct dtypes.
        """
        # Ensure the data types are the same as before featurization
        # for numeric columns.
        if self._dtypes is None:
            return x
        for col in self._dtypes.index:
            if col == self._target_column:
                # Skip the type for target column
                continue
            if np.issubdtype(self._dtypes[col], np.number) and col in x.columns:
                x[col] = x[col].astype(self._dtypes[col])
        return x

    def fit_transform(self,
                      x: TimeSeriesDataFrame,
                      y: np.ndarray = None) -> TimeSeriesDataFrame:
        """
        Fit and transform function for RestoreDtypesTransformer.

        :param x: Input data.
        :type x: TimeSeriesDataFrame
        :param y: Unused.
        :type y: numpy.ndarray
        :return: The data frame with correct dtypes.
        """
        self.fit(x, y)
        return cast(TimeSeriesDataFrame, self.transform(x))
