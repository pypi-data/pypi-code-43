# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Module for creating training dataset from dapaprep Dataflow object."""
import math
import numpy as np
import pandas as pd
import torch
from typing import Any, List
from torch.utils.data import Dataset

import azureml.automl.core.featurizer.transformer.timeseries as automl_transformer
from azureml.automl.core.column_purpose_detection import ColumnPurposeDetector
from ..constants import FeatureType, ForecastConstant, DROP_COLUMN_LIST
from ..types import DataInputType, TargetInputType
import forecast.data.transforms as tfs
from forecast.data import FUTURE_DEP_KEY, FUTURE_IND_KEY, PAST_DEP_KEY, PAST_IND_KEY
from forecast.data.sources.data_source import DataSourceConfig
from forecast.data.sources.data_source import EncodingSpec


class TimeSeriesDataset(Dataset):
    """This class provides a dataset for training timeseries model with dataprep features and label."""

    @staticmethod
    def _drop_extra_columns(X: pd.DataFrame) -> pd.DataFrame:
        drop_columns = []
        for col in X.columns:
            if col in DROP_COLUMN_LIST:
                drop_columns.append(col)
        if drop_columns:
            return X.drop(drop_columns, inplace=False, axis=1)
        return X

    def __init__(self,
                 X_dflow: DataInputType,
                 y_dflow: TargetInputType,
                 horizon: int,
                 step: int = 1,
                 thinning: float = 1.0,
                 has_past_regressors: bool = False,
                 one_hot: bool = False,
                 pre_transform: automl_transformer.TimeSeriesTransformer = None,
                 transform: Any = None,
                 train_transform: bool = False,
                 fetch_y_only: bool = False,
                 **settings: Any):
        """
        Take a training data(X) and label(y) and provides access to windowed subseries for torch DNN training.

        :param X_dflow: Training features in DataPrep DataFlow form(numeric data of shape(row_count, feature_count).
        :param y_dflow: Training label in DataPrep DataFlow for with shape(row_count, 1).
        :param horizon: Number of time steps to forecast.
        :param step: Time step size between consecutive examples.
        :param thinning: Fraction of examples to include.
        :param has_past_regressors: data to populate past regressors for each sample
        :param one_hot: one_hot encode or not
        :param pre_transform: pre_transformer to use
        :param transform: feature transforms to use
        :param train_transform: whether training is needed for transformers
        :param settings: automl timeseries settings for pre_transform
        """
        self.horizon = horizon
        self.step = step
        self.thinning = thinning
        self.transform = transform
        self._pre_transform = pre_transform
        self._len = None
        self.lookback = None
        self.fetch_y_only = fetch_y_only
        self._cache = {}
        if self._pre_transform is not None:
            assert isinstance(self._pre_transform, automl_transformer.TimeSeriesTransformer)
        if isinstance(X_dflow, pd.DataFrame):
            X_df = X_dflow
        else:
            X_df = X_dflow.to_pandas_dataframe(extended_types=True)

        if isinstance(y_dflow, np.ndarray):
            y_df = pd.DataFrame(y_dflow)
        elif isinstance(y_dflow, pd.DataFrame):
            y_df = y_dflow
        else:
            y_df = y_dflow.to_pandas_dataframe(extended_types=True)

        get_encodings, encodings = False, []
        if train_transform and self._pre_transform is None and settings is not None and len(settings) > 0:
            # Create a timeseries transform which is applied before data is passed to DNN
            self._pre_transform = automl_transformer.TimeSeriesTransformer(logger=None, **settings)
            self._pre_transform.fit(X_df, y_df)
            if one_hot:
                get_encodings = True

        if self._pre_transform:
            X_transformed = self._pre_transform.transform(X_df, y_df)
            if ForecastConstant.automl_constants.TimeSeriesInternal.DUMMY_TARGET_COLUMN in X_transformed:
                y_df = X_transformed[ForecastConstant.automl_constants.TimeSeriesInternal.DUMMY_TARGET_COLUMN]
            X_transformed = self._drop_extra_columns(X_transformed)
        else:
            X_transformed = X_df

        if get_encodings:
            encodings = self._get_embedding(X_transformed)

        self.dset_config = DataSourceConfig(feature_channels=X_transformed.shape[1],
                                            forecast_channels=1,
                                            encodings=encodings)

        self._data_grains = []
        grains = settings.get(ForecastConstant.grain_column_names, None) if settings else None
        if grains is not None:
            if isinstance(grains, str):
                grains = [grains]
            assert ForecastConstant.automl_constants.TimeSeriesInternal.DUMMY_TARGET_COLUMN not in X_transformed
            X_transformed.insert(0, ForecastConstant.automl_constants.TimeSeriesInternal.DUMMY_TARGET_COLUMN,
                                 y_df.values)
            groupby = X_transformed.groupby(grains)
            for grain in groupby.groups:
                X_df = groupby.get_group(grain)
                y_df = X_df[ForecastConstant.automl_constants.TimeSeriesInternal.DUMMY_TARGET_COLUMN]
                X = X_df.values.T
                y = y_df.values
                y = y.reshape((1, y.shape[0]))
                self._data_grains.append(_DataGrainItem(X, y))
        else:
            X = X_transformed.values.T
            y = y_df.values
            y = y.reshape((1, y.shape[0]))
            X = np.vstack((y, X))
            self._data_grains.append(_DataGrainItem(X, y))

        self.has_past_regressors = has_past_regressors
        if self.transform is None and not self.fetch_y_only:
            self.transform = self._get_transforms(one_hot)

    def set_lookback(self, lookback: int) -> None:
        """
        Set lookback to be used with this dataset.

        :param lookback: Number of time steps used as input for forecasting.
        """
        self.lookback = lookback
        self._len = 0
        for item in self._data_grains:
            start_index = self._len
            size = self._get_size(item.y)
            self._len += size
            item.lookup_start_ix = start_index
            item.lookup_end_ix = self._len

    def _get_size(self, y) -> None:
        """
        Set lookback to be used with this dataset.

        :param lookback: Number of time steps used as input for forecasting.
        """
        # If timeseries is smaller than lookback + horizon, we would need to pad
        if y.shape[-1] < self.lookback + self.horizon:
            sample_count = 1
        else:
            sample_count = (y.shape[-1] - self.lookback - self.horizon + self.step) // self.step
        return max(1, int(self.thinning * sample_count))

    def is_small_dataset(self) -> bool:
        """Return true if dataset is small."""
        if self._len is not None:
            return self._len < ForecastConstant.SMALL_DATASET_MAX_ROWS
        return True

    @staticmethod
    def _get_embedding(data: pd.DataFrame) -> List[EncodingSpec]:
        index = 0
        encodings = []
        column_purpose_detector = ColumnPurposeDetector()
        column_purpose = column_purpose_detector.get_raw_stats_and_column_purposes(data)
        for stats, featureType, name in column_purpose:
            if featureType == FeatureType.Categorical and stats.num_unique_vals > 2:
                # TODO remove this and replace this with label encoder
                max_num_features = int(data[name].max().astype(int) + 1)
                # embedding = EncodingSpec(feature_index=index, num_vals=stats.num_unique_vals)
                embedding = EncodingSpec(feature_index=index, num_vals=max_num_features)
                encodings.append(embedding)
                # TODO remove this once we move to unified logger
                print(index, name, featureType, stats.num_unique_vals, max_num_features + 1)
            index = index + 1
        return encodings

    def _get_transforms(self, one_hot) -> tfs.ComposedTransform:
        targets = [0]
        tf_list = [
            tfs.LogTransform(offset=1.0, targets=targets),
            tfs.SubtractOffset(targets=targets)
        ]
        drop_first = False
        if one_hot and self.dset_config.encodings:
            drop = True if drop_first else False
            tf_list = [tfs.OneHotEncode([e.feature_index for e in self.dset_config.encodings],
                                        [e.num_vals for e in self.dset_config.encodings],
                                        drop_first=drop),
                       tfs.OneHotEncode([e.feature_index for e in self.dset_config.encodings],
                                        [e.num_vals for e in self.dset_config.encodings],
                                        drop_first=drop,
                                        key=FUTURE_IND_KEY)] + tf_list
        return tfs.ComposedTransform(tf_list)

    def __len__(self) -> int:
        """Return the number of samples in the dataset.

        :return: number of samples.
        """
        return self._len

    def feature_count(self):
        """Return the number of features in the dataset."""
        return self._data_grains[0].X.shape[0]

    def get_train_test_split(self, validation_percent: float = 0.1):
        """
        Split the dataset into train and test as per the validtaion percent.

        :param validation_percent: percentage of data to be used as validation.
        """
        if self.lookback is None:
            raise ValueError("lookback not set")
        train_size = 0
        test_size = 0
        test_data_grains = []
        train_data_grains = []
        for item in self._data_grains:
            # total samples in the grain.
            grain_size = item.lookup_end_ix - item.lookup_start_ix

            grain_test_size = max(1, math.floor(grain_size * validation_percent))
            if grain_size == grain_test_size:
                grain_test_size = 0
            grain_train_size = grain_size - grain_test_size
            train_item = _DataGrainItem(item.X, item.y, train_size, train_size + grain_train_size)
            train_size += grain_train_size
            train_data_grains.append(train_item)
            if grain_test_size > 0:
                grain_test_size = math.ceil(grain_test_size / self.horizon)
                test_item = _DataGrainItem(item.X, item.y, test_size, test_size + grain_test_size, grain_train_size)
                test_size += grain_test_size
                test_data_grains.append(test_item)

        train_dataset = TransformedTimeSeriesDataset(train_data_grains, self.horizon, self.lookback, train_size,
                                                     self.dset_config, self.step, self.has_past_regressors,
                                                     self.pre_transform, self.transform, self.fetch_y_only)

        test_dataset = TransformedTimeSeriesDataset(test_data_grains, self.horizon, self.lookback, test_size,
                                                    self.dset_config, self.horizon, self.has_past_regressors,
                                                    self.pre_transform, self.transform, self.fetch_y_only)
        assert len(test_data_grains) <= len(train_data_grains)
        if len(test_data_grains) == 0:
            msg = "length of test grain {0}, train size = {1}".\
                format(len(test_data_grains), len(train_data_grains))
        assert len(test_data_grains) > 0, msg

        return train_dataset, test_dataset

    def __getitem__(self, idx: int) -> dict:
        """
        Get the idx-th training sample item from the dataset.

        :param idx: the item to get the sample.
        :return: returns the idx-th sample.
        """
        cached = self._cache.get(idx, {})
        if cached:
            return cached

        idx2, X, y = self._get_index_grain_from_lookup(idx)
        sample = self. _getitem_from_df(X, y, idx2)
        self._cache[idx] = sample
        return sample

    def _get_index_grain_from_lookup(self, idx) -> tuple:
        located_grain = None
        for item in self._data_grains:
            if idx >= item.lookup_start_ix and idx < item.lookup_end_ix:
                located_grain = item
                break
        if located_grain is None:
            raise IndexError("passed in {0} is not found in datasets".format(idx))
        # lookup index from the grain is the offset +
        # steps size * distance to the index from lookup start.
        lookup_index = located_grain.offset + self.step * (idx - located_grain.lookup_start_ix)
        return lookup_index, located_grain.X, located_grain.y

    def _getitem_from_df(self, X, y, idx: int) -> dict:
        """
        Get the idx-th training sample item from the dataset.

        :param X: feature ndarray
        :param y: target array
        :param idx: the item to get the sample.
        :return: returns the idx-th sample.
        """
        # Get time series
        # The data values are transformed so the result is of the shape nfeatures X lookback for X
        # and 1 X horizon for y
        start_index = idx
        X_past = None
        X_fut = None
        if self.has_past_regressors:
            if X.shape[-1] < self.lookback + self.horizon:
                # If the time series is too short, zero-pad on the left
                if not self.fetch_y_only:
                    X_past = X[1:, :-self.horizon]
                    X_past = np.pad(
                        X_past,
                        pad_width=((0, 0), (self.lookback - X_past.shape[-1], 0)),
                        mode='constant',
                        constant_values=0
                    )
                    X_fut = X[1:, -self.horizon:]

                    X_past = torch.tensor(X_past.astype(np.float32), dtype=torch.float)
                    X_fut = torch.tensor(X_fut.astype(np.float32), dtype=torch.float)

                y_past = y[:, :-self.horizon]
                y_past = np.pad(
                    y_past,
                    pad_width=((0, 0), (self.lookback - y_past.shape[-1], 0)),
                    mode='constant',
                    constant_values=0
                )
                y_fut = y[:, -self.horizon:]

                y_past = torch.tensor(y_past.astype(np.float32), dtype=torch.float)
                y_fut = torch.tensor(y_fut.astype(np.float32), dtype=torch.float)
            else:
                end_index = start_index + self.lookback + self.horizon
                if not self.fetch_y_only:
                    X_item = X[1:, start_index:end_index]
                    X_past = torch.tensor(X_item[:, :self.lookback].astype(np.float32), dtype=torch.float)
                    X_fut = torch.tensor(X_item[:, self.lookback:].astype(np.float32), dtype=torch.float)
                y_item = y[:, start_index:end_index]
                y_past = torch.tensor(y_item[:, :self.lookback].astype(np.float32), dtype=torch.float)
                y_fut = torch.tensor(y_item[:, self.lookback:].astype(np.float32), dtype=torch.float)

            # Create the input and output for the sample
            sample = {PAST_IND_KEY: X_past,
                      PAST_DEP_KEY: y_past,
                      FUTURE_IND_KEY: X_fut,
                      FUTURE_DEP_KEY: y_fut}
        else:
            X = None
            if not self.fetch_y_only:
                X_item = X[:, start_index:start_index + self.lookback]
                X = torch.tensor(X_item.astype(np.float32), dtype=torch.float)
            y_item = y[:, start_index + self.lookback:start_index + self.lookback + self.horizon]
            y = torch.tensor(y_item.astype(np.float32), dtype=torch.float)
            # Create the input and output for the sample
            sample = {'X': X, 'y': y}
        if self.transform:
            sample = self.transform(sample)
        return sample

    @property
    def pre_transform(self):
        """Pre transforms for this timeseries dataset."""
        return self._pre_transform


class _DataGrainItem:
    """This class holds a slice of feature and label."""

    def __init__(self,
                 X: np.ndarray,
                 y: np.ndarray,
                 lookup_start_ix: int = 0,
                 lookup_end_ix: int = None,
                 offset: int = 0):
        self.X = X
        self.y = y
        self.lookup_start_ix = lookup_start_ix
        self.lookup_end_ix = lookup_end_ix
        self.offset = offset
        assert X.shape[-1] == y.shape[-1]
        if lookup_end_ix and lookup_start_ix >= lookup_end_ix:
            raise ValueError("end lookup index should be greater than start lookup index")


class TransformedTimeSeriesDataset(TimeSeriesDataset):
    """This class provides a dataset for based on automl transformed data and used in train test split."""

    def __init__(self, data_grains: List[_DataGrainItem],
                 horizon: int,
                 lookback: int,
                 len: int,
                 dset_config: DataSourceConfig,
                 step: int = 1,
                 has_past_regressors: bool = False,
                 pre_transform: automl_transformer.TimeSeriesTransformer = None,
                 transform: Any = None,
                 fetch_y_only: bool = False):
        """
        Take a list of grains amd and provides access to windowed subseries for torch DNN training.

        :param data_grains : list of datagrains.
        :param horizon: Number of time steps to forecast.
        :param lookback: look back to use with in examples.
        :param len: number of samples in the grains.
        :param step: Time step size between consecutive examples.
        :param dset_config: dataset config
        :param has_past_regressors: data to populate past regressors for each sample
        :param pre_transform: pre_transformer to use
        :param transform: feature transforms to use
        :param fetch_y_only: whether fetch_y_only
        """
        self._cache = {}
        self._data_grains = data_grains
        self.horizon = horizon
        self.lookback = lookback
        self._len = len
        self.dset_configs = dset_config
        self.step = step
        self.has_past_regressors = has_past_regressors
        self._pre_transform = pre_transform
        self.transform = transform
        self.fetch_y_only = fetch_y_only
        if self._pre_transform is not None:
            assert isinstance(self._pre_transform, automl_transformer.TimeSeriesTransformer)
        print("Len ", len, "step", step)
