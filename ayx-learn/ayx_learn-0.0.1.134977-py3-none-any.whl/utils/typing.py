# Copyright (C) 2019 Alteryx, Inc. All rights reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.
"""Collection of functions to assist with data typing."""

from ayx_learn.utils.constants import ColumnTypes

import numpy as np

import pandas as pd


def to_numeric(series):
    """Convert a series to numeric values."""
    series = pd.to_numeric(series, errors="coerce")

    if series.dtype != np.float64:
        series = series.apply(val_to_float)

    return series


def to_categorical(series):
    """Convert a series to categorical values."""
    series = series.astype("category")
    series = series.apply(str)
    return series


def to_boolean(series):
    """Convert a series to boolean values."""
    col_to_bool = np.vectorize(val_to_bool)
    return col_to_bool(series).astype(float)


def to_id(series):
    """Convert a series to an ID type."""
    return series


def val_to_float(x):
    """Convert a single number to a floating point value."""
    try:
        return float(x)
    except Exception:
        return np.nan


def val_to_bool(val):
    """Convert a single number to a boolean value."""
    val = str(val).strip().upper()

    try:
        return {
            "1": True,
            "1.0": True,
            "TRUE": True,
            "T": True,
            "Y": True,
            "YES": True,
            "0": False,
            "0.0": False,
            "FALSE": False,
            "F": False,
            "N": False,
            "NO": False,
        }[val]
    except KeyError:
        return None


typing_conversions = {
    ColumnTypes.NUMERIC: to_numeric,
    ColumnTypes.CATEGORICAL: to_categorical,
    ColumnTypes.BOOLEAN: to_boolean,
    ColumnTypes.ID: to_id,
}
