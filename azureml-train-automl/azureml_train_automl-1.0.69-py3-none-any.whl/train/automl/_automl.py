# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Global methods used during an automated machine learning iteration for both remote and local runs."""
import json
import logging
from typing import Optional, Union

import numpy as np
import pandas as pd
import scipy.sparse
from azureml.core import Run
from azureml.telemetry.activity import log_activity

import azureml.automl.core
from automl.client.core.common.types import DataInputType, DataSingleColumnInputType
from automl.client.core.runtime.cache_store import CacheStore
from automl.client.core.runtime import logging_utilities as runtime_logging_utilities
from azureml.automl.core import data_transformation, fit_pipeline as fit_pipeline_helper
from azureml.automl.core.automl_pipeline import AutoMLPipeline
from azureml.automl.core.data_context import RawDataContext, TransformedDataContext
from azureml.automl.core.streaming_data_context import StreamingTransformedDataContext
from . import _constants_azureml
from ._azureautomlruncontext import AzureAutoMLRunContext
from ._azureautomlsettings import AzureAutoMLSettings
from ._logging import get_logger
from .utilities import _check_if_y_label_has_single_frequency_class


def _subsampling_recommended(num_samples, num_features):
    """
    Recommend whether subsampling should be on or off based on shape of X.

    :param num_samples: Number of samples after preprocessing.
    :type num_samples: int
    :param num_features: Number of features after preprocessing.
    :type num_features: int
    :return: Flag indicate whether subsampling is recommended for given shape of X.
    :rtype: bool
    """
    # Ideally this number should be on service side.
    # However this number is proportional to the iteration overhead.
    # Which makes this specific number SDK specific.
    # For nativeclient or miroclient, this number will be different due to smaller overhead.
    # We will leave this here for now until we have a way of incorporating
    # hardware and network numbers in our model
    return num_samples * num_features > 300000000


def _set_problem_info(X: DataInputType,
                      y: DataSingleColumnInputType,
                      automl_settings: AzureAutoMLSettings,
                      current_run: Run,
                      transformed_data_context: Optional[Union[TransformedDataContext,
                                                         StreamingTransformedDataContext]] = None,
                      cache_store: Optional[CacheStore] = None,
                      is_adb_run: bool = False,
                      logger: Optional[logging.Logger] = None) -> None:
    """
    Set statistics about user data.

    :param X: The training features to use when fitting pipelines during AutoML experiment.
    :type X: pandas.DataFrame or numpy.ndarray or azureml.dataprep.Dataflow
    :param y: Training labels to use when fitting pipelines during AutoML experiment.
    :type y: pandas.DataFrame or numpy.ndarray or azureml.dataprep.Dataflow
    :param automl_settings: The AutoML settings to use.
    :type automl_settings: AzureAutoMLSettings
    :param current_run: The AutoMLRun to set the info for.
    :type current_run: azureml.core.run.Run
    :param transformed_data_context: Containing X, y and other transformed data info.
    :type transformed_data_context: TransformedDataContext or StreamingTransformedDataContext
    :param is_adb_run: flag whether this is a Azure Databricks run or not.
    :type is_adb_run: bool
    :param logger: the logger.
    :type logger: logging.logger
    :return: None
    """
    x_raw_column_names = None
    if isinstance(X, pd.DataFrame):
        x_raw_column_names = X.columns.values
    run_id = current_run._run_id
    if logger is not None and not automl_settings.enable_streaming:
        # logging X and y info
        runtime_logging_utilities.log_data_info(logger=logger, data_name="X", data=X, run_id=run_id)
        runtime_logging_utilities.log_data_info(logger=logger, data_name="y", data=y, run_id=run_id)

    if transformed_data_context is None:
        raw_data_context = RawDataContext(automl_settings_obj=automl_settings,
                                          X=X,
                                          y=y,
                                          x_raw_column_names=x_raw_column_names)

        transformed_data_context = \
            data_transformation.transform_data(raw_data_context=raw_data_context,
                                               cache_store=cache_store,
                                               is_onnx_compatible=automl_settings.enable_onnx_compatible_models,
                                               enable_dnn=automl_settings.enable_dnn,
                                               logger=logger,
                                               enable_streaming=automl_settings.enable_streaming)
    X = transformed_data_context.X
    y = transformed_data_context.y

    subsampling = automl_settings.enable_subsampling
    if subsampling is None:
        subsampling = _subsampling_recommended(X.shape[0], X.shape[1])

    problem_info_dict = {
        "dataset_num_categorical": 0,
        "is_sparse": scipy.sparse.issparse(X),
        "subsampling": subsampling
    }

    if automl_settings.enable_streaming:
        # Note: when using incremental learning, we are not calculating
        # some problem info properties that Miro may use for recommendation. It's uncertain at
        # this point whether these properties are needed
        problem_info_dict["dataset_features"] = X.head(1).shape[1]

        # If subsampling, set the number of dataset samples.
        # Note: when not subsampling, avoid this, because invoking Dataflow.shape
        # triggers Dataflow profile computation, which is expensive on large data
        if subsampling:
            problem_info_dict["dataset_samples"] = X.shape[0]
    else:
        problem_info_dict["dataset_classes"] = len(np.unique(y))
        problem_info_dict["dataset_features"] = X.shape[1]
        problem_info_dict["dataset_samples"] = X.shape[0]
        problem_info_dict['single_frequency_class_detected'] = \
            _check_if_y_label_has_single_frequency_class(automl_settings=automl_settings,
                                                         y=transformed_data_context.y,
                                                         logger=logger)
    problem_info_str = json.dumps(problem_info_dict)

    # This is required since token may expire
    if is_adb_run:
        current_run = Run.get_context()

    current_run.add_properties(
        {_constants_azureml.Properties.PROBLEM_INFO: problem_info_str})


def fit_pipeline(pipeline_script,
                 automl_settings,
                 X=None,
                 y=None,
                 sample_weight=None,
                 X_valid=None,
                 y_valid=None,
                 sample_weight_valid=None,
                 cv_splits_indices=None,
                 train_frac=1,
                 fit_iteration_parameters_dict=None,
                 experiment=None,
                 pipeline_id=None,
                 remote=True,
                 is_adb_run=False,
                 logger=None,
                 child_run_metrics=None,
                 transformed_data_context=None,
                 elapsed_time=None,
                 onnx_cvt=None):
    """
    Run a single iteration of an automated machine learning experiment. Note that this function is deprecated.

    This method is automatically called during a regular Automated Machine Learning
    experiment. fit_pipeline will evaluate the pipeline for this iteration, fit the pipeline with the provided data,
    calculate the various metrics relevant for this experiment, and log all the results in the specified Run's
    history.

    :param pipeline_script: serialized Pipeline returned from the server.
    :type pipeline_script: str
    :param automl_settings: User settings specified when creating AutoMLConfig.
    :type automl_settings: str or dict
    :param X: Input training data.
    :type X: numpy.ndarray or pandas.DataFrame
    :param y: Input training labels.
    :type y: numpy.ndarray or pandas.DataFrame
    :param sample_weight: Sample weights for training data.
    :type sample_weight: numpy.ndarray or pandas.DataFrame
    :param X_valid: validation data.
    :type X_valid: numpy.ndarray or pandas.DataFrame
    :param y_valid: validation labels.
    :type y_valid: numpy.ndarray or pandas.DataFrame
    :param sample_weight_valid: validation set sample weights.
    :type sample_weight_valid: numpy.ndarray or pandas.DataFrame
    :param cv_splits_indices: Custom indices by which to split the data when running cross validation.
    :type cv_splits_indices: numpy.ndarray or pandas.DataFrame
    :param train_frac: Fraction of training data to use, (0,1].
    :type train_frac: float
    :param fit_iteration_parameters_dict: Remaining data specific parameters for fit such as 'x_raw_column_names'.
    :type fit_iteration_parameters_dict: dict
    :param experiment: The azureml.core experiment.
    :type experiment: azureml.core.experiment.Experiment
    :param pipeline_id: Hash Id of current pipeline being evaluated.
    :type pipeline_id: str
    :param remote: flag whether this is a remote run or local run.
    :type remote: bool
    :param is_adb_run: flag whether this is a azure databricks run or not.
    :type is_adb_run: bool
    :param logger: logger for info/error messages.
    :param child_run_metrics: child run metrics
    :type child_run_metrics: run context
    :param transformed_data_context: Containing X, y and other transformed data info.
    :type transformed_data_context: TransformedDataContext or StreamingTransformedDataContext
    :param elapsed_time: How long this experiment has already taken in minutes
    :type elapsed_time: int
    :param onnx_cvt: The onnx converter.
    :type onnx_cvt: OnnxConverter
    :return: AzureML Run Properties for this child run
    :rtype: dict
    """
    if logger is None:
        logger = get_logger(automl_settings=automl_settings)
    logger.warning('fit_pipeline() is deprecated. It will be removed in a future release.')

    with log_activity(logger=logger, activity_name='fit_pipeline'):
        automl_settings_obj = AzureAutoMLSettings.from_string_or_dict(automl_settings, experiment=experiment)
        if fit_iteration_parameters_dict is None and transformed_data_context is None:
            fit_iteration_parameters_dict = {
                'X': X,
                'y': y,
                'X_valid': X_valid,
                'y_valid': y_valid,
                'sample_weight': sample_weight,
                'sample_weight_valid': sample_weight_valid,
                'cv_splits_indices': cv_splits_indices,
                'x_raw_column_names': None
            }
        if child_run_metrics is None and remote:
            child_run_metrics = Run.get_context()

        automl_run_context = AzureAutoMLRunContext(child_run_metrics, is_adb_run)
        automl_pipeline = AutoMLPipeline(automl_run_context, pipeline_script, pipeline_id, train_frac)

        return fit_pipeline_helper.fit_pipeline(
            automl_pipeline,
            automl_settings_obj,
            automl_run_context,
            fit_iteration_parameters_dict,
            remote,
            logger,
            transformed_data_context,
            elapsed_time,
            onnx_cvt).get_output_dict()
