# -*- coding: utf-8 -*-

from typing import Optional, List, Tuple
from warnings import warn

import pandas as pd
import pandas_flavor as pf


def _control_duplicates(
    dataframe1: pd.DataFrame, dataframe2: pd.DataFrame
) -> Tuple[pd.DataFrame, pd.DataFrame]:
    _duplicates_dataframe1 = dataframe1.duplicated().sum()
    _duplicates_dataframe2 = dataframe2.duplicated().sum()
    if _duplicates_dataframe1 > 0:
        warn(
            UserWarning(
                f"There are {_duplicates_dataframe1} duplicate rows in dataframe1. These are dropped in order to perform set operations"
            )
        )
        dataframe1 = dataframe1.drop_duplicates()
    if _duplicates_dataframe2 > 0:
        warn(
            UserWarning(
                f"There are {_duplicates_dataframe2} duplicate rows in dataframe2. These are droppedin order to perform set operations"
            )
        )
        dataframe2 = dataframe2.drop_duplicates()
    return dataframe1, dataframe2


@pf.register_dataframe_method
def difference(dataframe1: pd.DataFrame, dataframe2: pd.DataFrame):
    """The set difference between dataframe1 (S) and dataframe2 (T), i.e. it returns those elements that are in dataframe1
    but not in dataframe2. Formally S - T = {s|s ∈ S and s ∉ T}.

    If duplicates exists in either dataframe they are dropped and a UserWarning is issued.

    Does not alter the original DataFrame.

    Parameters
    ----------
    dataframe1 : pd.DataFrame\n
    dataframe2 : pd.DataFrame\n

    The code is copied from the users WeNYoBen answer to the question "Python Pandas - Find difference between two data
    frames" at [StackOverflow](https://stackoverflow.com/questions/48647534/python-pandas-find-difference-between-two-data-frames)

    Returns
    -------
    pandas DataFrame\n
        The set difference between dataframe1 and dataframe2

    Raises
    ------
    ValueError\n
        Raises ValueError if the columns in datframe1 and dataframe2 are not identical.
    """
    if not dataframe1.columns.to_list() == dataframe2.columns.to_list():
        raise ValueError(
            "The number of and names of the columns in the two dataframes must be identical."
        )
    dataframe1, dataframe2 = _control_duplicates(
        dataframe1=dataframe1, dataframe2=dataframe2
    )
    return pd.concat([dataframe1, dataframe2, dataframe2]).drop_duplicates(keep=False)


@pf.register_dataframe_method
def symmmetric_difference(
    dataframe1: pd.DataFrame,
    dataframe2: pd.DataFrame,
    dataframe_names: Optional[List[str]] = None,
) -> pd.DataFrame:
    """The symmetric set difference between dataframe1 (S) and dataframe2 (T). It is the same as the union of the set difference between
    dataframe1 and dataframe2 and the set difference between dataframe2 and dataframe1. Formally A ⊕ B = (A - B) ∪ (B - A).

    If duplicates exists in either dataframe they are dropped and a UserWarning is issued.

    Does not alter the original DataFrame.

    Parameters
    ----------
    dataframe1 : pd.DataFrame\n
    dataframe2 : pd.DataFrame\n
    dataframe_names : Optional[List[str]], default None\n
        The names given in the list is inserted in the returned dataframe in a column called 'original_dataframe'. The purpose
        of this column is to make it easier to track differences between the two dataframes.

    Returns
    -------
    pandas DataFrame\n
        The set difference between dataframe1 and dataframe2

    Raises
    ------
    ValueError\n
        Raises ValueError if the columns in datframe1 and dataframe2 are not identical.
    ValueError\n
        Raises ValueError if the dataframe_names parameter is used and the length of the passed list is not 2.
    """
    if dataframe_names and len(dataframe_names) != 2:
        raise ValueError("Only two dataframe names")
    dataframe1, dataframe2 = _control_duplicates(
        dataframe1=dataframe1, dataframe2=dataframe2
    )
    df1 = difference(dataframe1=dataframe1, dataframe2=dataframe2)
    df2 = difference(dataframe1=dataframe2, dataframe2=dataframe1)
    if dataframe_names:
        df1["original_dataframe"] = dataframe_names[0]
        df2["original_dataframe"] = dataframe_names[1]
    return pd.concat([df1, df2]).reset_index(drop=True)


@pf.register_dataframe_method
def intersection(dataframe1: pd.DataFrame, dataframe2: pd.DataFrame) -> pd.DataFrame:
    """The set intersection between dataframe1 (S) and dataframe2 (T), i.e. it returns the elements that are both in dataframe1
    and dataframe2. Formally S ∩ T = {s|s ∈ S and s ∈ T}.

    If duplicates exists in either dataframe they are dropped and a UserWarning is issued.

    Does not alter the original DataFrame.

    Syntactic sugar for the pandas dataframe merge method with the parametere "how" passed as "inner".

    Parameters
    ----------
    dataframe1 : pd.DataFrame\n
    dataframe2 : pd.DataFrame\n

    Returns
    -------
    pandas DataFrame\n
        The set difference between dataframe1 and dataframe2

    Raises
    ------
    ValueError\n
        Raises ValueError if the columns in datframe1 and dataframe2 are not identical.
    """
    if not dataframe1.columns.to_list() == dataframe2.columns.to_list():
        raise ValueError(
            "The number of and names of the columns in the two dataframes must be identical."
        )
    dataframe1, dataframe2 = _control_duplicates(
        dataframe1=dataframe1, dataframe2=dataframe2
    )
    return dataframe1.merge(right=dataframe2, how="inner").reset_index(drop=True)


@pf.register_dataframe_method
def union(dataframe1: pd.DataFrame, dataframe2: pd.DataFrame) -> pd.DataFrame:
    """The set union between dataframe1 (S) and dataframe2 (T), i.e. it returns the elements that are both in dataframe1
    and dataframe2. Formally S ∩ T = {s|s ∈ S and s ∈ T}.

    If duplicates exists in either dataframe they are dropped and a UserWarning is issued.

    Does not alter the original DataFrame.

    Syntactic sugar for the pandas dataframe append method.

    Parameters
    ----------
    dataframe1 : pd.DataFrame\n
    dataframe2 : pd.DataFrame\n

    Returns
    -------
    pandas DataFrame\n
        The set difference between dataframe1 and dataframe2

    Raises
    ------
    ValueError\n
        Raises ValueError if the columns in datframe1 and dataframe2 are not identical.
    """
    if not dataframe1.columns.to_list() == dataframe2.columns.to_list():
        raise ValueError(
            "The number of and names of the columns in the two dataframes must be identical."
        )
    dataframe1, dataframe2 = _control_duplicates(
        dataframe1=dataframe1, dataframe2=dataframe2
    )
    return dataframe1.append(dataframe2).reset_index(drop=True)


if __name__ == "__main__":
    pass
