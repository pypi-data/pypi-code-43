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
"""Definition of the ColumnTypeTransformer for applying data typing to a dataframe."""

from ayx_learn.utils.constants import ColumnTypes
from ayx_learn.utils.typing import typing_conversions
from ayx_learn.utils.validate import validate_col_type

import pandas as pd

import sklearn.base


class ColumnTypeTransformer(sklearn.base.TransformerMixin):
    """Transformer used for applying typing to a dataframe."""

    def __init__(
        self, coltype=ColumnTypes.NUMERIC, colname=None, inplace=False, **kwargs
    ):
        self.coltype = coltype
        self.colname = colname
        self._inplace = bool(inplace)

    @property
    def coltype(self):
        """Getter for column type of this transformer."""
        return self.__coltype

    @coltype.setter
    def coltype(self, value):
        """Setter for column type of this transformer."""
        validate_col_type(value)
        self.__coltype = value

    def transform(self, x, y=None, **kwargs):
        """Apply typing transforms to input dataframe."""
        if not isinstance(x, pd.DataFrame):
            raise TypeError("Input must be a pandas dataframe.")
        columns_to_transform = x.columns
        if self.colname is not None:
            columns_to_transform = [self.colname]
        inplace = self._inplace
        if not inplace:
            x = x.copy()
        # Apply transformation columnwise
        for column in columns_to_transform:
            x.loc[:, column] = typing_conversions[self.coltype](x[column])
        return x

    def fit(self, x, y=None, **kwargs):
        """Fit the transformer."""
        return self
