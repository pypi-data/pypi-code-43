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
"""FeatureModifier used for operating on subsets of DataFrame columns using regex."""

from ayx_learn.pipeline_utils.dataframe_feature_union import DataFrameFeatureUnion
from ayx_learn.transformers.column_selector_transformer import ColumnSelectorTransformer
from ayx_learn.transformers.dataframe_function_transformer import (
    DataFrameFunctionTransformer,
)

import pandas as pd

import sklearn.base
import sklearn.pipeline


# Feature modifier: takes a list of regular expressions to
# indicate columns to apply the transformer to
# If in place is set to true, the original columns are removed,
# if false, the new features are unioned to the
# original data set. The columns not selected by
# col_select are untouched
class FeatureModifier(sklearn.base.TransformerMixin, sklearn.base.BaseEstimator):
    """
    Custom transformer for operating on features using regex.

    Transformer that is designed to operate on Pandas
    DataFrame objects by mapping a sklearn Transformer to a set
    of one or more columns in a Pandas DataFrame.  Several
    DataframeFeatureModifier instances can be chained together in
    an sklearn.Pipeline, returning a pandas Dataframe as output.
    """

    def __init__(
        self,
        transformer,
        col_select=None,
        in_place=True,
        name_scheme="in_place",
        name="",
        drop_unselected=False,
    ):
        """
        Initialize a FeatureModifier.

        Arguments:
            transformer: sklearn.TransformerMixin -- An sklearn transformer
            that will be applied to the columns specified in col_select

        Keyword Arguments:
            col_select : list -- A list containing regular expression
                selectors that will be applied for selecting
                one or more DataFrame columns for the specified
                transformer to operate on (default: {None})
            in_place : bool -- Specifies whether transformed columns
                will replace original columns, or simply be
                appended to original columns with names
                generated according to name_scheme (default: {True})
            name_scheme : str -- "in_place"|"append"|"new"
                "append": The value specified in name will
                be appended to original column name as the name
                of newly transformed columns
                "new" : The value specified in name will
                be used for new columns, with a numeric value,
                separated by underscore, appended to the new column
                name (default: {in_place})
            name : str -- Value used for new columns generated,
                according to values specified for "in_place" and
                "name_scheme" parameters. (default: {""})
        """
        self._drop_unselected = drop_unselected
        self._transformer = transformer

        if not in_place and name_scheme == "in_place":
            raise ValueError(
                f"""Must use different naming scheme than
                {name_scheme} when operating in place."""
            )

        self._name_scheme = name_scheme
        self._name = name

        # If it's in place, then we want to deselect the columns that we are
        # operating on. If it's not in place (i.e. we're appending new features)
        # then we want to keep all the original columns, i.e. deselect None
        if in_place:
            self._unchanged_selector = ColumnSelectorTransformer(
                col_select=col_select, select_not_deselect=False
            )
        else:
            self._unchanged_selector = ColumnSelectorTransformer(
                col_select=None, select_not_deselect=False
            )

        # Select the columns to apply the transformer to
        self._change_selector = ColumnSelectorTransformer(
            col_select=col_select, select_not_deselect=True
        )

        self.steps_list = [
            (
                "2",
                sklearn.pipeline.make_pipeline(
                    self._change_selector,
                    DataFrameFunctionTransformer(self._register_original_col_names),
                    self._transformer,
                    DataFrameFunctionTransformer(self._create_output_df),
                ),
            )
        ]

        if not self._drop_unselected:
            self.steps_list.insert(
                0, ("1", sklearn.pipeline.make_pipeline(self._unchanged_selector))
            )

        # Build the pipeline to run, we will individually run the
        # transformer on the selected columns, and then feature union the result
        # with the unchanged columns
        self._internal_pipeline = DataFrameFeatureUnion(self.steps_list)

    def _create_output_df(self, x, y=None):
        if isinstance(x, pd.DataFrame):
            return x
        return pd.DataFrame(x, columns=self._gen_col_names(x))

    def _register_original_col_names(self, x, y=None):
        self._orig_cols = list(x)
        return x

    def _intersection_empty(self, lst1, lst2):
        return len(self._intersection(lst1, lst2)) == 0

    def _intersection(self, lst1, lst2):
        return [value for value in lst1 if value in lst2]

    def _validate_columns(self, new_cols):
        if not self._intersection_empty(new_cols, self._orig_cols):
            raise ValueError(
                f"""Column names contain duplicates. The following
            column names appear in original and new columns:
            {self._intersection(new_cols, self._orig_cols)}"""
            )

    def _gen_col_names(self, x):
        if self._name_scheme == "in_place":
            return self._orig_cols
        elif self._name_scheme == "append":
            new_cols = [name + self._name for name in self._orig_cols]
            self._validate_columns(new_cols)
            return new_cols
        elif self._name_scheme == "new":
            new_cols = [self._name + "_" + str(ind) for ind in range(len(x[0]))]
            self._validate_columns(new_cols)
            return new_cols
        else:
            raise ValueError("Unknown naming scheme")

    def fit(self, x, y=None, **kwargs):
        """Fit a dataframe."""
        assert isinstance(x, pd.DataFrame)
        return self._internal_pipeline.fit(x, y)

    def transform(self, x, y=None, *args, **kwargs):
        """Transform a dataframe."""
        assert isinstance(x, pd.DataFrame)
        return self._internal_pipeline.transform(x, y)
