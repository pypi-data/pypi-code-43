__all__ = ['is_na', 'has_na', 'drop_na', 'fill_na', 'get_number_of_na', 'df_isnull']


import functools
from collections.abc import Iterable

import numpy as np
import pandas as pd
from pandas.api.types import is_categorical_dtype

from azureml.studio.core.utils.categoryutils import add_category


def is_na(value):
    """
    This function takes a scalar or an iterable and detects
    whether this scalar is missing (NaN in numeric arrays, None or NaN
    in object arrays, NaT in datetimelike).

    For an iterable object, this function will recursively detect if the iterable
    is empty or only contains missing value

    return True for value == np.nan, None or NAT
    :param value: scalar or None
    :return:
    type: bool
    """
    # For an iterable object, recursively detect if it is empty or contains only
    # missing value
    if isinstance(value, Iterable):
        if isinstance(value, pd.DataFrame):
            return is_na(value[column] for column in value)

        elif isinstance(value, dict):
            return is_na(v for v in value.values())

        elif isinstance(value, str):
            return pd.isnull(value)

        elif isinstance(value, bytes):
            return pd.isnull(value)

        return all(is_na(x) for x in value)

    return pd.isnull(value)


def has_na(iterable):
    """
    Determine if an array has NaN

    :param iterable: an iterator with __iter__ attribute
    :return:
    type: bool
    """
    if hasattr(iterable, '__iter__'):
        return any(pd.isnull(iterable))
    else:
        raise TypeError('Input array is not an iterator')


def drop_na(series, reset_index=False, include_inf=False):
    """
    Drop all NaN in an array

    :param series: pandas.Series
    :param inplace: bool, if True, do operation in place and return None
    :param reset_index: bool, if True, reset the index
    :param include_inf: bool, if True, drop np.inf and -np.inf as well
    :return: array or None

    """

    if not isinstance(series, pd.Series):
        raise TypeError('Input array must be pandas.Series')

    if include_inf:
        try:
            # Slice series with Boolean series. In this way the performance is vastly improved.
            # However, series == np.inf will raise error if series has elements such as Series, DataFrame or np array.
            # To avoid such error, wrap with try-except block.
            series = series[~((series == np.inf) | (series == -np.inf))]
        except ValueError as e:
            # Ignore the error if it is caused by comparing Series, DataFrame or Numpy array object with np.inf.
            if not any(isinstance(e, (np.ndarray, pd.Series, pd.DataFrame)) for e in series):
                raise e
    if reset_index:
        return series.dropna().reset_index(drop=True)
    return series.dropna()


def fill_na(array, replacement_value, inplace=False):
    """
    replace NaN in array with replacement_value

    :param array: object with fillna method
    :param replacement_value: Value to use to fill holes (e.g. 0),
            alternately a dict/Series/DataFrame of values specifying
            which value to use for each index (for a Series) or column (for a DataFrame).
    :param inplace: bool, if True, do operation in place and return None
    :return: array or None
    """
    if not hasattr(array, 'fillna'):
        raise TypeError('Input array must have attribute fillna')

    # For categorical series, add replacement_value to categories
    if isinstance(array, pd.Series) and is_categorical_dtype(array):
        if inplace:
            add_category(
                series=array,
                new_category=replacement_value,
                inplace=True
            )
        else:
            array = add_category(
                series=array,
                new_category=replacement_value
            )

    if inplace:
        array.fillna(replacement_value, inplace=True)
    else:
        return array.fillna(replacement_value)


def get_number_of_na(array):
    """
    Compute the number of missing values in array

    """
    # This implementation is better than sum(pd.isnull(array)),
    # both in speed and memory storage
    return len(array) - pd.Series.count(array)


def df_isnull(df: pd.DataFrame, column_names=None, column_indices=None, include_inf=False):
    """Detect missing values for DataFrame

    Return a boolean series indicating if the data rows has NA in selected columns.
    Check all columns in DataFrame if no column names or column indices provided.
    Similar as Series.isnull(), but faster, lower memory cost, and support regarding inf as missing value.

    :param df: pandas.DataFrame.
    :param column_names: A list of string.
    :param column_indices: A list of 0-based int.
    :param include_inf: bool, if True, df_isnull(np.inf) will be True
    :return: a boolean series.
    """

    # same as df[col_names].isnull().any(axis=1), but fast and low memory cost

    def _series_is_null(series):
        if include_inf:
            return pd.isnull(series) | np.isinf(series)
        else:
            return pd.isnull(series)

    if column_names is not None:
        # Guard a single str input.
        if type(column_names) not in (list, tuple):
            raise ValueError("'column_names' should be a list or tuple.")
        row_isnull_per_column = map(lambda col_name: _series_is_null(df[col_name]), column_names)
    elif column_indices is not None:
        if type(column_indices) not in (list, tuple):
            raise ValueError("'column_indices' should be a list or tuple.")
        row_isnull_per_column = map(lambda col_idx: _series_is_null(df.iloc[:, col_idx]), column_indices)
    else:
        row_isnull_per_column = map(lambda col_idx: _series_is_null(df.iloc[:, col_idx]), range(0, df.shape[1]))

    return functools.reduce(lambda a, b: a | b, row_isnull_per_column)
