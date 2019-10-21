# -*- coding: utf-8 -*-
import math

import numpy as np
import pandas as pd


def dropna(df):
    """Drop rows with "Nans" values
    """
    df = df[df < math.exp(709)]  # big number
    df = df[df != 0.0]
    df = df.dropna()
    return df

def ema(series, periods, fillna=False):
    if fillna:
        return series.ewm(span=periods, min_periods=0).mean()
    return series.ewm(span=periods, min_periods=periods).mean()

def get_min_max(x1, x2, f='min'):
    if not np.isnan(x1) and not np.isnan(x2):
        if f == 'max':
            return max(x1, x2)
        elif f == 'min':
            return min(x1, x2)
        else:
            raise ValueError('"f" variable value should be "min" or "max"')
    else:
        return np.nan

# TODO: more efficient implementation (vectorized)
def wilder_smooth_sum(self, values, window):
    """Wilder's smoothing techniques

    https://stockcharts.com/school/doku.php?id=chart_school:technical_indicators:average_directional_index_adx

    The first technique is used to smooth each period's +DM1, -DM1 and TR1 values over 14 periods. As with
    an exponential moving average, the calculation has to start somewhere so the first value is simply the
    sum of the first 14 periods. As shown below, smoothing starts with the second 14-period calculation and
    continues throughout.

    First TR14 = Sum of first 14 periods of TR1
    Second TR14 = First TR14 - (First TR14/14) + Current TR1
    Subsequent Values = Prior TR14 - (Prior TR14/14) + Current TR1

    Args:
        values(pandas.Series): dataset column.
        window(int): size period.
    Returns:
        pandas.Series: dataset column applied wilder's smooth sum.

    """
    length = len(values.index)
    smooth_val = pd.Series(np.zeros(length), index=values.index)
    smooth_val[0:window] = np.nan
    if values.shape[0] >= window+1:
        smooth_val[window] = np.sum(values[1:window+1].values)
        for i in range(window + 1, length):
            smooth_val[i] = (smooth_val[i-1] * (1 - 1.0 / window)) + values[i]
    return smooth_val

# TODO: more efficient implementation (vectorized)
def wilder_smooth_adx_calculate(self, values, window):
    """Wilder's smoothing techniques

    https://stockcharts.com/school/doku.php?id=chart_school:technical_indicators:average_directional_index_adx

    The second technique is used to smooth each period's DX value to finish with the Average Directional Index
    (ADX). First, calculate an average for the first 14 days as a starting point. The second and subsequent
    calculations use the smoothing technique below:

    Definition:
        First ADX14 = 14 period Average of DX
        Second ADX14 = ((First ADX14 x 13) + Current DX Value)/14
        Subsequent ADX14 = ((Prior ADX14 x 13) + Current DX Value)/14

    Args:
        values(pandas.Series): dataset column.
        window(int): size period.
    Returns:
        pandas.Series: dataset column applied wilder's smooth sum.
    """
    length = len(values.index)
    smooth_val = pd.Series(np.zeros(length), index=values.index)
    padding = values.isnull().sum()
    smooth_val[0:window+padding] = np.nan
    if values.shape[0] >= window+1+padding:
        smooth_val[window+padding] = np.mean(values[1+padding:window+1+padding].values)
        for i in range(padding + window + 1, length):
            smooth_val[i] = ((smooth_val[i-1] * (window-1)) + values[i]) / window
    return smooth_val
