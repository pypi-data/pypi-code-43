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
"""Column select and column drop data frame transformer."""

import re

from ayx_learn.utils.validate import validate_list_of_str

import sklearn.base


class ColumnSelectorTransformer(sklearn.base.TransformerMixin):
    """Transformer used to select/deselect a set of columns based on regex.

    Column Selector/Deselector: Takes a list of regular expressions
    to match column names, and a flag to indicate if you want to select
    or deselect those columns.

    """

    def __init__(
        self, col_select=None, select_not_deselect=True, inplace=False, **kwargs
    ):
        if col_select is not None:
            validate_list_of_str(col_select)

        if col_select is None:
            self._col_select_regexs = []
        else:
            self._col_select_regexs = [re.compile(str(exp)) for exp in list(col_select)]

        self._select_not_deselect = select_not_deselect
        self._inplace = bool(inplace)

    def fit(self, x, y=None, **kwargs):
        """Fit the transformer. Noop in this case."""
        return self

    def transform(self, x, y=None, copy=False, **kwargs):
        """Select columns from dataframe based on regex."""
        inplace = self._inplace
        # Identify columns to select/deselect
        col_select = [list(filter(r.match, list(x))) for r in self._col_select_regexs]
        # Flatten the array
        col_select = [item for row in col_select for item in row]
        if self._select_not_deselect:
            result = x.drop(x.columns.difference(col_select), 1, inplace=inplace)
        else:
            result = x.drop(col_select, 1, inplace=inplace)
        if not inplace:
            x = result
        return x
