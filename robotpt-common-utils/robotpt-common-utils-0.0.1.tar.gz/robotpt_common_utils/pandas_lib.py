import pandas as pd
import numpy as np


def remove_consecutive_nans(
        dataframe,
        column_name,
        max_consecutive_nans
):
    if type(dataframe) is not pd.DataFrame:
        raise TypeError("'dataframe' should be a Pandas Dataframe")
    if max_consecutive_nans < 0:
        raise ValueError("'max_consecutive_nans' should be greater than 0")

    # Same as function below but doesn't work if this is placed in a function
    _dataframe = dataframe.copy()
    _dataframe['Group'] = _dataframe[column_name].notnull().astype(int).cumsum()
    _dataframe = _dataframe[_dataframe[column_name].isnull()]
    _dataframe = _dataframe[
        _dataframe.Group.isin(
            _dataframe.Group.value_counts()[
                _dataframe.Group.value_counts() <= max_consecutive_nans
                ].index
        )
    ]
    _dataframe['count'] = _dataframe.groupby('Group')['Group'].transform('size')
    _dataframe.drop_duplicates(['Group'], keep='first')

    return dataframe.drop(_dataframe.index)


def split_on_nan(dataframe, column_name):

    dataframes = np.split(dataframe, np.where(np.isnan(dataframe[column_name]))[0])

    # removing NaN entries
    dataframes = [
        ev[~np.isnan(ev[column_name])]
        for ev in dataframes
        if not isinstance(ev, np.ndarray)
    ]

    # removing empty DataFrames
    dataframes = [ev for ev in dataframes if not ev.empty]
    return dataframes
