# -*- coding: utf-8 -*-

import re
from collections import Counter
from typing import Union, List, Dict, Any

import pandas as pd
import pandas_flavor as pf


@pf.register_dataframe_method
def clean_column_names(
    object_: Union[List[Union[str, int]], pd.Index, pd.DataFrame],
    convert_duplicates: bool = True,
    convert_camel_case: bool = False,
) -> Union[List[str], pd.DataFrame]:
    """Clean messy column names. Inspired by the functions make_clean_names and clean_names from
    the R package janitor.

    Does not alter the original DataFrame.

    Parameters
    ----------
    object_ : Union[List[Union[str, int]], pd.Index, pd.DataFrame]\n
        Messy columnnames in a list or as a pandas index or a dataframe with messy columnames
    convert_duplicates : bool, optional\n
        If True, unique columnnames are created. E.g. if there are two columns, country and Country,
        this option set the columnnames to country1 and country2. By default True
    convert_camel_case : bool, optional\n
        Converts camel case to snake case. E.g the columnname SubRegion is changed to sub_region.
        However, it only works for actual camel case names, like the example above.
        If instead the original columname where SUbRegion the resulting converted name would be s_ub_region. Hence, use this option with caution. By default False

    Returns
    -------
    List[str] or a pandas DataFrame\n
        A list of cleaned columnames or a dataframe with cleaned columnames

    Raises
    ------
    TypeError\n
        Raises TypeError if the passed object_ is not a list, pandas index or a pandas dataframe
    """
    if isinstance(object_, (list, pd.Index)):
        columns = _clean_column_names_list(
            columns=object_,
            convert_duplicates=convert_duplicates,
            convert_camel_case=convert_camel_case,
        )
        return columns
    elif isinstance(object_, pd.DataFrame):
        df = _clean_column_names_dataframe(
            df=object_,
            convert_duplicates=convert_duplicates,
            convert_camel_case=convert_camel_case,
        )
        return df
    else:
        raise TypeError(
            f"The passed object_ is a {type(object_)}. It must be a list, pandas index or a pandas dataframe!"
        )


def _clean_column_names_list(
    columns: Union[List[Union[str, int]], pd.Index],
    convert_duplicates: bool = True,
    convert_camel_case: bool = False,
) -> List[str]:
    """Cleans messy columnames. Written to be a utility function. It is recommended
    to use the clean_columnames function instead.

    Regex that replace multiple spaces with one space i based on the user Nasir's answer at
    [StackOverflow](https://stackoverflow.com/questions/1546226/simple-way-to-remove-multiple-spaces-in-a-string)

    Regex that replace all non-alphanumeric characters in a string (except underscore) with underscore
    is based on the user psun's answer at [StackOverflow](https://stackoverflow.com/questions/12985456/replace-all-non-alphanumeric-characters-in-a-string/12985459)

    Parameters
    ----------
    columns : Union[List[Union[str, int]], pd.Index]\n
        Messy columnames
    convert_duplicates : bool, optional\n
        If True, unique columnnames are created. E.g. if there are two columns, country and Country,
        this option set the columnnames to country1 and country2. By default True
    convert_camel_case : bool, optional\n
        Converts camel case to snake case. E.g the columnname SubRegion is changed to sub_region.
        However, it only works for actual camel case names, like the example above. If instead the original
        columname where SUbRegion the resulting converted name would be s_ub_region. Hence, use this
        option with caution. By default False

    Returns
    -------
    List[str]\n
        Cleaned columnnames
    """
    columns = _clean_column_names(
        columns=columns,
        convert_duplicates=convert_duplicates,
        convert_camel_case=convert_camel_case,
        expressions=[
            r"column.lower()",  # set columnnames to lowercase
            r're.sub(r"\s+", " ", column).strip()',  # replace multiple spaces with one space
            r're.sub(r"\W+", "_", column).strip()',  # replace all non-alphanumeric characters in a string (except underscore) with underscore
            r'column.rstrip("_").lstrip("_")',  # remove leading and lagging underscores
        ],
    )
    return columns


def _clean_column_names_dataframe(
    df: pd.DataFrame, convert_duplicates: bool = True, convert_camel_case: bool = False
) -> pd.DataFrame:
    """Cleans messy columnames of a dataframe. Written to be a utility function. It is recommended
    to use the clean_columnames function instead.

    Does not alter the original DataFrame.

    Parameters
    ----------
    df : pd.DataFrame\n
        A dataframe with messy columnnames
    convert_duplicates : bool, optional\n
        If True, unique columnnames are created. E.g. if there are two columns, country and Country,
        this option set the columnnames to country1 and country2. By default True
    convert_camel_case : bool, optional\n
        Converts camel case to snake case. E.g the columnname SubRegion is changed to sub_region.
        However, it only works for actual camel case names, like the example above. If instead the original
        columname where SUbRegion the resulting converted name would be s_ub_region. Hence, use this
        option with caution. By default False
    Returns
    -------
    pd.DataFrame\n
        A dataframe with cleaned columnames

    Raises
    ------
    TypeError\n
        If the df object is not a pandas dataframe TypeError is raised
    """
    if not isinstance(df, pd.DataFrame):
        raise TypeError(
            f"The passed df is a {type(df)}. It must be a pandas dataframe!"
        )
    df.columns = _clean_column_names_list(
        columns=df.columns,
        convert_duplicates=convert_duplicates,
        convert_camel_case=convert_camel_case,
    )
    return df


def _clean_column_names(
    columns: Union[List[Union[str, int]], pd.Index],
    custom: Dict[Any, Any] = None,
    expressions: List[str] = None,
    convert_duplicates: bool = True,
    convert_camel_case: bool = False,
) -> List[str]:
    """Base function for clean_columnames. Can be used for very specific needs.
    ----------
    columns : Union[List[Union[str, int]], pd.Index]\n
        Messy columnnames
    custom : Dict[Any, Any], optional\n
        If you want to replace one character with another this option can be used.
        E.g if you want exclamationpoint to be replaced with dollarsign, pass the following:
        /{'!':'$'/}. Use with caution if the expression parameter is used since the expression parameter
        is evaluated after the custom parameter. By default None
    expressions : List[str], optional\n
        In this parameter any string method or regex can be passed. The must be passed as a string
        with column as object. E.g if you want, as in the example with in the custom parameter, wants
        to exclamationpoint to be replaced with dollarsign, pass the following:
         ["column.replace('!', '$')"]
        or you want capitalize the columns:
         ["column.capitalize()"]
        or you want to replace multiple spaces with one space:
         [r're.sub(r"\s+", " ", column).strip()'] # noqa: W605
        or if you want to do all of the above:
        ['column.replace("!", "$")',
         'column.capitalize()',
         r're.sub(r"\s+", " ", column).strip()' # noqa: W605
        ]
        By default None
    convert_duplicates : bool, optional\n
        If True, unique columnnames are created. E.g. if there are two columns, country and Country,
        this option set the columnnames to country1 and country2. By default True
    convert_camel_case : bool, optional\n
        Converts camel case to snake case. E.g the columnname SubRegion is changed to sub_region.
        However, it only works for actual camel case names, like the example above. If instead the original
        columname where SUbRegion the resulting converted name would be s_ub_region. Hence, use this
        option with caution. By default False

    Returns
    -------
    List[str]\n
        Clean columnnames

    Raises
    ------
    TypeError\n
        If passed column object is not a list or a pandas index TypeError is raised
    """
    if not isinstance(columns, (list, pd.Index)):
        raise TypeError(
            f"The passed columns is a {type(columns)}. It must be a list or a pandas index!"
        )
    if type(columns) == pd.Index:
        columns = columns.to_list()  # type: ignore
    columns = [str(column) for column in columns]
    if custom:
        for i, j in custom.items():
            columns = [k.replace(i, j) for k in columns]
    if convert_camel_case:
        columns = _camel_to_snake(columns=columns)
    if expressions:
        for reg in expressions:
            columns = [
                eval(reg, {}, {"column": column, "re": re}) for column in columns
            ]
    if convert_duplicates:
        columns = _convert_duplicates(columns=columns)
    return columns


def _camel_to_snake(columns: List[str]) -> List[str]:
    """Converts a list of strings with camel case formatting to a list of strings with snake case formatting

    Code is based on code from [StackOverflow](https://stackoverflow.com/questions/1175208/elegant-python-function-to-convert-camelcase-to-snake-case)

    Parameters
    ----------
    columns : List[str]
        A list of strings with camel case formatting

    Returns
    -------
    List
        A list of strings with snake case formatting

    Example
    -------
    ```python
    a = ["CountryName", "SubRegion"]
    b = _camel_to_snake(columns=a)
    print(b)

    ["country_name", "sub_region"]
    ```
    """
    _cols = []
    for i in columns:
        i = re.sub(r"(.)([A-Z][a-z]+)", r"\1_\2", i)
        i = re.sub(r"([a-z0-9])([A-Z])", r"\1_\2", i).lower().replace("__", "_")
        _cols.append(i)
    return _cols


def _convert_duplicates(columns: List[str]) -> List[str]:
    """Adds progressive numbers to a list of duplicate strings. Ignores non-duplicates.

    Function is based on code from [StackOverflow](https://stackoverflow.com/questions/30650474/python-rename-duplicates-in-list-with-progressive-numbers-without-sorting-list/30651843#30651843)

    Parameters
    ----------
    columns : List[str]\n
        A list of strings

    Returns
    -------
    List[str]\n
        A list of strings with progressive numbers added to duplicates.

    Example
    -------
    ```python
    a = ["country_name", "sub_region", "country_name"]\n
    b = _convert_duplicates(columns=a)\n
    print(b)
    ["country_name1", "sub_region", "country_name2"]
    ```


    """
    d: Dict[str, List] = {
        a: list(range(1, b + 1)) if b > 1 else [] for a, b in Counter(columns).items()
    }
    columns = [i + str(d[i].pop(0)) if len(d[i]) else i for i in columns]
    return columns


if __name__ == "__main__":
    pass
