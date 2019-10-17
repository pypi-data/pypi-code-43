import numpy as np
import pandas as pd

from datasci.pandas import drop_uninformative_columns, drop_duplicate_columns


def test_drop_uninformative_columns(n: int = 10):
    df = pd.DataFrame.from_dict({
        'repeated_string': np.repeat('abc', n),
        'repeated_float':  np.repeat(1.23, n),
        'repeated_int':    np.repeat(123, n),
        'repeated_nan':    np.repeat(np.nan, n),
        'random_float':    np.random.uniform(size=n),
        'int_range':       np.arange(n),
        'all_but_one':     np.concatenate([np.repeat(100, n - 1), [99]]),
        'all_but_one_2':   np.concatenate([[-1], np.repeat(0, n - 1)]),
        'nan_but_last':    np.concatenate([np.repeat(np.nan, n - 1), [1]]),
    })
    original_columns = set(df.columns)
    uninformative_columns = {column for column in original_columns
                             if column.startswith('repeated_')}
    informative_columns = original_columns - uninformative_columns
    # run function and compare result to original
    df = drop_uninformative_columns(df)
    resulting_columns = set(df.columns)
    # check that informative columns were not dropped and that uninformative columns were
    assert resulting_columns == informative_columns


def test_drop_duplicate_columns(n: int = 10):
    df = pd.DataFrame.from_dict({
        'int_range':              np.arange(n),
        'duplicate_int_range':    np.arange(n),
        'float_range':            np.arange(n).astype(float),
        'duplicate_float_range':  np.arange(n).astype(float),
        'repeated_int':           np.repeat(123, n),
        'repeated_string':        np.repeat('123', n),
        'duplicate_repeated_int': np.repeat('123', n).astype(int),
    })
    original_columns = set(df.columns)
    df = drop_duplicate_columns(df)
    assert set(df.columns) == {column for column in original_columns
                               if not column.startswith('duplicate_')}
