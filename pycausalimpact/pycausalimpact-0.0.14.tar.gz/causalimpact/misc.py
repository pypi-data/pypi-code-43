# Copyright 2014 Google Inc. All rights reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Miscellaneous functions to help in the implementation of Causal Impact."""


from __future__ import absolute_import, division, print_function

import numpy as np
import scipy.stats as stats
from statsmodels.tsa.statespace.structural import UnobservedComponents


def standardize(data):
    """
    Applies standardization to input data. Result should have mean zero and standard
    deviation of one.

    Args
    ----
      data: pandas DataFrame.

    Returns
    -------
      list:
        data: standardized data with zero mean and std of one.
        tuple:
          mean and standard deviation used on each column of input data to make
          standardization. These values should be used to obtain the original dataframe.

    Raises
    ------
      ValueError: if data has only one value.
    """
    if data.shape[0] == 1:
        raise ValueError('Input data must have more than one value')
    mu = data.mean(skipna=True)
    std = data.std(skipna=True, ddof=0)
    data = (data - mu) / std.fillna(1)
    return [data, (mu, std)]


def unstandardize(data, mus_sigs):
    """
    Applies the inverse transformation to return to original data.

    Args
    ----
      data: pandas DataFrame with zero mean and std of one.
      mus_sigs: tuple where first value is the mean used for the standardization and
                second value is the respective standard deviaion.

    Returns
    -------
      data: pandas DataFrame with mean and std given by input ``mus_sigs``
    """
    mu, sig = mus_sigs
    data = (data * sig) + mu
    return data


def get_z_score(p):
    """
    Returns the correspondent z-score with probability area p.

    Args
    ----
      p: float ranging between 0 and 1 representing the probability area to convert.

    Returns
    -------
      The z-score correspondent of p.
    """
    return stats.norm.ppf(p)


def get_referenced_model(model, endog, exog):
    """
    Buils an `UnobservedComponents` model using as reference the input `model`. This is
    mainly used for building models to make simulations of time series.

    Args
    ----
      model: `UnobservedComponents`.
          Template model that is used as reference to build a new one with new `endog`
          and `exog` variables.
      endog: pandas.Series.
          New endog value to be used in model.
      exog: pandas.Series.
          New exog value to be used in model.

    Returns
    -------
      ref_model: `UnobservedComponents`.
          New model built from input `model` setup.
    """
    args = {}
    args['level'] = model.level
    args['trend'] = model.trend
    args['seasonal'] = model.seasonal_periods
    args['freq_seasonal'] = [{'period': period, 'harmonics': h} for (period, h) in zip(
        model.freq_seasonal_periods, model.freq_seasonal_harmonics)]
    args['cycle'] = model.cycle
    args['ar'] = model.ar_order
    args['exog'] = exog
    args['endog'] = endog
    args['irregular'] = model.irregular
    args['stochastic_level'] = model.stochastic_level
    args['stochastic_trend'] = model.stochastic_trend
    args['stochastic_seasonal'] = model.stochastic_seasonal
    args['stochastic_freq_seasonal'] = model.stochastic_freq_seasonal
    args['stochastic_cycle'] = model.stochastic_cycle
    args['damped_cycle'] = model.damped_cycle
    cycle_bounds = model.cycle_frequency_bound
    lower_cycle_bound = 2 * np.pi / cycle_bounds[1]
    upper_cycle_bound = 2 * np.pi / cycle_bounds[0] if cycle_bounds[0] > 0 else np.inf
    args['cycle_period_bounds'] = (lower_cycle_bound, upper_cycle_bound)
    ref_model = UnobservedComponents(**args)
    return ref_model
