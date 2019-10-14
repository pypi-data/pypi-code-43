# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Manages settings for AutoML experiments."""
from typing import Any, cast, Dict, List, Optional, Tuple, Union
import logging
import math
import os
import pkg_resources
import sys
import scipy

from sklearn.model_selection import train_test_split
from automl.client.core.common import constants
from automl.client.core.common.activity_logger import TelemetryActivityLogger
from automl.client.core.common.constants import ModelNameMappings, SupportedModelNames
from automl.client.core.common.exceptions import ConfigException
from automl.client.core.common.logging_utilities import _get_null_logger
from automl.client.core.common.utilities import get_primary_metrics
from automl.client.core.runtime import forecasting_models
from automl.client.core.runtime import model_wrappers
from automl.client.core.runtime.types import DataInputType, DataSingleColumnInputType
from automl.client.core.runtime.metrics import minimize_or_maximize
from azureml.automl.core.constants import FeaturizationConfigMode
from azureml.automl.core.faults_verifier import VerifierManager
from azureml.automl.core.featurization import FeaturizationConfig
from .onnx_convert import OnnxConvertConstants


class AutoMLBaseSettings:
    """Persist and validate settings for an AutoML experiment."""

    MAXIMUM_DEFAULT_ENSEMBLE_SELECTION_ITERATIONS = 15
    MINIMUM_REQUIRED_ITERATIONS_ENSEMBLE = 2

    # 525600 minutes = 1 year
    MAXIMUM_EXPERIMENT_TIMEOUT_MINUTES = 525600

    # 43200 minutes = 1 month
    MAXIMUM_ITERATION_TIMEOUT_MINUTES = 43200

    # 1073741824 MB = 1 PB
    MAXIMUM_MEM_IN_MB = 1073741824

    MAX_LAG_LENGTH = 2000
    MAX_N_CROSS_VALIDATIONS = 1000
    MAX_CORES_PER_ITERATION = 16384

    """
    TODO: Add the following bits back to AzureML SDK:
    - experiment
    - compute target
    - spark context
    """

    def __init__(self,
                 path: Optional[str] = None,
                 iterations: int = 100,
                 data_script: Optional[str] = None,
                 primary_metric: Optional[str] = None,
                 task_type: Optional[str] = None,
                 validation_size: Optional[float] = None,
                 n_cross_validations: Optional[int] = None,
                 y_min: Optional[float] = None,
                 y_max: Optional[float] = None,
                 num_classes: Optional[int] = None,
                 featurization: Union[str, FeaturizationConfig] = FeaturizationConfigMode.Off,
                 preprocess: bool = False,
                 lag_length: int = 0,
                 max_cores_per_iteration: int = 1,
                 max_concurrent_iterations: int = 1,
                 iteration_timeout_minutes: Optional[int] = None,
                 mem_in_mb: Optional[int] = None,
                 enforce_time_on_windows: bool = os.name == 'nt',
                 experiment_timeout_minutes: Optional[int] = None,
                 experiment_exit_score: Optional[float] = None,
                 blacklist_models: Optional[List[str]] = None,
                 whitelist_models: Optional[List[str]] = None,
                 exclude_nan_labels: bool = True,
                 verbosity: int = logging.INFO,
                 debug_log: str = 'automl.log',
                 debug_flag: Optional[Dict[str, Any]] = None,
                 enable_voting_ensemble: bool = True,
                 enable_stack_ensemble: bool = False,
                 ensemble_iterations: Optional[int] = None,
                 model_explainability: bool = False,
                 enable_tf: bool = True,
                 enable_cache: bool = True,
                 enable_subsampling: Optional[bool] = None,
                 subsample_seed: Optional[int] = None,
                 cost_mode: int = constants.PipelineCost.COST_NONE,
                 is_timeseries: bool = False,
                 enable_early_stopping: bool = False,
                 early_stopping_n_iters: int = 10,
                 enable_onnx_compatible_models: bool = False,
                 enable_feature_sweeping: bool = False,
                 enable_nimbusml: Optional[bool] = None,
                 enable_streaming: Optional[bool] = None,
                 label_column_name: Optional[str] = None,
                 weight_column_name: Optional[str] = None,
                 vm_type: Optional[str] = None,
                 **kwargs: Any):
        """
        Manage settings used by AutoML components.

        :param path: Full path to the project folder
        :param iterations: Number of different pipelines to test
        :param data_script: File path to the script containing get_data()
        :param primary_metric: The metric that you want to optimize.
        :param task_type: Field describing whether this will be a classification or regression experiment
        :param validation_size: What percent of the data to hold out for validation
        :param n_cross_validations: How many cross validations to perform
        :param y_min: Minimum value of y for a regression experiment
        :param y_max: Maximum value of y for a regression experiment
        :param num_classes: Number of classes in the label data
        :param featurization: Indicator for whether featurization step should be done automatically or not,
            or whether customized featurization should be used.
        :param preprocess: Flag whether AutoML should preprocess your data for you
        :param lag_length: How many rows to lag data when preprocessing time series data
        :param max_cores_per_iteration: Maximum number of threads to use for a given iteration
        :param max_concurrent_iterations:
            Maximum number of iterations that would be executed in parallel.
            This should be less than the number of cores on the AzureML compute. Formerly concurrent_iterations.
        :param iteration_timeout_minutes: Maximum time in seconds that each iteration before it terminates
        :param mem_in_mb: Maximum memory usage of each iteration before it terminates
        :param enforce_time_on_windows: flag to enforce time limit on model training at each iteration under windows.
        :param experiment_timeout_minutes: Maximum amount of time that all iterations combined can take
        :param experiment_exit_score:
            Target score for experiment. Experiment will terminate after this score is reached.
        :param blacklist_models: List of algorithms to ignore for AutoML experiment
        :param whitelist_models: List of model names to search for AutoML experiment
        :param exclude_nan_labels: Flag whether to exclude rows with NaN values in the label
        :param verbosity: Verbosity level for AutoML log file
        :param debug_log: File path to AutoML logs
        :param enable_voting_ensemble: Flag to enable/disable an extra iteration for Voting ensemble.
        :param enable_stack_ensemble: Flag to enable/disable an extra iteration for Stack ensemble.
        :param ensemble_iterations: Number of models to consider for the ensemble generation
        :param model_explainability: Flag whether to explain AutoML model
        :param enable_TF: Flag to enable/disable Tensorflow algorithms
        :param enable_cache: Flag to enable/disable disk cache for transformed, preprocessed data.
        :param enable_subsampling: Flag to enable/disable subsampling.
        :param subsample_seed: random_state used to sample the data.
        :param cost_mode: Flag to set cost prediction modes. COST_NONE stands for none cost prediction,
            COST_FILTER stands for cost prediction per iteration.
        :type cost_mode: int or automl.client.core.common.constants.PipelineCost
        :param is_timeseries: Flag whether AutoML should process your data as time series data.
        :type is_timeseries: bool
        :param enable_early_stopping: Flag whether the experiment should stop early if the score is not improving.
        :type enable_early_stopping: bool
        :param early_stopping_n_iters: The number of iterations to run in addition to landmark pipelines before
            early stopping kicks in.
        :type early_stopping_n_iters: int
        :param enable_onnx_compatible_models: Flag to enable/disable enforcing the onnx compatible models.
        :param enable_feature_sweeping: Flag to enable/disable feature sweeping.
        :param enable_nimbusml: Flag to enable/disable NimbusML transformers / learners.
        :param enable_streaming: Flag to enable/disable streaming.
        :param label_column_name: The name of the label column.
        :param weight_column_name: Name of the column corresponding to the sample weights.
        :param kwargs:
        """
        self.path = path

        self.iterations = iterations

        if primary_metric is None and task_type is None:
            raise ConfigException('One or both of primary metric and task type must be provided.')
        elif primary_metric is None and task_type is not None:
            self.task_type = task_type
            if task_type == constants.Tasks.CLASSIFICATION:
                self.primary_metric = constants.Metric.Accuracy
            elif task_type == constants.Tasks.REGRESSION:
                self.primary_metric = constants.Metric.Spearman
        elif primary_metric is not None and task_type is None:
            self.primary_metric = primary_metric
            if self.primary_metric in constants.Metric.REGRESSION_PRIMARY_SET:
                self.task_type = constants.Tasks.REGRESSION
            elif self.primary_metric in constants.Metric.CLASSIFICATION_PRIMARY_SET:
                self.task_type = constants.Tasks.CLASSIFICATION
            else:
                raise ConfigException("Invalid primary metric specified. Please use one of {0} for classification or "
                                      "{1} for regression.".format(constants.Metric.CLASSIFICATION_PRIMARY_SET,
                                                                   constants.Metric.REGRESSION_PRIMARY_SET))
        else:
            self.primary_metric = cast(str, primary_metric)
            self.task_type = cast(str, task_type)
            if self.primary_metric not in get_primary_metrics(self.task_type):
                raise ConfigException("Invalid primary metric specified for {0}. Please use one of: {1}".format(
                    self.task_type, get_primary_metrics(self.task_type)))

        self.data_script = data_script

        # TODO remove this once Miro/AutoML common code can handle None
        if validation_size is None:
            self.validation_size = 0.0
        else:
            self.validation_size = validation_size
        self.n_cross_validations = n_cross_validations

        self.y_min = y_min
        self.y_max = y_max

        self.num_classes = num_classes

        if isinstance(featurization, FeaturizationConfig):
            self.featurization = featurization.__dict__  # type: Union[str, Dict[str, Any]]
        else:
            self.featurization = featurization

        self.preprocess = preprocess
        self.lag_length = lag_length
        self.is_timeseries = is_timeseries

        self.max_cores_per_iteration = max_cores_per_iteration
        self.max_concurrent_iterations = max_concurrent_iterations
        self.iteration_timeout_minutes = iteration_timeout_minutes
        self.mem_in_mb = mem_in_mb
        self.enforce_time_on_windows = enforce_time_on_windows
        self.experiment_timeout_minutes = experiment_timeout_minutes
        self.experiment_exit_score = experiment_exit_score

        self.whitelist_models = self._filter_model_names_to_customer_facing_only(whitelist_models)
        self.blacklist_algos = self._filter_model_names_to_customer_facing_only(blacklist_models)
        self.supported_models = self._get_supported_model_names()

        self.auto_blacklist = True
        self.blacklist_samples_reached = False
        self.exclude_nan_labels = exclude_nan_labels

        self.verbosity = verbosity
        self.debug_log = debug_log
        self.show_warnings = False
        self.model_explainability = model_explainability
        self.service_url = None
        self.sdk_url = None
        self.sdk_packages = None

        self.enable_onnx_compatible_models = enable_onnx_compatible_models
        if self.enable_onnx_compatible_models:
            # Read the config of spliting the onnx models of the featurizer and estimator parts.
            enable_split_onnx_featurizer_estimator_models = kwargs.get(
                "enable_split_onnx_featurizer_estimator_models", False)
            self.enable_split_onnx_featurizer_estimator_models = enable_split_onnx_featurizer_estimator_models
        else:
            self.enable_split_onnx_featurizer_estimator_models = False

        self.enable_feature_sweeping = (not is_timeseries) and (
            not self.enable_onnx_compatible_models) and enable_feature_sweeping
        self.vm_type = vm_type

        # telemetry settings
        self.telemetry_verbosity = logging.getLevelName(logging.NOTSET)
        self.send_telemetry = False

        logger = self._get_logger()

        # enable/ disable neural networks for forecasting and natural language processing
        self.enable_dnn = kwargs.pop('enable_dnn', False)
        if self.task_type == constants.Tasks.CLASSIFICATION and self.enable_dnn and not self.preprocess:
            self.preprocess = True
            logger.info("Resetting AutoMLBaseSettings param preprocess=True required by DNNs for classification.")

        # time series settings
        if is_timeseries:
            self.time_column_name = kwargs.pop(constants.TimeSeries.TIME_COLUMN_NAME, None)
            grains = kwargs.pop(constants.TimeSeries.GRAIN_COLUMN_NAMES, None)
            wrong_grains_msg = "Wrong grain type: expected string, list of strings or None."
            if isinstance(grains, str):
                self.grain_column_names = [grains]  # type: Optional[List[str]]
            elif grains is None or isinstance(grains, list):
                if grains is not None:
                    for grain in grains:
                        if not isinstance(grain, str):
                            raise ConfigException(wrong_grains_msg)
                    if len(grains) == 0:
                        grains = None
                self.grain_column_names = grains
            else:
                raise ConfigException(wrong_grains_msg)
            self.drop_column_names = kwargs.pop(constants.TimeSeries.DROP_COLUMN_NAMES, None)
            self.max_horizon = kwargs.pop(constants.TimeSeries.MAX_HORIZON,
                                          constants.TimeSeriesInternal.MAX_HORIZON_DEFAULT)
            AutoMLBaseSettings.is_int_or_auto(self.max_horizon, constants.TimeSeries.MAX_HORIZON, False)
            self.dropna = False
            self.overwrite_columns = constants.TimeSeriesInternal.OVERWRITE_COLUMNS_DEFAULT
            self.transform_dictionary = constants.TimeSeriesInternal.TRANSFORM_DICT_DEFAULT
            self.window_size = kwargs.pop(constants.TimeSeries.TARGET_ROLLING_WINDOW_SIZE,
                                          constants.TimeSeriesInternal.WINDOW_SIZE_DEFDAULT)
            AutoMLBaseSettings.is_int_or_auto(self.window_size, constants.TimeSeries.TARGET_ROLLING_WINDOW_SIZE)
            self.country_or_region = kwargs.pop(constants.TimeSeries.COUNTRY_OR_REGION, None)
            # For backword compatible, keep country for a while
            # TODO: remove support for country parameter
            _country = kwargs.pop("country", None)
            if _country is not None:
                msg = "Parameter 'country' will be deprecated. Use 'country_or_region'"
                logging.warning(msg)  # print warning to console
                logger.warning(msg)  # print warning to logs
                self.country_or_region = _country

            lags = kwargs.pop(
                constants.TimeSeries.TARGET_LAGS,
                constants.TimeSeriesInternal.TARGET_LAGS_DEFAULT)  # type: Optional[Union[List[int], int]]
            type_error = (
                'Unsupported value of target_lags. rarget_lags must be integer, list of integers or \'{}\'.'
                .format(constants.TimeSeries.AUTO))
            if isinstance(lags, int) or isinstance(lags, list):
                if isinstance(lags, int):
                    target_lags = [lags]  # type: Optional[List[Union[int, str]]]
                else:
                    # Get unique values.
                    target_lags = list(set(lags))
                if target_lags == []:
                    target_lags = None
                elif target_lags is not None:  # This condition is required for mypy.
                    for lag in target_lags:
                        if not isinstance(lag, int):
                            raise ConfigException(type_error)
                        if lag < 1 or lag > AutoMLBaseSettings.MAX_LAG_LENGTH:
                            raise ConfigException(
                                "The {} must be between 1 and {} inclusive." .format(
                                    constants.TimeSeries.TARGET_LAGS,
                                    AutoMLBaseSettings.MAX_LAG_LENGTH))
            elif lags == constants.TimeSeries.AUTO:
                target_lags = [constants.TimeSeries.AUTO]
            elif lags is None:
                target_lags = None
            else:
                raise ConfigException(type_error)

            # Convert target lags to dictionary or None.
            if target_lags is not None:
                self.lags =\
                    {constants.TimeSeriesInternal.DUMMY_TARGET_COLUMN:
                     target_lags}  # type: Optional[Dict[str, List[Union[int, str]]]]
            else:
                self.lags = None
            seasonality_input = kwargs.pop(constants.TimeSeries.SEASONALITY,
                                           constants.TimeSeriesInternal.SEASONALITY_VALUE_DEFAULT)
            setattr(self, constants.TimeSeries.SEASONALITY, seasonality_input)
            stl_input = kwargs.pop(constants.TimeSeries.USE_STL,
                                   constants.TimeSeriesInternal.USE_STL_DEFAULT)
            setattr(self, constants.TimeSeries.USE_STL, stl_input)
            rm_insufficient = kwargs.pop(
                constants.TimeSeries.SHORT_SERIES_HANDLING,
                constants.TimeSeriesInternal.SHORT_SERIES_HANDLING_DEFAULT)
            setattr(self, constants.TimeSeries.SHORT_SERIES_HANDLING, rm_insufficient)

        # Early stopping settings
        self.enable_early_stopping = enable_early_stopping
        self.early_stopping_n_iters = early_stopping_n_iters

        if debug_flag:
            if 'service_url' in debug_flag:
                self.service_url = debug_flag['service_url']
            if 'show_warnings' in debug_flag:
                self.show_warnings = debug_flag['show_warnings']
            if 'sdk_url' in debug_flag:
                self.sdk_url = debug_flag['sdk_url']
            if 'sdk_packages' in debug_flag:
                self.sdk_packages = debug_flag['sdk_packages']

        # Deprecated param
        self.metrics = None

        # backward compatible settings
        old_voting_ensemble_flag = kwargs.pop("enable_ensembling", None)
        old_stack_ensemble_flag = kwargs.pop("enable_stack_ensembling", None)
        enable_voting_ensemble = \
            old_voting_ensemble_flag if old_voting_ensemble_flag is not None else enable_voting_ensemble
        enable_stack_ensemble = \
            old_stack_ensemble_flag if old_stack_ensemble_flag is not None else enable_stack_ensemble

        if self.enable_onnx_compatible_models:
            # disable Stack Ensemble until support for ONNX comes in
            enable_stack_ensemble = False

        total_ensembles = 0
        if enable_voting_ensemble:
            total_ensembles += 1
        if enable_stack_ensemble:
            total_ensembles += 1

        if self.iterations >= AutoMLBaseSettings.MINIMUM_REQUIRED_ITERATIONS_ENSEMBLE + total_ensembles:
            self.enable_ensembling = enable_voting_ensemble
            self.enable_stack_ensembling = enable_stack_ensemble
            if ensemble_iterations is not None:
                self.ensemble_iterations = ensemble_iterations  # type: Optional[int]
            else:
                self.ensemble_iterations = min(AutoMLBaseSettings.MAXIMUM_DEFAULT_ENSEMBLE_SELECTION_ITERATIONS,
                                               self.iterations)
        else:
            self.enable_ensembling = False
            self.enable_stack_ensembling = False
            self.ensemble_iterations = None

        self.enable_tf = enable_tf
        self.enable_cache = enable_cache
        # Deprecation warning for enable_cache, if set to False
        if not enable_cache:
            msg = (
                "Parameter 'enable_cache' will be deprecated. Azure blob store / local disk based "
                "caches for pre-processed and/or transformed data will always be preferred."
            )
            logging.warning(msg)  # print warning to console
            logger.warning(msg)  # print warning to logs
        self.enable_subsampling = enable_subsampling
        self.subsample_seed = subsample_seed
        self.enable_nimbusml = False if enable_nimbusml is None else enable_nimbusml
        self.enable_streaming = False if enable_streaming is None else enable_streaming
        # backward compatible settings
        old_streaming_flag = kwargs.pop("use_incremental_learning", None)
        self.enable_streaming = \
            old_streaming_flag if old_streaming_flag is not None else self.enable_streaming

        self.label_column_name = label_column_name
        self.weight_column_name = weight_column_name

        self.cost_mode = cost_mode
        self._verify_settings(logger)

        # Settings that need to be set after verification
        if self.task_type is not None and self.primary_metric is not None:
            self.metric_operation = minimize_or_maximize(
                task=self.task_type, metric=self.primary_metric)
        else:
            self.metric_operation = None

        # Show warnings for deprecating lag_length
        if lag_length != 0:
            msg = (
                "Parameter 'lag_length' will be deprecated. Reference "
                "time_series_settings in forecasting task to set it"
            )
            logging.warning(msg)  # print warning to console
            logger.warning(msg)  # print warning to logs

        # Deprecation of concurrent_iterations
        try:
            concurrent_iterations = kwargs.pop('concurrent_iterations')  # type: int
            msg = "Parameter 'concurrent_iterations' will be deprecated. Use 'max_concurrent_iterations'"
            logging.warning(msg)  # print warning to console
            logger.warning(msg)  # print warning to logs
            self.max_concurrent_iterations = concurrent_iterations
        except KeyError:
            pass

        # Deprecation of max_time_sec
        try:
            max_time_sec = kwargs.pop('max_time_sec')  # type: int
            msg = "Parameter 'max_time_sec' will be deprecated. Use 'iteration_timeout_minutes'"
            logging.warning(msg)  # print warning to console
            logger.warning(msg)  # print warning to logs
            if max_time_sec:
                self.iteration_timeout_minutes = math.ceil(max_time_sec / 60)
        except KeyError:
            pass

        # Deprecation of exit_time_sec
        try:
            exit_time_sec = kwargs.pop('exit_time_sec')  # type: int
            msg = "Parameter 'exit_time_sec' will be deprecated. Use 'experiment_timeout_minutes'"
            logging.warning(msg)  # print warning to console
            logger.warning(msg)  # print warning to logs
            if exit_time_sec:
                self.experiment_timeout_minutes = math.ceil(exit_time_sec / 60)
        except KeyError:
            pass

        # Deprecation of exit_score
        try:
            exit_score = kwargs.pop('exit_score')
            msg = "Parameter 'exit_score' will be deprecated. Use 'experiment_exit_score'"
            logging.warning(msg)  # print warning to console
            logger.warning(msg)  # print warning to logs
            self.experiment_exit_score = exit_score
        except KeyError:
            pass

        # Deprecation of blacklist_algos
        try:
            old_algos_param = kwargs.pop('blacklist_algos')
            # TODO: Re-enable this warning once we change everything to use blacklist_models
            # logging.warning("Parameter 'blacklist_algos' will be deprecated. Use 'blacklist_models.'")
            if self.blacklist_algos and old_algos_param is not None:
                self.blacklist_algos = self.blacklist_algos + \
                    self._filter_model_names_to_customer_facing_only(
                        list(set(old_algos_param) - set(self.blacklist_algos))
                    )
            else:
                self.blacklist_algos = self._filter_model_names_to_customer_facing_only(old_algos_param)
        except KeyError:
            pass

        for key, value in kwargs.items():
            if key not in self.__dict__.keys():
                msg = "Received unrecognized parameter: {0} {1}".format(key, value)
                logging.warning(msg)  # print warning to console
                logger.warning(msg)  # print warning to logs
            setattr(self, key, value)

    def _get_logger(self) -> TelemetryActivityLogger:
        from azureml.telemetry import AML_INTERNAL_LOGGER_NAMESPACE, get_telemetry_log_handler
        TELEMETRY_AUTOML_COMPONENT_KEY = 'automl'
        telemetry_handler = get_telemetry_log_handler(component_name=TELEMETRY_AUTOML_COMPONENT_KEY)
        from automl.client.core.common import __version__
        automl_core_sdk_version = pkg_resources.get_distribution("azureml-automl-core").version
        if self.is_timeseries:
            task_type = "forecasting"
        else:
            task_type = self.task_type
        custom_dimensions = {
            "common_core_version": __version__,
            "task_type": task_type,
            "automl_core_sdk_version": automl_core_sdk_version
        }

        logger = TelemetryActivityLogger(
            namespace=AML_INTERNAL_LOGGER_NAMESPACE,
            filename=self.debug_log,
            verbosity=self.verbosity,
            extra_handlers=[telemetry_handler],
            custom_dimensions=custom_dimensions)

        return logger

    def _verify_settings(self, logger=None):
        """
        Verify that input automl_settings are sensible.

        TODO (#357763): Reorganize the checks here and in AutoMLConfig and see what's redundant/can be reworked.

        :return:
        :rtype: None
        """
        if logger is None:
            logger = _get_null_logger()

        if self.validation_size is not None:
            if self.validation_size > 1.0 or self.validation_size < 0.0:
                raise ValueError(
                    "validation_size parameter must be between 0 and 1 when specified.")

        if self.n_cross_validations is not None:
            if not isinstance(self.n_cross_validations, int):
                raise ValueError('n_cross_validations must be an integer.')
            if self.n_cross_validations < 2 or self.n_cross_validations > AutoMLBaseSettings.MAX_N_CROSS_VALIDATIONS:
                raise ValueError('n_cross_validations must be between 2 to {} inclusive when specified.'
                                 .format(AutoMLBaseSettings.MAX_N_CROSS_VALIDATIONS))
            if self.enable_dnn:
                raise ConfigException('Deep neural networks (DNN) do not support cross-validation, '
                                      'please provide validation data or disable DNNs.')

        if self.iterations < 1 or self.iterations > constants.MAX_ITERATIONS:
            raise ValueError(
                'Number of iterations must be between 1 and {} inclusive.'.format(constants.MAX_ITERATIONS))

        if (self.enable_ensembling or self.enable_stack_ensembling) and self.ensemble_iterations < 1:
            raise ValueError(
                "When ensembling is enabled, the ensemble_iterations setting can't be less than 1")

        if (self.enable_ensembling or self.enable_stack_ensembling) and self.ensemble_iterations > self.iterations:
            raise ValueError(
                "When ensembling is enabled, the ensemble_iterations setting can't be greater than \
                the total number of iterations: {0}".format(self.iterations))

        if self.path is not None and not isinstance(self.path, str):
            raise ValueError('Input parameter \"path\" needs to be a string. '
                             'Received \"{0}\".'.format(type(self.path)))
        if not isinstance(self.preprocess, bool):
            raise ValueError('Input parameter \"preprocess\" needs to be a boolean. '
                             'Received \"{0}\".'.format(type(self.preprocess)))
        if self.max_cores_per_iteration is not None and self.max_cores_per_iteration != -1 and \
                (self.max_cores_per_iteration < 1 or
                 self.max_cores_per_iteration > AutoMLBaseSettings.MAX_CORES_PER_ITERATION):
            raise ValueError('Input parameter \"max_cores_per_iteration\" '
                             'needs to be -1 or between 1 and {} inclusive.'
                             .format(AutoMLBaseSettings.MAX_CORES_PER_ITERATION))
        if self.max_concurrent_iterations is not None and self.max_concurrent_iterations < 1:
            raise ValueError('Input parameter \"max_concurrent_iterations\" '
                             'needs to be greater or equal to 1, if set.')
        if self.iteration_timeout_minutes is not None and \
                (self.iteration_timeout_minutes < 1 or self.iteration_timeout_minutes >
                 AutoMLBaseSettings.MAXIMUM_ITERATION_TIMEOUT_MINUTES):
            raise ValueError('Input parameter \"iteration_timeout_minutes\" '
                             'needs to be between 1 and {} inclusive if set.'
                             .format(AutoMLBaseSettings.MAXIMUM_ITERATION_TIMEOUT_MINUTES))
        if self.mem_in_mb is not None and \
                (self.mem_in_mb < 1 or self.mem_in_mb > AutoMLBaseSettings.MAXIMUM_MEM_IN_MB):
            raise ValueError('Input parameter \"mem_in_mb\" '
                             'needs to be between 1 and {} if set.'.format(AutoMLBaseSettings.MAXIMUM_MEM_IN_MB))
        if self.enforce_time_on_windows is not None and not isinstance(self.enforce_time_on_windows, bool):
            raise ValueError('Input parameter \"enforce_time_on_windows\" needs to be a boolean if set. '
                             'Received \"{0}\".'.format(type(self.enforce_time_on_windows)))
        if self.experiment_timeout_minutes is not None and \
                (self.experiment_timeout_minutes < 1 or self.experiment_timeout_minutes >
                 AutoMLBaseSettings.MAXIMUM_EXPERIMENT_TIMEOUT_MINUTES):
            raise ValueError('Input parameter \"experiment_timeout_minutes\" '
                             'needs to be between 1 and {} if set.'
                             .format(AutoMLBaseSettings.MAXIMUM_EXPERIMENT_TIMEOUT_MINUTES))
        if self.blacklist_algos is not None and not isinstance(self.blacklist_algos, list):
            raise ValueError('Input parameter \"blacklist_algos\" needs to be a list of strings. '
                             'Received \"{0}\".'.format(type(self.blacklist_algos)))
        if not isinstance(self.exclude_nan_labels, bool):
            raise ValueError('Input parameter \"exclude_nan_labels\" needs to be a boolean. '
                             'Received \"{0}\".'.format(type(self.exclude_nan_labels)))
        if self.debug_log is not None and not isinstance(self.debug_log, str):
            raise ValueError('Input parameter \"debug_log\" needs to be a string filepath. '
                             'Received \"{0}\".'.format(type(self.debug_log)))
        if self.is_timeseries:
            if self.preprocess:
                logger.warning('Timeseries use its own preprocess, ignoring preprocess parameter.')
            if self.task_type == constants.Tasks.CLASSIFICATION:
                raise ValueError('Timeseries do not support classification yet.'
                                 'Received \"{0}\".'.format(type(self.task_type)))
            if self.time_column_name is None:
                raise ValueError('Timeseries need to set time column. ')
            if self.lag_length < 0 or self.lag_length > AutoMLBaseSettings.MAX_LAG_LENGTH:
                raise ValueError('Lag length must be between 0 and {} inclusive.'
                                 .format(AutoMLBaseSettings.MAX_LAG_LENGTH))

        if self.enable_onnx_compatible_models:
            if sys.version_info >= OnnxConvertConstants.OnnxIncompatiblePythonVersion:
                raise ConfigException('The ONNX package does not support Python 3.8, '
                                      'please use lower version of Python to get the ONNX model.')
            if self.is_timeseries:
                raise ValueError('Timeseries is not ONNX compatible, disable enable_onnx_compatible_models to run.')
            if self.enable_tf:
                raise ValueError(
                    'Tensorflow models are not ONNX compatible, disable enable_onnx_compatible_models to run.')

        if self.enable_subsampling and not isinstance(self.enable_subsampling, bool):
            raise ValueError('Input parameter \"enable_subsampling\" needs to be a boolean. '
                             'Received \"{0}\".'.format(type(self.enable_subsampling)))
        if not self.enable_subsampling and self.subsample_seed:
            msg = 'Input parameter \"enable_subsampling\" is set to False but \"subsample_seed\" was specified.'
            logging.warning(msg)  # print warning to console
            logger.warning(msg)  # print warning to logs
        if self.enable_subsampling and self.subsample_seed and not \
                isinstance(self.subsample_seed, int):
            raise ValueError('Input parameter \"subsample_seed\" needs to be an integer. '
                             'Received \"{0}\".'.format(type(self.subsample_seed)))

        if self.whitelist_models is not None:
            if len(self.whitelist_models) == 0:
                raise ConfigException('Input values for whitelist_models not recognized. Please use one of {}'.format(
                    self._get_supported_model_names()), target="whitelist_models")

        xgb_warning = 'XGBoost is included in recommended algorithms list but not installed locally. '\
            'If you would like to include XGBoost models in the recommended algorithms '\
            'please install XGBoost locally. Adding XGBoost to the blacklist.'
        xgbc = constants.SupportedModels.Classification.XGBoostClassifier
        xgbr = constants.SupportedModels.Regression.XGBoostRegressor

        # If xgboost is in whitelist but not installed, remove it and print a warning.
        if not model_wrappers.xgboost_present:
            if self.blacklist_algos is None:
                logger.warning(xgb_warning)
                if self.task_type == constants.Tasks.CLASSIFICATION:
                    self.blacklist_algos = [xgbc]
                else:
                    self.blacklist_algos = [xgbr]
            elif xgbc not in self.blacklist_algos and self.task_type == constants.Tasks.CLASSIFICATION:
                logger.warning(xgb_warning)
                self.blacklist_algos.append(xgbc)
            elif xgbr not in self.blacklist_algos:
                logger.warning(xgb_warning)
                self.blacklist_algos.append(xgbr)

        try:
            forecasting_models.ProphetModel._get_fbprophet()
        except ImportError:
            if self.blacklist_algos is None:
                self.blacklist_algos = [constants.SupportedModels.Forecasting.Prophet]
            elif constants.SupportedModels.Forecasting.Prophet not in self.blacklist_algos:
                self.blacklist_algos.append(constants.SupportedModels.Forecasting.Prophet)

        if self.blacklist_algos is not None:
            if all([model in self.blacklist_algos for model in self._get_supported_model_names()]):
                raise ConfigException('All models are blacklisted, please make sure at least one model is allowed')

        if self.blacklist_algos is not None and self.whitelist_models is not None:
            bla = set(self.blacklist_algos)
            wlm = set(self.whitelist_models)

            actual_wlm = wlm - bla
            shared = bla.intersection(wlm)

            if len(actual_wlm) == 0:
                raise ConfigException(
                    'blacklisted and whitelisted models are exactly the same. Found: {0}.'
                    'Please remove models from the blacklist or add models to the whitelist.'.format(wlm))
            if len(shared) > 0:
                logging.warning(
                    'blacklist and whitelist contain shared models.'
                    '{0} will be blacklisted.'.format(shared))

        if self.early_stopping_n_iters < 0:
            raise ValueError('The number of additional iterations for early stopping cannot be negative.')

        if self.model_explainability:
            try:
                import azureml.explain
            except ImportError:
                raise ConfigException('Please install azureml-explain-model package for model explanations')

    def _filter_model_names_to_customer_facing_only(self, model_names):
        if model_names is None:
            return None
        supported_model_names = self._get_supported_model_names()
        return [model for model in model_names if model
                in supported_model_names]

    def _get_supported_model_names(self):
        supported_model_names = []  # type: List[str]
        if self.task_type == constants.Tasks.CLASSIFICATION:
            supported_model_names = [model.customer_model_name for model in
                                     SupportedModelNames.SupportedClassificationModelList]
        elif self.task_type == constants.Tasks.REGRESSION:
            supported_model_names = [model.customer_model_name for model in
                                     SupportedModelNames.SupportedRegressionModelList]
        if self.is_timeseries:
            supported_model_names = [model.customer_model_name for model in
                                     SupportedModelNames.SupportedForecastingModelList]
        return supported_model_names

    @staticmethod
    def from_string_or_dict(val: Union[Dict[str, Any], str, 'AutoMLBaseSettings']) -> 'AutoMLBaseSettings':
        """
        Convert a string or dictionary containing settings to an AutoMLBaseSettings object.

        If the provided value is already an AutoMLBaseSettings object, it is simply passed through.

        :param val: the input data to convert
        :return: an AutoMLBaseSettings object
        """
        if isinstance(val, str):
            val = eval(val)
        if isinstance(val, dict):
            val = AutoMLBaseSettings(**val)

        if isinstance(val, AutoMLBaseSettings):
            return val
        else:
            raise ValueError("`input` parameter is not of type string or dict")

    def __str__(self):
        """
        Convert this settings object into human readable form.

        :return: a human readable representation of this object
        """
        output = [' - {0}: {1}'.format(k, v) for k, v in self.__dict__.items()]
        return '\n'.join(output)

    def _format_selective(self, black_list_keys):
        """
        Format selective items for logging.

        Returned string will look as follows below
        Example:
            - key1: value1
            - key2: value2

        :param black_list_keys: List of keys to ignore.
        :type black_list_keys: list(str)
        :return: Filterd settings as string
        :rtype: str
        """
        dict_copy = self._filter(black_list_keys=black_list_keys)
        output = [' - {0}: {1}'.format(k, v) for k, v in dict_copy.items()]
        return '\n'.join(output)

    def as_serializable_dict(self) -> Dict[str, Any]:
        return self._filter(['spark_context', 'logger'])

    def _filter(self, black_list_keys: Optional[List[str]]) -> Dict[str, Any]:
        return dict([(k, v) for k, v in self.__dict__.items()
                     if black_list_keys is None or k not in black_list_keys])

    def rule_based_validation(
            self,
            X: DataInputType = None,
            y: DataSingleColumnInputType = None,
            X_valid: DataInputType = None,
            y_valid: DataSingleColumnInputType = None,
            cv_splits_indices: Any = None,
            logger: Any = None,
            test_size: Optional[float] = constants.RuleBasedValidation.DEFAULT_TRAIN_VALIDATE_TEST_SIZE,
            random_state: Optional[int] = constants.RuleBasedValidation.DEFAULT_TRAIN_VALIDATE_RANDOM_STATE,
            verifier: Optional[VerifierManager] = None
    ) -> Tuple[DataInputType, DataSingleColumnInputType, DataInputType, DataSingleColumnInputType]:
        """
        Choose CV or train validation based on the data size.

        This will choose cv/ train validation based on the input data. And the AutoMLSettings will be changed.
        :param X: Training data.
        :type X: pandas.DataFrame or numpy.ndarray or scipy.sparse
        :param y: Training labels.
        :type y: pandas.DataFrame or numpy.ndarray or scipy.sparse
        :param X_valid: validation features.
        :type X_valid: pandas.DataFrame or numpy.ndarray
        :param y_valid: validation labels.
        :type y_valid: pandas.DataFrame or numpy.ndarray
        :param cv_splits_indices: Indices where to split training data for
        cross validation
        :type cv_splits_indices: list(int), or list(Dataflow) in which each Dataflow represent a train-valid set
                                 where 1 indicates record for training and 0
                                 indicates record for validation
        :param logger: the logger.
        :type logger: logger
        :param test_size: train validation test_size.
        :type test_size: float
        :param random_state: train validation random_state.
        :type random_state: int
        :return:
        """
        if logger is None:
            logger = _get_null_logger()
        if not self._is_rule_based_validation_needed(
                X_valid, self.n_cross_validations,
                cv_splits_indices, self.validation_size,
                self.is_timeseries
        ):
            logger.info("User has validation defined, no train rule based validation needed.")
            return X, y, X_valid, y_valid

        number_of_cv = self._get_cv_number(X)
        if number_of_cv > 1:  # As CV must be larger than 1, so 1 here means train valid split
            self.n_cross_validations = number_of_cv
            if verifier:
                verifier.update_data_verifier_for_cv(self.n_cross_validations)
            logger.info(
                "Rule based validation: Using rule based cv now with cv {}.".format(str(self.n_cross_validations))
            )
        else:
            logger.info("Rule based validation: Using rule based train/test splits.")
            # Using stratified split for classification. If the dataset cannot be split using
            # stratified split or the task type is regression, then using normal train test split.
            is_stratified = True
            if self.task_type == constants.Tasks.CLASSIFICATION:
                try:
                    X, X_valid, y, y_valid = train_test_split(
                        X, y, stratify=y, test_size=test_size, random_state=random_state)
                    logger.info("Rule based validation: Using stratified sampling.")
                except Exception:
                    is_stratified = False
                    logger.warning("Straified split meets exception {}".format(Exception))
                    logger.warning("Rule based validation: Stratified split failed. Fall to use random sampling.")
            if self.task_type == constants.Tasks.REGRESSION or not is_stratified:
                X, X_valid, y, y_valid = train_test_split(
                    X, y, test_size=test_size, random_state=random_state)
                logger.info("Rule based validation: Using random sampling.")

            if verifier:
                verifier.update_data_verifier_for_train_test_validation(X.shape[0], X_valid.shape[0])

        return X, y, X_valid, y_valid

    @staticmethod
    def is_int_or_auto(val: Optional[Any], val_name: str, allow_none: bool = True) -> None:
        """
        Raise a ConfigExceprion if value is not 'auto' or integer.

        :param val: The value to test.
        :param val_name: the name of a value to be displayed in the error message.
        :param allow_none: if true, the None value is allowed for val.
        :raises: ConfigException
        """
        if allow_none and val is None:
            return
        if not isinstance(val, int) and val != constants.TimeSeries.AUTO:
            raise ConfigException(
                exception_message='Unsupported value of {}. {} must be integer or \'{}\'.'.format(
                    val_name, val_name, constants.TimeSeries.AUTO),
                target=val_name)

    @staticmethod
    def _is_rule_based_validation_needed(
            X_valid: DataInputType,
            n_cross_validations: Optional[int] = None,
            cv_splits_indices: Optional[Any] = None,
            validation_size: Optional[float] = None,
            is_timeseries: Optional[bool] = None
    ) -> bool:
        """
        Check whether user input need automated validation settings.

        This function will be true if user has no input validation settings and the training is not timeseries.
        """
        is_needed = not is_timeseries
        is_needed = is_needed and X_valid is None and (validation_size is None or validation_size == 0.0)
        is_needed = is_needed and n_cross_validations is None and cv_splits_indices is None
        return is_needed

    @staticmethod
    def _get_cv_number(X: DataInputType) -> int:
        """Return the number of cross validation is needed. If is 1 using train test splits."""
        if scipy.sparse.issparse(X):
            return constants.RuleBasedValidation.SPARSE_N_CROSS_VALIDATIONS
        for rule in constants.RuleBasedValidation.VALIDATION_LIMITS_NO_SPARSE:
            if X.shape[0] >= rule.LOWER_BOUND and X.shape[0] < rule.UPPER_BOUND:
                return rule.NUMBER_OF_CV
        # by default return constants.RuleBasedValidation.DEFAULT_N_CROSS_VALIDATIONS
        return constants.RuleBasedValidation.DEFAULT_N_CROSS_VALIDATIONS
