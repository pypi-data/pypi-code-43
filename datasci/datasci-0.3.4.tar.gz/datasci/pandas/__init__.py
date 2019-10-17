from itertools import combinations
from typing import Any, Iterator, Tuple
import logging
import numpy as np
import pandas as pd

logger = logging.getLogger(__name__)


def drop_na_columns(df: pd.DataFrame, inplace=False) -> pd.DataFrame:
    """
    Simply calls df.dropna(axis='columns', how='all', ...)
    """
    return df.dropna(axis='columns', how='all', inplace=inplace)


def uninformative_columns(df: pd.DataFrame) -> Iterator[Tuple[str, Any]]:
    """
    List columns of df where values in all cells are identical,
    along with that identical value.
    """
    # TODO: support DataFrames where df.columns is a MultiIndex
    for column in df.columns:
        series = df[column]
        series_iter = iter(df[column])
        try:
            exemplar = next(series_iter)
        except StopIteration:
            # no rows => nothing to check :|
            continue
        # nan is a special case, since np.nan != np.nan
        if series.dtype == np.float and np.isnan(exemplar):
            if all(np.isnan(item) for item in series_iter):
                yield column, exemplar
        elif all(item == exemplar for item in series_iter):
            yield column, exemplar


def drop_uninformative_columns(df: pd.DataFrame) -> pd.DataFrame:
    """
    Drop columns from df where values in all cells are identical.
    """
    for column, value in uninformative_columns(df):
        logger.debug(
            'Dropping column %r from DataFrame (every value %s %r)',
            column,
            'is' if isinstance(value, float) and np.isnan(value) else '=',
            value,
        )
        df = df.drop(column, axis='columns')
    return df


def duplicate_columns(df: pd.DataFrame) -> Iterator[Tuple[str, str]]:
    """
    List columns of df where values in all cells are identical to those in a preceding column,
    along with the preceding column having identical values.
    """
    columns = set(df.columns)
    for column1, column2 in combinations(df.columns, 2):
        if column1 not in columns or column2 not in columns:
            continue
        series1 = df[column1]
        series2 = df[column2]
        # convert dtypes to strings since numpy raises "TypeError: data type not understood"
        # when comparing to pandas's dtypes extensions
        if str(series1.dtype) == str(series2.dtype) and all(series1 == series2):
            yield column2, column1
            columns.remove(column2)
    return df


def drop_duplicate_columns(df: pd.DataFrame) -> pd.DataFrame:
    """
    Drop columns from df where values in all cells are identical to those in a preceding column.
    """
    for duplicate_column, original_column in duplicate_columns(df):
        logger.debug(
            'Dropping column %r from DataFrame (duplicate of %r)',
            duplicate_column,
            original_column,
        )
        df = df.drop(duplicate_column, axis='columns')
    return df
