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
"""One hot encoder implementation."""
import logging

from ayx_learn.utils.exceptions import OheUnexpectedLevelsException
from ayx_learn.utils.validate import validate_no_nulls

import numpy as np

import pandas as pd

from sklearn.preprocessing import OneHotEncoder
from sklearn.utils.validation import check_is_fitted

logger = logging.getLogger(__name__)


class OneHotEncoderTransformer(OneHotEncoder):
    """Used to perform one-hot-encoding on a dataframe."""

    def __init__(self, *args, categorical_columns="auto", **kwargs):
        """Construct one hot encoding object."""
        super().__init__(*args, **kwargs, sparse=False)
        self.categorical_columns = categorical_columns
        self._input_columns = []
        self._columns_to_encode = []

    @property
    def categorical_columns(self):
        """Getter for categorical columns."""
        return self.__categorical_columns

    @categorical_columns.setter
    def categorical_columns(self, value):
        if not isinstance(value, list) and value != "auto" and value is not None:
            raise ValueError(
                "categorical_columns must be a list of column names, 'auto', or None."
            )
        self.__categorical_columns = value

    def fit(self, x, *_, **__):
        """Fit one hot encoder."""
        self._input_columns = list(x)

        if self.categorical_columns is None:
            self._columns_to_encode = self._input_columns
        elif self.categorical_columns == "auto":
            self._columns_to_encode = x.select_dtypes(
                include=["category", "object"]
            ).columns.tolist()
        else:
            self._columns_to_encode = self.categorical_columns

        try:
            super().fit(x[self._columns_to_encode])
        except ValueError as e:
            logger.exception(e)
            validate_no_nulls(x)
            raise e

        return self

    def transform(self, x, *_, **__):
        """One hot encode new data."""
        check_is_fitted(self, ["categories_"])

        if set(x.columns) != set(self._input_columns):
            err_str = (
                f"Incoming columns don't match fitted columns: {self._input_columns}"
            )
            logger.error(err_str)
            raise ValueError(err_str)
        elif list(x.columns) != list(self._input_columns):
            x = x[self._input_columns]

        try:
            x_encoded = super().transform(x[self._columns_to_encode])
        except ValueError as e:
            logger.exception(e)
            validate_no_nulls(x)
            self._validate_no_unexpected_categories(x)
            raise e

        x_encoded = pd.DataFrame(
            x_encoded, columns=self.get_categorical_feature_names(), index=x.index
        )

        unencoded_columns = [
            col for col in list(x) if col not in self._columns_to_encode
        ]

        if len(unencoded_columns) == 0:
            return x_encoded

        unencoded_df = x[unencoded_columns]

        x_encoded[list(unencoded_df)] = unencoded_df

        return x_encoded

    def get_feature_names_(self):
        """Get the the names of all the output features."""
        check_is_fitted(self, ["categories_"])

        features = self.get_categorical_feature_names()

        unique_names = set(self._input_columns)
        for idx, feature in enumerate(features):
            new_feature = self._get_unique_name(feature, unique_names)
            features[idx] = new_feature
            unique_names.add(new_feature)

        for feature in self._input_columns:
            if feature not in self._columns_to_encode:
                features.append(feature)

        return features

    def get_categorical_feature_names(self):
        """Get the names of the output categorical features."""
        return super().get_feature_names(self._columns_to_encode).tolist()

    def get_link(self):
        """Get the link between original column names and encoded ones."""
        original_features = self._columns_to_encode
        encoded_features = self.get_feature_names_()

        num_features = [len(x) for x in self.categories_]
        num_features.insert(0, 0)

        category_idxs = np.cumsum(num_features).tolist()
        category_idxs = [
            (category_idxs[i], category_idxs[i + 1])
            for i in range(len(category_idxs) - 1)
        ]

        link = {
            col: col
            for col in self._input_columns
            if col not in self._columns_to_encode
        }
        for original_feature_idx, (encoded_start, encoded_end) in enumerate(
            category_idxs
        ):
            for encoded_feature_idx in range(encoded_start, encoded_end):
                link[encoded_features[encoded_feature_idx]] = original_features[
                    original_feature_idx
                ]

        return link

    @staticmethod
    def _get_unique_name(name, set_):
        if name not in set_:
            return name

        idx = 2
        while True:
            new_name = f"{name}_{idx}"
            if new_name not in set_:
                return new_name

            idx += 1

    def _validate_no_unexpected_categories(self, x):
        for idx, col in enumerate(self._columns_to_encode):
            expected_cats = set(self.categories_[idx])
            actual_cats = set(x[col].unique())

            if not actual_cats.issubset(expected_cats):
                unexpected_cats = actual_cats.difference(expected_cats)
                err_str = (
                    f"Found unexpected categories {unexpected_cats} in column {col}."
                )
                logger.error(err_str)
                raise OheUnexpectedLevelsException(err_str, (unexpected_cats, col))
