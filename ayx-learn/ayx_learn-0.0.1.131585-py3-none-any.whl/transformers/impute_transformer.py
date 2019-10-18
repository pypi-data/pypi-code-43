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
"""Impute method transformer."""

from enum import Enum

from ayx_learn.utils.validate import validate_enum

import pandas as pd

import sklearn.base


def mean(df, *args):
    """Calculate fill value in MEAN mode."""
    return df.mean()


def mode(df, *args):
    """Calculate fill value in MODE mode."""
    return df.mode()[0]


def median(df, *args):
    """Calculate fill value in MEDIAN mode."""
    return df.median()


def value(_, val, *args):
    """Calculate fill value in VALUE mode."""
    return val


def custom(df, _, func, *args):
    """Calculate fill value in CUSTOM mode."""
    if not func:
        raise ValueError("Function has not been properly specified.")
    return func(df)


impute_method_dict = {
    "MEAN": mean,
    "MEDIAN": median,
    "MODE": mode,
    "VALUE": value,
    "CUSTOM": custom,
}

# Auto generate the Enum for Impute methods based on the above dict.
# This implicitly forces any additional imputation methods to have
# associated functions
ImputeMethods = Enum("ImputeMethods", " ".join(impute_method_dict.keys()))


class ImputeTransformer(sklearn.base.TransformerMixin):
    """Impute columns in a DataFrame.

    Parameters
    ----------
    colnames: List[str]
        Columns to impute.

    method: ImputeMethods
        Imputation method to apply. MEAN, MODE, MEDIAN, VALUE, or CUSTOM.

    value: float
    """

    def __init__(
        self,
        method: ImputeMethods = ImputeMethods.MEAN,
        value: float = 0.0,
        custom_method=None,
        colname=None,
        inplace=False,
        **kwargs
    ):
        self.method = method
        self.value = value
        self.col_value_dict = {}
        if custom_method:
            self.custom_method = custom_method
        else:
            self.__custom_method = None
        self.colname = colname
        self._inplace = bool(inplace)

    @property
    def method(self):
        """Get imputation method."""
        return self.__method

    @method.setter
    def method(self, method: ImputeMethods):
        """Set imputation method."""
        validate_enum(method, ImputeMethods)
        self.__method = method

    @property
    def value(self):
        """Get value in VALUE imputation method."""
        return self.__value

    @value.setter
    def value(self, value: float):
        """Set value in VALUE imputation method."""
        self.__value = value

    @property
    def custom_method(self):
        """Getter for custom_method used in the CUSTOM imputer mode."""
        return self.__custom_method

    @custom_method.setter
    def custom_method(self, custom_method):
        """Setter for custom_method used in the CUSTOM imputer mode."""
        if not callable(custom_method):
            raise ValueError("Custom method must be callable.")
        self.__custom_method = custom_method

    def transform(self, x: pd.DataFrame, y=None, **kwargs) -> pd.DataFrame:
        """Impute the colnames in the DataFrame.

        Parameters
        ----------
        x : pandas.DataFrame
            Incoming DataFrame.

        Returns
        -------
        pandas.DataFrame
            Imputed DataFrame

        Raises
        ------
        ValueError
            If imputation method is invalid.
        Exception
            If an error occurs, such as invalid colname.
        """
        columns_to_impute = x.columns
        if self.colname is not None:
            columns_to_impute = [self.colname]
        inplace = self._inplace
        if not inplace:
            x = x.copy()
        for column in columns_to_impute:
            try:
                # Extract the column
                data = x[column]

                # Calculate the fill value
                try:
                    value = self.col_value_dict[column]
                except KeyError:
                    raise ValueError("A column is present that was not during fit.")

                # Perform imputation
                if data.dtype.name == "category" and value not in data.cat.categories:
                    data = data.cat.add_categories(value)
                x.loc[:, column] = data.fillna(value)
            except Exception as err:
                raise err
        return x

    def fit(self, x: pd.DataFrame, y=None, **kwargs):
        """Return self."""
        method = self.method
        columns_to_impute = x.columns
        if self.colname is not None:
            columns_to_impute = [self.colname]
        for column in columns_to_impute:
            try:
                # Extract the column
                data = x[column]

                # Calculate the fill value
                value = impute_method_dict[method.name](
                    data, self.value, self.custom_method
                )

                # Save it
                self.col_value_dict[column] = value

            except Exception as err:
                raise err
        return self
