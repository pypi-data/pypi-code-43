# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Dataset that supports streaming."""
from contextlib import contextmanager
from enum import Enum
from random import randint
from typing import Iterator, Optional, Any, Dict, List, Tuple, Set

import azureml.dataprep as dprep
import numpy as np
from nimbusml.preprocessing import DatasetTransformer

from automl.client.core.common import constants
from automl.client.core.common.dataflow_utilities import PickleableDataflow
from automl.client.core.common.exceptions import DataException
from automl.client.core.runtime.datasets import DatasetBase
from automl.client.core.runtime.problem_info import ProblemInfo


class DatasetMetadataKeys(Enum):
    """Metadata class for a Dataset."""

    feature_column_names = 'FeatureColumnNames'
    label_column_name = 'LabelColumnName'
    weight_column_name = 'WeightColumnName'
    # Specifies how the raw input data looks like, can be used for generating inference examples
    raw_data_snapshot = 'RawDataSnapshot'

    @staticmethod
    def validate_dataset_metadata(dataset_metadata: Dict['DatasetMetadataKeys', Any]) -> List[str]:
        """
        Validate the Dataset metadata dictionary to check if the required fields are provided.

        :param dataset_metadata: mapping of dataset metadata keys and values
        :return:
        """
        errors = []  # type: List[str]
        missing_key_message = 'Dataset metadata was missing the field for: {}'
        if not dataset_metadata:
            errors.append('No Dataset metadata was provided. Required fields: {}'.
                          format(DatasetMetadataKeys._required_keys()))
            return errors

        for key in DatasetMetadataKeys._required_keys():
            if dataset_metadata.get(key, None) is None:
                errors.append(missing_key_message.format(key))

        return errors

    @staticmethod
    def _required_keys() -> List['DatasetMetadataKeys']:
        return [DatasetMetadataKeys.feature_column_names,
                DatasetMetadataKeys.label_column_name,
                DatasetMetadataKeys.raw_data_snapshot]


class StreamingDataset(DatasetBase):
    """Dataset that supports streaming data (data that may be too large to fit into memory)."""

    CLASS_LABELS_DONT_EXIST_ERROR = "Class labels only exist for classification datasets."
    MAX_ROWS_TO_SUBSAMPLE = 100000

    def __init__(self,
                 task: str,
                 training_data: dprep.Dataflow,
                 dataset_metadata: Dict[DatasetMetadataKeys, Any],
                 validation_data: Optional[dprep.Dataflow] = None,
                 y_min: Optional[float] = None,
                 y_max: Optional[float] = None,
                 featurization_transformer: Optional[Any] = None):
        """
        Initialize a StreamingDataset.

        :param task: Task type, e.g. 'Classification' or 'Regression'
        :param training_data:  The input training data as an AzureML Dataflow
        :param dataset_metadata: Meta information about the dataset, e.g. Label column name
        :param validation_data: The input validation data as an AzureML Dataflow
        :param y_min: min value of the label
        :param y_max: max value of the label
        :param featurization_transformer: An optional featurization transform to be applied to the data
        """
        dataset_metadata_validation_errors = DatasetMetadataKeys.validate_dataset_metadata(dataset_metadata)
        if dataset_metadata_validation_errors:
            raise DataException('Dataset metadata validation failed: {}'.format(dataset_metadata_validation_errors))

        self.training_data = training_data
        self._dataset_metadata = dataset_metadata
        self.feature_column_names = self._dataset_metadata[DatasetMetadataKeys.feature_column_names]
        self.label_column_name = self._dataset_metadata[DatasetMetadataKeys.label_column_name]
        self.raw_data_snapshot = self._dataset_metadata[DatasetMetadataKeys.raw_data_snapshot]
        self.weight_column_name = self._dataset_metadata.get(DatasetMetadataKeys.weight_column_name)

        self.validation_data = validation_data
        self.y_min = y_min
        self.y_max = y_max
        self._featurization_transformer = featurization_transformer

        self.task = task
        self.training_type = constants.TrainingType.TrainAndValidation
        if self.task == constants.Tasks.CLASSIFICATION:
            # this logic assumes that first MAX_ROWS_TO_SUBSAMPLE labels in train and test contain all labels.
            # note that this assumption MAY NOT ALWAYS HOLD TRUE. (for instance, a large dataset sorted by
            # label would invalidate this assumption.) if needed, a full set of labels could possibly be
            # extracted from the Dataflow's profile or the fit Nimbus pipeline
            self.train_class_labels = np.unique(self.get_y().
                                                drop_nulls(columns=[self.label_column_name]).
                                                head(StreamingDataset.MAX_ROWS_TO_SUBSAMPLE))
            valid_class_labels = np.unique(self.get_y_valid().
                                           drop_nulls(columns=[self.label_column_name]).
                                           head(StreamingDataset.MAX_ROWS_TO_SUBSAMPLE))
            self.class_labels = np.unique(np.concatenate((self.train_class_labels, valid_class_labels)))
        if self.task == constants.Tasks.REGRESSION:
            # convert y_valid to a numpy array
            # (we are assuming that y_valid is small enough to fit into memory)
            y_valid_dflow = self.get_y_valid()
            y_valid_np = y_valid_dflow.to_pandas_dataframe().iloc[:, 0].values

            self.bin_info = self.make_bin_info(y_valid_np.shape[0], y_valid_np)

    @property
    def dataset_metadata(self):
        """Get the dataset metadata."""
        return self._dataset_metadata

    def _get_raw_data_snapshot_str(self):
        """Get the data snapshot for the raw data."""
        return self.raw_data_snapshot

    def get_bin_info(self):
        """Get bin info."""
        return self.bin_info

    def get_X(self) -> dprep.Dataflow:
        """Get the feature columns of the training dataset."""
        return self.training_data.drop_columns([self.label_column_name, self.weight_column_name])

    def get_y(self) -> dprep.Dataflow:
        """Get the label column of the training dataset."""
        return self.training_data.keep_columns([self.label_column_name])

    def get_weight(self) -> dprep.Dataflow:
        """Get the weight column of the training dataset."""
        return self.training_data.keep_columns([self.weight_column_name]) \
            if self.weight_column_name is not None else None

    def get_X_valid(self) -> dprep.Dataflow:
        """Get the feature columns of the validation dataset."""
        return self.validation_data.drop_columns([self.label_column_name, self.weight_column_name]) \
            if self.validation_data is not None else None

    def get_y_valid(self) -> dprep.Dataflow:
        """Get the label column of the validation dataset."""
        return self.validation_data.keep_columns([self.label_column_name]) \
            if self.validation_data is not None else None

    def get_weight_valid(self) -> dprep.Dataflow:
        """Get the weight column of the validation dataset."""
        return self.validation_data.keep_columns([self.weight_column_name]) \
            if self.validation_data is not None and self.weight_column_name is not None else None

    def get_class_labels(self) -> np.ndarray:
        """Get the class labels for a classification task."""
        if self.task != constants.Tasks.CLASSIFICATION:
            raise DataException(StreamingDataset.CLASS_LABELS_DONT_EXIST_ERROR)
        return self.class_labels

    def get_is_sparse(self):
        """Dataset that supports streaming data (data that may be too large to fit into memory)."""
        return False

    def get_num_classes(self):
        """
        Get the number of classes in the dataset.

        :return:  number of classes
        """
        if self.task != constants.Tasks.CLASSIFICATION:
            raise DataException(StreamingDataset.CLASS_LABELS_DONT_EXIST_ERROR)
        return len(self.class_labels)

    def get_problem_info(self):
        """
        Get the ProblemInfo for the dataset.

        :return: _ProblemInfo
        """
        return ProblemInfo(is_sparse=False,
                           feature_column_names=self.feature_column_names,
                           label_column_name=self.label_column_name,
                           weight_column_name=self.weight_column_name,
                           enable_streaming=True)

    def get_subsampled_dataset(self, training_percent, random_state=None):
        """Get subsampled dataset."""
        # if random state is None, set it to an arbitrary fixed value. this ensures that
        # rows are consistent across sampled X, y, and weight Dataflow
        if random_state is None:
            random_state = randint(1, 1000)

        subsample_frac = training_percent / 100

        # subsample original data
        training_data = self.training_data.take_sample(subsample_frac, random_state)
        return StreamingDataset(
            self.task,
            training_data,
            self._dataset_metadata,
            self.validation_data)

    def get_train_class_labels(self):
        """Get the class labels from training data for a classification task."""
        if self.task != constants.Tasks.CLASSIFICATION:
            raise DataException(StreamingDataset.CLASS_LABELS_DONT_EXIST_ERROR)
        return self.train_class_labels

    def get_train_set(self):
        """Get the training part of the dataset."""
        return self.get_X(), self.get_y(), self.get_weight()

    def get_training_type(self):
        """
        Get training type.

        :return: str: training type
        """
        return constants.TrainingType.TrainAndValidation

    def get_transformers(self):
        """
        Get the transformers.

        :return: dict of transformers if success, else none
        """
        return {}

    def get_raw_data_type(self):
        """Return the raw data type."""
        return None

    def get_valid_set(self):
        """Get the validation part of the dataset."""
        return self.get_X_valid(), self.get_y_valid(), self.get_weight_valid()

    def get_y_transformer(self):
        """Get the y_transformer."""
        return None

    def get_y_range(self) -> Tuple[Optional[float], Optional[float]]:
        """
        Get the range of y values.

        :return: The y_min and y_max value.
        """
        return self.y_min, self.y_max

    def has_test_set(self):
        """Return true if the given dataset has test set available."""
        return False

    def get_preprocessor(self) -> Optional[Any]:
        """Return the preprocessor for this dataset, if any."""
        return self._featurization_transformer

    def get_preprocessor_pipeline_step(self) -> Optional[Tuple[str, Any]]:
        """
        Return the pre-processing pipeline for this Dataset, if any.

        :return: Pair consisting of the name of the pre-processor and the object
        """
        # The input dataset (X and y) are already transformed in this class
        if self._featurization_transformer is None:
            return None

        # This is Nimbus specific, and kinda weird to have in this file. This should be refactored out
        # to a more Nimbus specific place. Long term, DatasetTransformer shouldn't be used, once Dataflow's
        # map_partition() function is usable, this class should just be out of the business for handling
        # preprocessed pipelines

        # The training data in case of NimbusML will *not* be a featurized Dataflow, instead, we use the
        # pre-fitted transformation pipeline computed in the setup phase and tack that onto the learner.
        # DatasetTransformer is the glue that takes in a fitted transformation pipeline and passes the
        # transformed dataflow to the (NimbusML) learner
        return ('DatasetTransformer',
                DatasetTransformer(transform_model=self._featurization_transformer.pipeline.model))

    def clear_cache(self) -> bool:
        """Clear any temporary state left by this class."""
        # Nothing to clear here
        return True

    def is_timeseries(self) -> bool:
        """Check if this dataset is for timeseries."""
        # Since streaming is not supported for forecasting at the moment, always return False here
        return False

    def get_num_auto_cv_splits(self) -> Optional[int]:
        """Return the number of auto CV splits that are to be used for this dataset."""
        # No CV for streaming scenarios yet
        return None

    @contextmanager
    def open_dataset(self) -> Iterator[None]:
        """
        Load the dataset from the cache and then clean it up automatically (if cached).

        Note that any changes made to the dataset won't be reflected back. This is only intended for
        reading the underlying dataset, and caching it back to reduce memory consumption.
        Usage:
            with client_datasets.open_dataset():
                do_something_with_dataset()
        """
        yield

    def __getstate__(self):
        """Get a dictionary representing the object's current state (used for pickling)."""
        state = self.__dict__.copy()
        for key, value in state.items():
            if isinstance(value, dprep.Dataflow):
                state[key] = PickleableDataflow(value)
        return state

    def __setstate__(self, newstate):
        """Set the object's state based on a state dictionary (used for unpickling)."""
        for key, value in newstate.items():
            if isinstance(value, PickleableDataflow):
                newstate[key] = value.get_dataflow()
        self.__dict__.update(newstate)
