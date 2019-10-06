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
"""Validation utility functions."""
import logging
from enum import Enum
from typing import List

from ayx_learn.utils.constants import ColumnTypes
from ayx_learn.utils.exceptions import NullValueError

logger = logging.getLogger(__name__)


def validate_enum(value: Enum, enum: Enum):
    """Validate value is in the enum.

    Parameters
    ----------
    value : Enum
        Value to be tested
    enum : Enum
        Enum to be tested

    Returns
    -------
    None
        If enum is valid.

    Raises
    ------
    TypeError
        If value is not in enum.
    """
    if not isinstance(value, enum):
        raise TypeError(f"{value} is not a valid {enum}")


def validate_list_of_str(lst: List[str]):
    """Validate that list consists of elements of type str.

    Parameters
    ----------
    lst : List[str]
        List of type str.

    Returns
    -------
    None
        If valid list.

    Raises
    ------
    TypeError
        If not a List or not all elements of list are of type str.
    """
    if not isinstance(lst, List):
        raise TypeError(f"{lst} is not a valid {List}")

    if not all(isinstance(elem, str) for elem in lst):
        raise TypeError(f"{lst} is not all of type str")


def validate_col_type(coltype):
    """Assert coltype is valid."""
    return validate_enum(coltype, ColumnTypes)


def validate_no_nulls(df):
    """Assert that a dataframe contains no null values."""
    for col in list(df):
        if df[col].isnull().values.any():
            err_str = f"Dataframe contains null values in column: {col}"
            logger.error(err_str)
            raise NullValueError(err_str, col)
