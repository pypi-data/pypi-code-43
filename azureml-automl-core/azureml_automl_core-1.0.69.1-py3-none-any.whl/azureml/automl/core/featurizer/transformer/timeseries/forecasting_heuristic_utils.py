# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Utilities used to infer auto features."""
import math
import numpy as np
import pandas as pd
import warnings

from pandas.tseries.offsets import (Minute, Hour, Day,
                                    MonthBegin, MonthEnd,
                                    QuarterBegin, QuarterEnd,
                                    YearBegin, YearEnd)
from statsmodels.tsa.seasonal import seasonal_decompose
from statsmodels.tsa.stattools import pacf
from statsmodels.tsa.tsatools import freq_to_period
from typing import cast, List, Optional, Tuple, Union

from automl.client.core.common.types import GrainType
from automl.client.core.common.constants import TimeSeriesInternal
from automl.client.core.common.exceptions import DataException


def get_heuristic_max_horison(data: pd.DataFrame, time_colname: str) -> int:
    """
    Estimate heuristic max horison given the data frame.

    **Note:** If the frequency can not be established the default will be returned.
    :param data: the data frame to estimate heurustics for.
    :time_colname: The name of a time column.
    """
    freq = get_frequency_safe(data[time_colname])
    if freq is None:
        return TimeSeriesInternal.MAX_HORIZON_DEFAULT
    max_horizon = frequency_based_lags(freq)
    if max_horizon == 0:
        return TimeSeriesInternal.MAX_HORIZON_DEFAULT
    return max_horizon


def get_frequency_safe(time_index: pd.DatetimeIndex) -> pd.DateOffset:
    """
    Determine the frequency of a time index.

    :param time_index: the index, which frequency needs to be determined.
    :return: the frequency value.
    """

    freq = pd.infer_freq(time_index)
    if freq is not None:
        return freq
    diffs = time_index.values[1:] - time_index.values[:-1]
    ddf = pd.DataFrame({'diffs': diffs})
    td = ddf.mode()['diffs'][0]
    return pd.tseries.frequencies.to_offset(td)


def frequency_based_lags(freq: pd.DateOffset) -> int:
    """
    Return a frequency based lag that should be added to the list of lags.

    returns 0 if lags can not be estimated.
    :param freq: the frequency for which lags should be determined.
    :return: The value of lags for given frequency or 0.
    """

    tol = 1e-6

    offset = pd.tseries.frequencies.to_offset(freq)

    if isinstance(offset, Minute):
        # see if we evenly divide an hour
        multiple = 3600.0 / offset.delta.seconds
        if abs(multiple - round(multiple)) < tol:
            return round(multiple)

        # and if not an hour, do we evenly divide a day?
        multiple = 86400.0 / offset.delta.seconds
        if abs(multiple - round(multiple)) < tol:
            return round(multiple)

        return 0

    if isinstance(offset, Hour):
        sec_offset = _get_seconds_from_hour_offset_maybe(offset)
        multiple = 86400.0 / sec_offset
        if abs(multiple - round(multiple)) < tol:
            return round(multiple)

    if isinstance(offset, Day):
        if offset.n == 1:
            return 7
        else:
            return 0
    # there is no fixed lag for 'same day last month' due to the above note
    if isinstance(offset, MonthBegin) or isinstance(offset, MonthEnd):
        multiple = 12.0 / offset.n
        if abs(multiple - round(multiple)) < tol:
            return round(multiple)
        return 0

    if isinstance(offset, QuarterBegin) or isinstance(offset, QuarterEnd):
        multiple = 4.0 / offset.n
        if abs(multiple - round(multiple)) < tol:
            return round(multiple)
        return 0

    if isinstance(offset, YearBegin) or isinstance(offset, YearEnd):
        if offset.n == 1:
            return 1
    return 0


def _get_seconds_from_hour_offset_maybe(off: Hour) -> int:
    """
    Pandas does not correctly process multiples of hours in v. 0.23.4

    This functuion checks if it is the case and corrects it if needed.
    :param off: The hour offset to get seconds from.
    """
    # First check if there is an error.
    test_off = Hour(n=42)
    # we expect 42 * 60 * 60 seconds.
    exp_seconds = 42 * 60 * 60
    # If there is an error 3600 will be returned, which is not 3600 * 42.
    if exp_seconds == test_off.delta.seconds:
        return cast(int, off.delta.seconds)
    else:
        return cast(int, off.n * 60 * 60)


def analyze_pacf_one_grain(series: pd.Series) -> Tuple[Optional[int], Optional[int]]:
    """
    output the suggested lags (p) and rolling window (k) settings

    Input: a DataFrame with one column and a time-based index
    """

    z = 1.96  # 95% significance
    ifreq = None

    if series.index is not None and series.index.freq is None:
        # Fix the series, containing NaNs and/or gaps in dates.
        # For example 01/01/2010, 01/03/2010, 01/04/2010
        # will be filled to
        # 01/01/2010, 01/02/2010, 01/03/2010, 01/04/2010
        # NaNs will be interpolated.

        ifreq = get_frequency_safe(series.sort_index().index)
        # find the range of dates within which we should have regular intervals
        mindate = min(series.index)
        maxdate = max(series.index)
        # construct the range
        TIME_IX = 'timeidx'
        expected_dates = pd.DataFrame({
            TIME_IX: pd.date_range(mindate, maxdate, freq=ifreq),
            'default': np.NaN
        })
        expected_dates.rename(
            columns={TIME_IX: series.index.names[0]}, inplace=True)
        expected_dates.set_index(series.index.names[0], inplace=True)
        # merge the original series onto the expected times
        series_as_frame = series.to_frame()
        series_as_frame.reset_index(inplace=True, drop=False)
        series_as_frame.set_index(expected_dates.index.names[0], inplace=True, drop=True)
        series_as_frame.columns = ['data']
        filled_out = expected_dates.merge(series_as_frame, how='left', left_index=True, right_index=True)
        # now we have all dates but nan values where rows were not provided
        filled_out = filled_out.drop(columns=['default']).sort_index()
        series = filled_out.interpolate()

    # deseason/detrend the series
    period = -1
    # We should make sure that the series frequency may be converted to periods.
    if ifreq is None:
        ifreq = series.index.freq
    try:
        # First we try the statsmodels method.
        period = freq_to_period(ifreq)
    except ValueError:
        # If it fails we do our best to fix it.
        period = frequency_based_lags(ifreq)
    if period == 0:
        raise DataException("The frequency is not supported.")

    # two periods larger than the data period
    lags = min(period * 2, len(series))

    if any([pd.isna(x) for x in series[series.columns[0]]]):
        series = series.interpolate()
        series.dropna(inplace=True, axis=0)
        if len(series) == 0:
            raise DataException("One of the series is empty.")
    results = seasonal_decompose(series, freq=period)

    # compute pacf, dropping na resulting from STL
    # we will add up the trend and the noise
    try:
        pac = pacf((results.trend + results.resid).dropna(), nlags=lags)
    except np.linalg.LinAlgError:
        warnings.warn("Linear algebra problem. Might be caused a constant value series in the data.")
        return (None, None)

    sig = z * 1. / math.sqrt(lags)
    sig_bool = [math.fabs(x) > sig for x in pac]
    if all(sig_bool):
        # warn user there is strong seasonality/moving average
        warnings.warn("Strong seasonality or moving average: de-seasoning did not work well")
        p = 0
    else:
        p = np.argmin(sig_bool) - 1  # argmin on bool finds first index where false
        # we want the index of last true
        # 0-based index will account for the first element always being 1

    # argmax will be zero if all are false
    # this will output 1 then and will be ignored
    k = np.argmax(sig_bool[(p + 1):]) + (p + 1)

    return (p, k)


def analyze_pacf_per_grain(dataframe: pd.DataFrame,
                           time_colname: str,
                           target_colname: str,
                           grain_colnames: Optional[Union[str, List[str]]] = None,
                           max_grains: int = 100) -> Tuple[int, int]:
    """
    Analyze all grains in a dataframe and recommend lags and RW settings

    :param dataframe: A DataFrame with the time index in a column.
    :param time_colname: The time column name.
    :param grain_colnames: The grain column names if any.
    :param target_colname: The target column name.
    :max_grains: The maximal number of grains to sample from the data set.
    :return: lags and RW settings.
    """
    INVALID_CORRELATION = 'Unable to estimate the partial correlation. No heuristic lags could be detected.'
    # get all grain combinations (don't group yet, filter first)
    if grain_colnames is not None:
        grains = dataframe[grain_colnames].drop_duplicates()
        N = grains.shape[0]
        if N >= max_grains:
            # don't use all the grains, but pick 100
            chosen = np.random.choice(N, size=max_grains, replace=False)
        else:
            chosen = range(N)
        chosen_grains = grains.iloc[chosen]
        # If the data frame contains only one grains column,
        if isinstance(chosen_grains, pd.Series):
            chosen_grains = chosen_grains.to_frame()
        subset = dataframe.merge(chosen_grains, how='inner').set_index(time_colname)
        pk = subset.groupby(grain_colnames)[target_colname].apply(analyze_pacf_one_grain)
        # we now have a series consisting of (p,k) tuples, one tuple per grain
        # unpack into a dataframe and compute the mean
        pk.dropna(inplace=True)
        modes = pd.DataFrame(list(pk), columns=["p", "k"]).mode()
        if len(modes) == 0:
            raise DataException(INVALID_CORRELATION)
    else:
        # No grains, only one df.
        p, k = analyze_pacf_one_grain(dataframe.set_index(time_colname)[target_colname])
        if p is None or k is None:
            raise DataException(INVALID_CORRELATION)
        modes = {"p": [p], "k": [k]}

    Lags = modes["p"][0]
    RW = 0 if Lags == 0 else modes["k"][0]

    return int(Lags), int(RW)
