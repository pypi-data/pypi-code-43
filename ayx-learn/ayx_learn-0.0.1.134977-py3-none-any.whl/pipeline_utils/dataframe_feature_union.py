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
"""Feature union for pandas dataframes in sklearn pipelines."""

import numpy as np

import pandas as pd

import scipy

import sklearn.pipeline


class DataFrameFeatureUnion(sklearn.pipeline.FeatureUnion):
    """
    Override of sklearn FeatureUnion for use with dataframes.

    The purpose of this class is to allow for using pandas DataFrames in sklearn
    Transformers and pipelines while preserving DataFrame features
    like column names, etc.

    See blog post here where this was copied from:
    https://zablo.net/blog/post/pandas-dataframe-in-scikit-learn-feature-union

    Arguments:
        transformer_list: list -- List of (string, transformer) tuples

        n_jobs: int  -- Number of jobs to run in parallel

        transformer_weights : dict, optional -- Multiplicative weights
            for features per transformer.  Keys are transformer names,
            values the weights.
    """

    def _find_duplicates(self, lst):
        found = set()
        duplicates = set()
        for value in lst:
            if value in found:
                duplicates.add(value)
            found.add(value)

        return list(duplicates)

    def _merge_dataframes_by_column(self, xs):
        retval = pd.concat(xs, axis="columns", copy=False)
        col_names = list(retval)

        duplicate_cols = self._find_duplicates(col_names)
        if len(duplicate_cols) > 0:
            raise ValueError(f"Duplicate columns found: f{duplicate_cols}")

        return retval

    def transform(self, x, y=None):
        """Apply transform to each parallel step in the pipeline and feature union."""
        xs = []
        for _, trans, weight in self._iter():
            xs.append(trans.transform(x))

        if not xs:
            # All transformers are None
            return np.zeros((x.shape[0], 0))
        if any(scipy.sparse.issparse(f) for f in xs):
            xs = scipy.sparse.hstack(xs).tocsr()
        else:
            xs = self._merge_dataframes_by_column(xs)
        return xs

    def fit(self, x, y=None):
        """Fit each transform in the feature union."""
        self.transformer_list = list(self.transformer_list)
        self._validate_transformers()
        transformers = []
        for _, trans, _ in self._iter():
            transformers.append(trans.fit(x, y))
        self._update_transformer_list(transformers)
        return self

    def fit_transform(self, x, y=None, **fit_params):
        """
        Fit/transform the steps in the feature union.

        Override of sklearn.FeatureUnion fit_transform
        that handles pandas DataFrame objects, ensuring
        that output will still be a pandas DataFrame.

        Arguments:
            x: pandas DataFrame object -- Pandas DataFrame
            containing the data columns specified in the
            a PandasTransform constructor.

        Keyword Arguments:
            y: pandas Series object -- Targets for supervised learning (default: {None})

        Returns
        -------
            pandas.DataFrame -- A pandas DataFrame containing the
            results of the transformations specified.
        """
        self.fit(x, y)
        return self.transform(x, y)
