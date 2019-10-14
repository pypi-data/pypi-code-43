# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""AutoML object in charge of orchestrating various AutoML runs for predicting models."""
import json
import logging
import os
import os.path
import sys
import warnings
from datetime import datetime
from typing import Any, cast, List, Optional, Dict, Union
from types import ModuleType
from pathlib import Path
import shutil

import math
import numpy as np
import pandas as pd
import pytz
import sklearn
from azureml._restclient.jasmine_client import JasmineClient
from azureml._restclient.experiment_client import ExperimentClient
from azureml._restclient.models.create_parent_run_dto import CreateParentRunDto
from azureml._restclient.service_context import ServiceContext
from azureml.core import Experiment
from azureml.core import Run
from azureml.core._serialization_utils import _serialize_to_dict
from azureml.core.compute_target import AbstractComputeTarget
from azureml.core.runconfig import RunConfiguration
from azureml.exceptions import ServiceException as AzureMLServiceException
from azureml.telemetry import get_diagnostics_collection_info, is_diagnostics_collection_info_available
from azureml.telemetry.activity import log_activity
from msrest.exceptions import HttpOperationError

from automl.client.core.common import logging_utilities
from automl.client.core.common import utilities as common_utilities
from automl.client.core.common.constants import TelemetryConstants
from .exceptions import (ClientException,
                         DataException,
                         ConfigException,
                         ServiceException,
                         ModelFitException)
from automl.client.core.common.exceptions import ErrorTypes
from automl.client.core.common.limit_function_call_exceptions import TimeoutException
from automl.client.core.common.logging_utilities import BLACKLISTED_LOGGING_KEYS
from automl.client.core.runtime import memory_utilities
from automl.client.core.runtime import model_wrappers
from automl.client.core.runtime import pipeline_spec
from automl.client.core.runtime import utilities as runtime_utilities
from automl.client.core.runtime.cache_store import CacheStore
from azureml.automl.core import data_transformation
from azureml.automl.core import dataprep_utilities
from azureml.automl.core import dataset_utilities
from azureml.automl.core import fit_pipeline as fit_pipeline_helper
from azureml.automl.core import training_utilities
from azureml.automl.core._experiment_observer import ExperimentStatus
from azureml.automl.core.automl_pipeline import AutoMLPipeline
from azureml.automl.core.console_interface import ConsoleInterface
from azureml.automl.core.data_context import RawDataContext
from azureml.automl.core.data_context import TransformedDataContext
from azureml.automl.core.streaming_data_context import StreamingTransformedDataContext
from azureml.automl.core.faults_verifier import VerifierManager
from azureml.automl.core.onnx_convert import OnnxConverter, OnnxConvertConstants
from azureml.automl.core.systemusage_telemetry import SystemResourceUsageTelemetryFactory
from . import _automl, constants
from ._adb_driver_node import _AdbDriverNode
from ._adb_run_experiment import adb_run_experiment
from ._automl_feature_config_manager import AutoMLFeatureConfigManager
from ._azure_experiment_observer import AzureExperimentObserver
from ._azureautomlruncontext import AzureAutoMLRunContext
from ._azureautomlsettings import AzureAutoMLSettings
from ._cachestorefactory import CacheStoreFactory
from ._constants_azureml import ContinueFlagStates
from ._environment_utilities import log_user_sdk_dependencies, modify_run_configuration
from ._logging import get_logger, TELEMETRY_AUTOML_COMPONENT_KEY
from ._remote_console_interface import RemoteConsoleInterface
from .automl_adb_run import AutoMLADBRun
from .exceptions import ValidationException
from .run import AutoMLRun
from .automl_explain_utilities import _automl_perform_best_run_explain_model
from .utilities import friendly_http_exception, _get_package_version, _load_user_script


class AzureAutoMLClient:
    """Client to run AutoML experiments on Azure Machine Learning platform."""

    # Caches for querying and printing child runs
    run_map = {}
    metric_map = {}
    properties_map = {}

    def __init__(self, experiment: Experiment, settings: AzureAutoMLSettings):
        """
        Create an AzureAutoMLClient.

        :param settings: the AutoML settings to use
        """
        self.automl_settings = settings
        self.experiment = experiment

        self._status = constants.Status.NotStarted
        self._loop = None
        self._score_max = None
        self._score_min = None
        self._score_best = None
        self._console_logger = open(os.devnull, "w")

        self.parent_run_id = None   # type: Optional[str]
        self.current_iter = None
        self.input_data = None      # type: Optional[Dict[str, Union[Any, Any]]]
        self._adb_thread = None
        self.onnx_cvt = None        # type: Optional[OnnxConverter]

        self._check_create_folders(self.automl_settings.path)

        telemetry_set_by_user = True
        # turn on default telemetry collection, if user is not set
        if not is_diagnostics_collection_info_available():
            telemetry_set_by_user = False

        self.logger = get_logger(
            self.automl_settings.debug_log,
            self.automl_settings.verbosity,
            automl_settings=self.automl_settings)

        if not telemetry_set_by_user:
            self.logger.info("Telemetry collection is not set, turning it on by default.")

        send_telemetry, level = get_diagnostics_collection_info(component_name=TELEMETRY_AUTOML_COMPONENT_KEY)
        self.automl_settings.telemetry_verbosity = level
        self.automl_settings.send_telemetry = send_telemetry
        self._usage_telemetry = SystemResourceUsageTelemetryFactory.get_system_usage_telemetry(
            self.logger)
        self._usage_telemetry.start()

        self.experiment_start_time = None

        if not self.automl_settings.show_warnings:
            # sklearn forces warnings, so we disable them here
            warnings.simplefilter('ignore', DeprecationWarning)
            warnings.simplefilter('ignore', RuntimeWarning)
            warnings.simplefilter('ignore', UserWarning)
            warnings.simplefilter('ignore', FutureWarning)
            warnings.simplefilter('ignore', sklearn.exceptions.UndefinedMetricWarning)

        # Setup the user script.
        self._setup_data_script()

        # Set up clients to communicate with AML services
        self._jasmine_client = JasmineClient(self.experiment.workspace.service_context, self.experiment.name,
                                             host=self.automl_settings.service_url)
        self.feature_config_manager = AutoMLFeatureConfigManager(self._jasmine_client, self.logger)
        self.experiment_client = ExperimentClient(self.experiment.workspace.service_context, self.experiment.name,
                                                  host=self.automl_settings.service_url)

        self.current_run = None     # type: Optional[AutoMLRun]

    def __del__(self):
        """Clean up AutoML loggers and close files."""
        try:
            logging_utilities.cleanup_log_map(self.automl_settings.debug_log,
                                              self.automl_settings.verbosity)

            if self._usage_telemetry is not None:
                self._usage_telemetry.stop()
        except Exception:
            # last chance, nothing can be done, so ignore any exception
            pass

    def cancel(self):
        """
        Cancel the ongoing local run.

        :return: None
        """
        self._status = constants.Status.Terminated

    def fit(self,
            run_configuration: Optional[RunConfiguration] = None,
            compute_target: Optional[AbstractComputeTarget] = None,
            X: Optional[Any] = None,
            y: Optional[Any] = None,
            sample_weight: Optional[Any] = None,
            X_valid: Optional[Any] = None,
            y_valid: Optional[Any] = None,
            sample_weight_valid: Optional[Any] = None,
            cv_splits_indices: Optional[List[Any]] = None,
            show_output: bool = False,
            existing_run: bool = False,
            training_data: Optional[Any] = None,
            validation_data: Optional[Any] = None,
            _script_run: Optional[Run] = None,
            kwargs: Optional[Dict[str, Any]] = None) -> AutoMLRun:
        """
        Start a new AutoML execution on the specified compute target.

        :param run_configuration: The run confiuguration used by AutoML, should contain a compute target for remote
        :type run_configuration: Azureml.core RunConfiguration
        :param compute_target: The AzureML compute node to run this experiment on
        :type compute_target: azureml.core.compute.AbstractComputeTarget
        :param X: Training features
        :type X: pandas.DataFrame or numpy.ndarray or azureml.dataprep.Dataflow or
                 azureml.core.Dataset, azureml.data.dataset_definition.DatasetDefinition
                 or azureml.data.TabularDataset
        :param y: Training labels
        :type y: pandas.DataFrame or numpy.ndarray or azureml.dataprep.Dataflow or
                 azureml.core.Dataset, azureml.data.dataset_definition.DatasetDefinition
                 or azureml.data.TabularDataset
        :param sample_weight:
        :type sample_weight: pandas.DataFrame or numpy.ndarray or azureml.dataprep.Dataflow
                or azureml.data.TabularDataset
        :param X_valid: validation features
        :type X_valid: pandas.DataFrame or numpy.ndarray or azureml.dataprep.Dataflow or
                   azureml.core.Dataset, azureml.data.dataset_definition.DatasetDefinition
                   or azureml.data.TabularDataset
        :param y_valid: validation labels
        :type y_valid: pandas.DataFrame or numpy.ndarray or azureml.dataprep.Dataflow or
                   azureml.core.Dataset, azureml.data.dataset_definition.DatasetDefinition
                   or azureml.data.TabularDataset
        :param sample_weight_valid: validation set sample weights
        :type sample_weight_valid: pandas.DataFrame or numpy.ndarray or azureml.dataprep.Dataflow
                or azureml.data.TabularDataset
        :param cv_splits_indices: Indices where to split training data for cross validation
        :type cv_splits_indices: list(int), or list(Dataflow) in which each Dataflow represent a train-valid set
                                 where 1 indicates record for training and 0 indicates record for validation
        :param show_output: Flag whether to print output to console
        :type show_output: bool
        :param existing_run: Flag whether this is a continuation of a previously completed experiment
        :type existing_run: bool
        :param _script_run: Run to associate with parent run id
        :type _script_run: azureml.core.Run
        :return: AutoML parent run
        :rtype: azureml.train.automl.AutoMLRun
        """
        self._status = constants.Status.Started

        if show_output:
            self._console_logger = sys.stdout

        if run_configuration is None:
            run_configuration = RunConfiguration()
            if compute_target is not None:
                run_configuration.name = compute_target.name
                self._console_logger.write('No run_configuration provided, running on {0} with default configuration\n'
                                           .format(compute_target.name))
            else:
                self._console_logger.write(
                    'No run_configuration provided, running locally with default configuration\n')
            run_configuration.environment.docker.enabled = True

        if run_configuration.framework.lower() != 'python':
            raise ConfigException('AutoML requires the run configuration framework to be set to "Python".')

        self.automl_settings.compute_target = run_configuration.target

        # Save the Dataset to Workspace so that its saved id will be logged for telemetry and lineage
        dataset_utilities.ensure_saved(
            self.experiment.workspace, X, y, sample_weight, X_valid, y_valid, sample_weight_valid, training_data,
            validation_data
        )

        dataset_utilities.collect_usage_telemetry(
            compute=run_configuration.target, spark_context=self.automl_settings.spark_context,
            X=X, y=y, sample_weight=sample_weight, X_valid=X_valid, y_valid=y_valid,
            sample_weight_valid=sample_weight_valid, training_data=training_data, validation_data=validation_data
        )

        X, y, sample_weight, X_valid, y_valid, sample_weight_valid = dataset_utilities.convert_inputs(
            X, y, sample_weight, X_valid,
            y_valid, sample_weight_valid
        )

        training_data, validation_data = dataset_utilities.convert_inputs_dataset(
            training_data,
            validation_data
        )

        try:
            if self.automl_settings.spark_context:
                self._init_adb_driver_run(run_configuration=run_configuration, X=X, y=y, sample_weight=sample_weight,
                                          X_valid=X_valid, y_valid=y_valid, sample_weight_valid=sample_weight_valid,
                                          cv_splits_indices=cv_splits_indices, show_output=show_output)
            elif run_configuration.target == 'local':
                if self.automl_settings.path is None:
                    self.automl_settings.path = '.'
                name = run_configuration._name if run_configuration._name else "local"
                run_configuration.save(self.automl_settings.path, name)
                self._console_logger.write('Running on local machine\n')
                self._fit_local(X=X, y=y, sample_weight=sample_weight, X_valid=X_valid, y_valid=y_valid,
                                cv_splits_indices=cv_splits_indices,
                                existing_run=existing_run, sample_weight_valid=sample_weight_valid,
                                training_data=training_data, validation_data=validation_data, _script_run=_script_run)
            else:
                self._console_logger.write('Running on remote compute: ' + str(run_configuration.target) + '\n')
                self.automl_settings.debug_log = "azureml_automl.log"
                self._fit_remote(run_configuration, X=X, y=y, sample_weight=sample_weight,
                                 X_valid=X_valid, y_valid=y_valid, sample_weight_valid=sample_weight_valid,
                                 cv_splits_indices=cv_splits_indices, show_output=show_output,
                                 training_data=training_data, validation_data=validation_data)
        except Exception as e:
            self._fail_parent_run(error_details=e,
                                  logger=self.logger)
            raise
        assert self.current_run is not None
        return self.current_run

    def _setup_data_script(self) -> None:
        module_path = self.automl_settings.data_script
        if self.automl_settings.data_script is not None:
            # Show warnings to user when use the data_script.
            warnings.warn('Please make sure in the data script the data script '
                          'uses the paths of data files on the remote machine.'
                          'The data script is not recommended anymore, '
                          'please take a look at the latest documentation to use the dprep interface.')

            if self.automl_settings.path is None:
                raise ConfigException('Please set the path (the project folder) in AutoMLConfig.')

            is_data_script_in_proj_dir = True
            if not os.path.exists(self.automl_settings.data_script):
                # Check if the data_script is a relative sub path from the project path (automl_settings.path)
                script_path = os.path.join(self.automl_settings.path, self.automl_settings.data_script)
                if os.path.exists(script_path):
                    module_path = script_path
                else:
                    raise ConfigException("Could not find data script with name '{0}' or '{1}'."
                                          .format(self.automl_settings.data_script, script_path))
            else:
                # Check if the data_script path is under the project path or it's sub folders.
                try:
                    path_script = Path(self.automl_settings.data_script)
                    path_project = Path(self.automl_settings.path)
                    if path_project not in path_script.parents:
                        is_data_script_in_proj_dir = False
                except Exception:
                    is_data_script_in_proj_dir = False
                module_path = self.automl_settings.data_script

            # Check if the data_script path is actually a file path.
            if not os.path.isfile(module_path):
                raise ConfigException("The provided user script path '{0}' is not a file."
                                      .format(self.automl_settings.data_script))

            # Make sure the script_path (the data script path) has the script file named as DATA_SCRIPT_FILE_NAME.
            module_file_name = os.path.basename(module_path)
            if module_file_name != constants.DATA_SCRIPT_FILE_NAME:
                raise ConfigException("The data script file name '{}' is incorrect, please use '{}'."
                                      .format(module_file_name, constants.DATA_SCRIPT_FILE_NAME))

            # If data_script is not in project folder, copy the data_script file into the project folder.
            # We'll take the snapshot of the project folder.
            if not is_data_script_in_proj_dir:
                # Need to copy the data script file.
                des_module_path = os.path.join(self.automl_settings.path, constants.DATA_SCRIPT_FILE_NAME)
                shutil.copy(os.path.abspath(module_path), des_module_path)
                module_path = des_module_path

            try:
                self.user_script = _load_user_script(module_path, self.logger)  # type: Optional[ModuleType]
                self.input_data = training_utilities._extract_user_data(self.user_script)
                training_utilities.auto_blacklist(self.input_data, self.automl_settings)
                if self.automl_settings.exclude_nan_labels:
                    self.input_data = runtime_utilities._y_nan_check(self.input_data)
            except ConfigException:
                raise
            except Exception as e:
                self.logger.warning('Failed to load user script ({}), skipping.'.format(e))
                self.user_script = None
        else:
            self.user_script = None

    def _init_adb_driver_run(self,
                             run_configuration: Optional[RunConfiguration] = None,
                             X: Optional[Any] = None,
                             y: Optional[Any] = None,
                             sample_weight: Optional[Any] = None,
                             X_valid: Optional[Any] = None,
                             y_valid: Optional[Any] = None,
                             sample_weight_valid: Optional[Any] = None,
                             cv_splits_indices: Optional[List[Any]] = None,
                             show_output: bool = False,
                             existing_run: bool = False) -> None:

        self._console_logger.write(
            'Running an experiment on spark cluster: {0}.\n'.format(self.automl_settings.name))

        # Forecasting runs will fail if caching is turned off (ADB only)
        if self.automl_settings.is_timeseries and not self.automl_settings.enable_cache:
            raise ConfigException(
                'Time-series forecasting requires `enable_cache=True` on spark cluster.')

        try:
            if not existing_run:
                self._fit_remote_core(run_configuration, X=X, y=y, sample_weight=sample_weight, X_valid=X_valid,
                                      y_valid=y_valid, sample_weight_valid=sample_weight_valid,
                                      cv_splits_indices=cv_splits_indices)
            # This should be refactored to have RunHistoryClient and make call on it to get token
            assert self.current_run is not None
            token_res = self.experiment_client._client.run.\
                get_token(experiment_name=self.automl_settings.name,
                          resource_group_name=self.automl_settings.resource_group,
                          subscription_id=self.automl_settings.subscription_id,
                          workspace_name=self.automl_settings.workspace_name,
                          run_id=self.current_run.run_id)
            aml_token = token_res.token
            aml_token_expiry = token_res.expiry_time_utc

            service_context = ServiceContext(
                subscription_id=self.automl_settings.subscription_id,
                resource_group_name=self.automl_settings.resource_group,
                workspace_name=self.automl_settings.workspace_name,
                workspace_id=self.experiment.workspace._workspace_id,
                authentication=self.experiment.workspace._auth_object)

            run_history_url = service_context._get_run_history_url()
            fn_script = None
            if self.automl_settings.data_script:
                with open(self.automl_settings.data_script, "r") as f:
                    fn_script = f.read()

            dataprep_json = dataprep_utilities.get_dataprep_json(
                X=X,
                y=y,
                sample_weight=sample_weight,
                X_valid=X_valid,
                y_valid=y_valid,
                sample_weight_valid=sample_weight_valid,
                cv_splits_indices=cv_splits_indices)
            # build dictionary of context
            assert self.current_run is not None
            run_context = {"subscription_id": self.automl_settings.subscription_id,
                           "resource_group": self.automl_settings.resource_group,
                           "location": self.experiment.workspace.location,
                           "workspace_name": self.automl_settings.workspace_name,
                           "experiment_name": self.automl_settings.name,
                           "parent_run_id": self.current_run.run_id,
                           "aml_token": aml_token,
                           "aml_token_expiry": aml_token_expiry,
                           "service_url": run_history_url,
                           "automl_settings_str": json.dumps(self.automl_settings.as_serializable_dict()),
                           'dataprep_json': dataprep_json,
                           "get_data_content": fn_script}
            adb_automl_context = [(index, run_context) for index in range(
                0, self.automl_settings.max_concurrent_iterations)]

            if not hasattr(self.automl_settings, 'is_run_from_test'):
                adb_thread = _AdbDriverNode("AutoML on Spark Experiment: {0}".format(self.experiment.name),
                                            adb_automl_context,
                                            self.automl_settings.spark_context,
                                            self.automl_settings.max_concurrent_iterations,
                                            self.current_run.run_id)
                adb_thread.start()
                self.current_run = AutoMLADBRun(self.experiment, self.parent_run_id, adb_thread)
            else:
                automlRDD = self.automl_settings.\
                    spark_context.parallelize(adb_automl_context,
                                              self.automl_settings.max_concurrent_iterations)
                automlRDD.map(adb_run_experiment).collect()

            if show_output:
                RemoteConsoleInterface._show_output(self.current_run,
                                                    self._console_logger,
                                                    self.logger,
                                                    self.automl_settings.primary_metric)
        except Exception as ex:
            logging_utilities.log_traceback(ex, self.logger)
            raise

    def _create_parent_run_for_local(self, X=None, y=None, sample_weight=None, X_valid=None, y_valid=None,
                                     sample_weight_valid=None, cv_splits_indices=None, existing_run=False,
                                     training_data=None, validation_data=None, verifier=None, _script_run=None):
        """
        Create parent run in Run History containing AutoML experiment information.

        :return: AutoML parent run
        :rtype: azureml.train.automl.AutoMLRun
        """
        #  Prepare data before entering for loop
        self.logger.info("Extracting user Data")
        self.input_data = training_utilities.format_training_data(
            X, y, sample_weight, X_valid, y_valid, sample_weight_valid,
            cv_splits_indices=cv_splits_indices, user_script=self.user_script,
            training_data=training_data, validation_data=validation_data,
            label_column_name=self.automl_settings.label_column_name,
            weight_column_name=self.automl_settings.weight_column_name,
            automl_settings=self.automl_settings,
            logger=self.logger, is_adb_run=True,
            verifier=verifier)

        training_utilities.validate_training_data_dict(self.input_data, self.automl_settings, check_sparse=True)
        training_utilities.auto_blacklist(self.input_data, self.automl_settings)
        if self.automl_settings.exclude_nan_labels:
            self.input_data = runtime_utilities._y_nan_check(self.input_data)
        training_utilities.set_task_parameters(self.input_data.get('y'), self.automl_settings)

        if not existing_run:
            parent_run_dto = self._create_parent_run_dto(constants.ComputeTargets.LOCAL)

            try:
                self.logger.info("Start creating parent run with DTO: {0}."
                                 .format(self.automl_settings._format_selective(BLACKLISTED_LOGGING_KEYS)))
                self.parent_run_id = self._jasmine_client.post_parent_run(parent_run_dto)
                self.logger.update_default_property('parent_run_id', self.parent_run_id)
            except (AzureMLServiceException, HttpOperationError) as e:
                logging_utilities.log_traceback(e, self.logger)
                friendly_http_exception(e, constants.API.CreateParentRun)
            except Exception as e:
                logging_utilities.log_traceback(e, self.logger)
                raise ClientException(
                    "Error when trying to create parent run in automl service") from None
            if _script_run is not None:
                _script_run.add_properties({"automl_id": self.parent_run_id})
            self.current_run = AutoMLRun(self.experiment,
                                         self.parent_run_id,
                                         host=self.automl_settings.service_url)
            # TODO: Remove with task 416022
            self._add_display_task()
            # only log user sdk dependencies on initial parent creation
            log_user_sdk_dependencies(self.current_run, self.logger)

        else:
            self.current_run = AutoMLRun(self.experiment,
                                         self.parent_run_id,
                                         host=self.automl_settings.service_url)

        if self.user_script:
            self.logger.info("[ParentRunID:{}] Local run using user script.".format(self.parent_run_id))
        else:
            self.logger.info("[ParentRunID:{}] Local run using input X and y.".format(self.parent_run_id))

        self._console_logger.write("Parent Run ID: {}\n".format(self.parent_run_id))
        self.logger.info("Parent Run ID: " + self.parent_run_id)

        self._status = constants.Status.InProgress

        self._log_data_stat(self.input_data.get("X"), 'X', prefix="[ParentRunId:{}]".format(self.parent_run_id))
        self._log_data_stat(self.input_data.get("y"), 'y', prefix="[ParentRunId:{}]".format(self.parent_run_id))
        dataset_utilities.log_dataset("X", X, self.current_run)
        dataset_utilities.log_dataset("y", y, self.current_run)
        dataset_utilities.log_dataset("X_valid", X_valid, self.current_run)
        dataset_utilities.log_dataset("y_valid", y_valid, self.current_run)

    def _get_transformed_context(self,
                                 input_data: Dict[str, Any],
                                 experiment_observer: AzureExperimentObserver,
                                 cache_store: Optional[CacheStore],
                                 verifier: VerifierManager) \
            -> Union[TransformedDataContext, StreamingTransformedDataContext]:
        if self.parent_run_id is None:
            # for mypy checks to pass
            raise ValueError("parent_run_id cannot be None within _get_transformed_context")
        with log_activity(logger=self.logger, activity_name=TelemetryConstants.PRE_PROCESS_NAME):
            if input_data.get("X_valid") is not None:
                self._log_data_stat(
                    input_data.get("X_valid"), 'X_valid', prefix="[ParentRunId:{}]".format(self.parent_run_id)
                )
            if input_data.get("y_valid") is not None:
                self._log_data_stat(
                    input_data.get("y_valid"), 'y_valid', prefix="[ParentRunId:{}]".format(self.parent_run_id)
                )

            raw_data_context = RawDataContext(automl_settings_obj=self.automl_settings,
                                              X=input_data.get("X"),
                                              y=input_data.get("y"),
                                              X_valid=input_data.get("X_valid"),
                                              y_valid=input_data.get("y_valid"),
                                              sample_weight=input_data.get("sample_weight"),
                                              sample_weight_valid=input_data.get("sample_weight_valid"),
                                              x_raw_column_names=input_data.get("x_raw_column_names"),
                                              cv_splits_indices=input_data.get("cv_splits_indices"))

            feature_sweeping_config = self.feature_config_manager.get_feature_sweeping_config(
                self.automl_settings.enable_feature_sweeping,
                self.parent_run_id,
                self.automl_settings.task_type)
            transformed_data_context = data_transformation.transform_data(
                raw_data_context=raw_data_context,
                experiment_observer=experiment_observer,
                logger=self.logger,
                cache_store=cache_store,
                is_onnx_compatible=self.automl_settings.enable_onnx_compatible_models,
                enable_feature_sweeping=self.automl_settings.enable_feature_sweeping,
                feature_sweeping_config=feature_sweeping_config,
                enable_dnn=self.automl_settings.enable_dnn,
                verifier=verifier)

            return transformed_data_context

    def _fit_local(self, X=None, y=None, sample_weight=None, X_valid=None, y_valid=None, sample_weight_valid=None,
                   cv_splits_indices=None, existing_run=False,
                   training_data=None, validation_data=None, _script_run=None):

        verifier = VerifierManager()

        self._create_parent_run_for_local(
            X=X, y=y, sample_weight=sample_weight, X_valid=X_valid, y_valid=y_valid,
            cv_splits_indices=cv_splits_indices, existing_run=existing_run,
            sample_weight_valid=sample_weight_valid,
            training_data=training_data, validation_data=validation_data, verifier=verifier, _script_run=_script_run)

        # Init the onnx converter with the original X if user set wants to enable onnx compatible models.
        if self.automl_settings.enable_onnx_compatible_models:
            pkg_ver = _get_package_version()
            enable_split_onnx_models = self.automl_settings.enable_split_onnx_featurizer_estimator_models
            self.onnx_cvt = OnnxConverter(logger=self.logger,
                                          version=pkg_ver,
                                          is_onnx_compatible=self.automl_settings.enable_onnx_compatible_models,
                                          enable_split_onnx_featurizer_estimator_models=enable_split_onnx_models)
            onnx_mdl_name = '{}[{}]'.format(OnnxConvertConstants.OnnxModelNamePrefix, self.parent_run_id)
            onnx_mdl_desc = {'ParentRunId': self.parent_run_id}
            self.onnx_cvt.initialize_input(X=self.input_data.get("X"),
                                           x_raw_column_names=self.input_data.get("x_raw_column_names"),
                                           model_name=onnx_mdl_name,
                                           model_desc=onnx_mdl_desc)

        # `enable_cache` is deprecated. Instead, rely on either `preprocess` or `is_timeseries` flags to
        # save the featurized / transformed data to the local disk based cache.
        cache_store = CacheStoreFactory.get_cache_store(
            enable_cache=(self.automl_settings.enable_cache or
                          self.automl_settings.preprocess or
                          self.automl_settings.is_timeseries),
            run_id=self.parent_run_id)
        experiment_observer = AzureExperimentObserver(self.current_run, self._console_logger, self.logger)
        transformed_data_context = self._get_transformed_context(self.input_data,
                                                                 experiment_observer,
                                                                 cache_store,
                                                                 verifier)

        if not existing_run:
            self._jasmine_client.set_parent_run_status(
                self.parent_run_id, constants.RunState.START_RUN)

            # set the problem info, so the JOS can use it to get pipelines.
            _automl._set_problem_info(transformed_data_context.X,
                                      transformed_data_context.y,
                                      automl_settings=self.automl_settings,
                                      current_run=self.current_run,
                                      transformed_data_context=transformed_data_context,
                                      cache_store=cache_store,
                                      logger=self.logger)

        subsampling = self.current_run._get_problem_info_dict().get('subsampling', False)

        dataset = training_utilities.init_client_dataset(transformed_data_context=transformed_data_context,
                                                         cache_store=cache_store,
                                                         automl_settings=self.automl_settings,
                                                         remote=False,
                                                         init_all_stats=False,
                                                         keep_in_memory=False)
        self.logger.info(
            "Initialized ClientDatasets object from transformed_data_context.. deleting transformed_data_context.")
        del transformed_data_context

        try:
            #  Set up interface to print execution progress
            ci = ConsoleInterface("score", self._console_logger, mask_sampling=not subsampling)
        except Exception as e:
            logging_utilities.log_traceback(e, self.logger)
            raise

        self.experiment_start_time = datetime.utcnow()

        if existing_run:
            self.current_run.tag("continue", ContinueFlagStates.ContinueSet)
            self.current_iter = len(
                list(self.current_run.get_children(_rehydrate_runs=False)))
        else:
            self.current_iter = 0
            if verifier is not None:
                parent_run_context = AzureAutoMLRunContext(self.current_run)
                verifier.write_result_file(parent_run_context, self.logger)
                ci.print_guardrails(verifier.ret_dict['faults'])

        experiment_observer.report_status(ExperimentStatus.ModelSelection, "Beginning model selection.")
        ci.print_descriptions()
        ci.print_columns()

        try:
            self.logger.info("Start local loop.")

            while self.current_iter < self.automl_settings.iterations:
                if self._status == constants.Status.Terminated:
                    self._console_logger.write(
                        "Stopping criteria reached at iteration {0}. Ending experiment.".format(self.current_iter - 1))
                    self.logger.info(
                        "Stopping criteria reached at iteration {0}. Ending experiment.".format(self.current_iter - 1))
                    self._jasmine_client.set_parent_run_status(self.parent_run_id, constants.RunState.COMPLETE_RUN)
                    return AutoMLRun(self.experiment, self.parent_run_id, host=self.automl_settings.service_url)
                self.logger.info("Start iteration: {0}".format(self.current_iter))
                with log_activity(logger=self.logger, activity_name=TelemetryConstants.FIT_ITERATION_NAME):
                    self._fit_iteration(ci, dataset=dataset)
            self._status = constants.Status.Completed
        except KeyboardInterrupt:
            self._status = constants.Status.Terminated
            self.logger.info(
                "[ParentRunId:{}]Received interrupt. Returning now.".format(self.parent_run_id))
            self._console_logger.write("Received interrupt. Returning now.")
            self._jasmine_client.set_parent_run_status(self.parent_run_id, constants.RunState.CANCEL_RUN)
        finally:
            # Perform model explanations for best run
            _automl_perform_best_run_explain_model(self.current_run, dataset, self.automl_settings,
                                                   self.logger, current_run=None,
                                                   experiment_observer=experiment_observer,
                                                   console_interface=ci)

            if not existing_run and self._status != constants.Status.Terminated and \
               self._is_any_childruns_succeed(self.current_run):
                self._jasmine_client.set_parent_run_status(
                    self.parent_run_id, constants.RunState.COMPLETE_RUN)
            elif not self._is_any_childruns_succeed(self.current_run):
                ex = ModelFitException("All child runs failed.")
                self._fail_parent_run(error_details=ex, logger=self.logger)

            # cleanup transformed, preprocessed data cache
            if dataset is not None:
                cache_clear_status = dataset.clear_cache()
                if not cache_clear_status:
                    self.logger.warning("Failed to unload the dataset from cache store.")

            # if we are from continue run, remove flag
            if existing_run:
                self.current_run.tag("continue", ContinueFlagStates.ContinueNone)

            # turn off system usage collection on run completion or failure
            if self._usage_telemetry is not None:
                self._usage_telemetry.stop()

        self.logger.info("Run Complete.")

    def _fit_iteration(self, ci, transformed_data_context=None, dataset=None):
        start_iter_time = datetime.utcnow()

        #  Query Jasmine for the next set of pipelines to run
        task_dto = self._get_task()

        if task_dto.is_experiment_over:
            self.logger.info("Complete task received. Completing experiment")
            self.cancel()
            return

        run_id = task_dto.childrun_id
        self.logger.update_default_property("child_run_id", run_id)

        pipeline_id = task_dto.pipeline_id
        pipeline_script = task_dto.pipeline_spec
        train_frac = float(task_dto.training_percent or 100) / 100

        """
        # TODO: Fix pipeline spec logging (#438111)
        self.logger.info(
            "Received pipeline: {0}".format(
                logging_utilities.remove_blacklisted_logging_keys_from_json_str(
                    pipeline_script
                )
            )
        )
        """
        self.logger.info('Received pipeline ID {}'.format(pipeline_id))

        ci.print_start(self.current_iter)
        errors = []
        child_run_metrics = None
        try:
            child_run = Run(self.experiment, run_id)
            # get total run time in seconds and convert to minutes
            elapsed_time = math.floor(int((datetime.utcnow() - self.experiment_start_time).total_seconds()) / 60)
            child_run.start()

            automl_run_context = AzureAutoMLRunContext(child_run)
            automl_pipeline = AutoMLPipeline(automl_run_context, pipeline_script, pipeline_id, train_frac)

            # copy the Run information to environment variables
            # this allows the child process that we spawn to be able to reconstruct the run object.
            self._set_environment_variables_for_reconstructing_run(child_run)
            fit_output = fit_pipeline_helper.fit_pipeline(
                automl_pipeline=automl_pipeline,
                automl_settings=self.automl_settings,
                automl_run_context=automl_run_context,
                remote=False,
                logger=self.logger,
                transformed_data_context=transformed_data_context,
                dataset=dataset,
                elapsed_time=elapsed_time,
                onnx_cvt=self.onnx_cvt,
                bypassing_model_explain=self.current_run.get_tags().get('model_explain_run'))

            if fit_output.errors:
                err_type = next(iter(fit_output.errors))
                exception_info = fit_output.errors[err_type]
                exception_obj = cast(BaseException, exception_info['exception'])
                if err_type == 'model_explanation' and isinstance(exception_obj, ImportError):
                    errors.append('Could not explain model due to missing dependency. Please run: pip install '
                                  'azureml-sdk[explain]')
                elif isinstance(exception_obj, TimeoutException):
                    errors.append('Fit operation exceeded provided timeout, terminating and moving onto the next '
                                  'iteration. Please consider increasing the iteration_timeout_minutes parameter.')
                else:
                    errors.append('Run {} failed with exception "{}".'.format(run_id, str(exception_obj)))

            score = fit_output.score
            preprocessor = fit_output.run_preprocessor
            model_name = fit_output.run_algorithm
        except Exception as e:
            logging_utilities.log_traceback(e, self.logger)
            score = constants.Defaults.DEFAULT_PIPELINE_SCORE
            preprocessor = ''
            model_name = ''
            errors.append('Run {} failed with exception "{}".'.format(run_id, str(e)))

        ci.print_pipeline(preprocessor, model_name, train_frac)
        self._update_internal_scores_after_iteration(score)

        end_iter_time = datetime.utcnow()
        end_iter_time = end_iter_time.replace(tzinfo=pytz.UTC)
        start_iter_time = start_iter_time.replace(tzinfo=pytz.UTC)
        if child_run_metrics is not None:
            created_time = child_run_metrics._run_dto['created_utc']
            if isinstance(created_time, str):
                created_time = datetime.strptime(created_time, '%Y-%m-%dT%H:%M:%S.%fZ')
            start_iter_time = created_time.replace(tzinfo=pytz.UTC)
            details = child_run_metrics.get_details()
            if 'endTimeUtc' in details:
                end_iter_time = datetime.strptime(details['endTimeUtc'],
                                                  '%Y-%m-%dT%H:%M:%S.%fZ').replace(tzinfo=pytz.UTC)
        iter_duration = str(end_iter_time - start_iter_time).split(".")[0]

        ci.print_end(iter_duration, score, self._score_best)
        self.current_iter = self.current_iter + 1

        for error in errors:
            ci.print_error(error)

    def _fit_remote(self, run_configuration, X=None, y=None, sample_weight=None, X_valid=None, y_valid=None,
                    sample_weight_valid=None, cv_splits_indices=None, show_output=False,
                    training_data=None, validation_data=None):

        self._fit_remote_core(run_configuration, X=X, y=y, sample_weight=sample_weight, X_valid=X_valid,
                              y_valid=y_valid, sample_weight_valid=sample_weight_valid,
                              cv_splits_indices=cv_splits_indices, training_data=training_data,
                              validation_data=validation_data)
        if show_output:
            RemoteConsoleInterface._show_output(self.current_run,
                                                self._console_logger,
                                                self.logger,
                                                self.automl_settings.primary_metric)

    def _fit_remote_core(self, run_configuration, X=None, y=None, sample_weight=None, X_valid=None, y_valid=None,
                         sample_weight_valid=None, cv_splits_indices=None, training_data=None, validation_data=None):
        if isinstance(run_configuration, str):
            run_config_object = RunConfiguration.load(
                self.automl_settings.path, run_configuration)
        else:
            # we alread have a run configuration object
            run_config_object = run_configuration
            run_configuration = run_config_object.target

        self._create_parent_run_for_remote(
            run_config_object, X=X, y=y, sample_weight=sample_weight, X_valid=X_valid, y_valid=y_valid,
            sample_weight_valid=sample_weight_valid, cv_splits_indices=cv_splits_indices,
            training_data=training_data, validation_data=validation_data)

        snapshotId = ""
        if self.automl_settings.path is not None:
            snapshotId = self.current_run.take_snapshot(self.automl_settings.path)
        self.logger.info("Snapshotted folder: {0} with snapshot_id: {1}".format(
            self.automl_settings.path, snapshotId))

        definition = {
            "Configuration": _serialize_to_dict(run_config_object)
        }

        # BUG: 287204
        del definition["Configuration"]["environment"]["python"]["condaDependenciesFile"]
        definition["Configuration"]["environment"]["python"]["condaDependencies"] = \
            run_config_object.environment.python.conda_dependencies._conda_dependencies

        self.logger.info("Starting a snapshot run (snapshotId : {0})".format(snapshotId))
        try:
            self._jasmine_client.post_remote_jasmine_snapshot_run(self.parent_run_id,
                                                                  json.dumps(definition),
                                                                  snapshotId)
        except (AzureMLServiceException, HttpOperationError) as e:
            logging_utilities.log_traceback(e, self.logger)
            friendly_http_exception(e, constants.API.StartRemoteSnapshotRun)
        except Exception as e:
            logging_utilities.log_traceback(e, self.logger)
            raise ClientException("Error occurred when trying to submit a remote run to AutoML Service.") \
                from None

    def _create_parent_run_for_remote(self, run_config_object, X=None, y=None, sample_weight=None,
                                      X_valid=None, y_valid=None, sample_weight_valid=None, cv_splits_indices=None,
                                      training_data=None, validation_data=None):

        run_configuration = run_config_object.target
        run_config_object = modify_run_configuration(self.automl_settings, run_config_object, self.logger)

        if training_data is not None:
            dataprep_json = dataprep_utilities.\
                get_dataprep_json_dataset(training_data=training_data,
                                          validation_data=validation_data)
        else:
            dataprep_json = dataprep_utilities.get_dataprep_json(X=X, y=y,
                                                                 sample_weight=sample_weight,
                                                                 X_valid=X_valid,
                                                                 y_valid=y_valid,
                                                                 sample_weight_valid=sample_weight_valid,
                                                                 cv_splits_indices=cv_splits_indices)
        if dataprep_json is not None:
            # escape quotations in json_str before sending to jasmine
            dataprep_json = dataprep_json.replace('\\', '\\\\').replace('"', '\\"')

        parent_run_dto = self._create_parent_run_dto(run_configuration, dataprep_json)

        self._validate_remote_input(parent_run_dto)

        try:
            self.logger.info(
                "Start creating parent run with DTO: {0}.".format(
                    self.automl_settings._format_selective(BLACKLISTED_LOGGING_KEYS)))
            self.parent_run_id = self._jasmine_client.post_parent_run(
                parent_run_dto)
        except (AzureMLServiceException, HttpOperationError) as e:
            logging_utilities.log_traceback(e, self.logger)
            friendly_http_exception(e, constants.API.CreateParentRun)
        except Exception as e:
            logging_utilities.log_traceback(e, self.logger)
            raise ClientException(
                "Error occurred when trying to create new parent run in AutoML service.") from None

        if self.user_script:
            self.logger.info(
                "[ParentRunID:{}] Remote run using user script.".format(self.parent_run_id))
        else:
            self.logger.info(
                "[ParentRunID:{}] Remote run using input X and y.".format(self.parent_run_id))

        if self.current_run is None:
            self.current_run = AutoMLRun(self.experiment, self.parent_run_id, host=self.automl_settings.service_url)

        # TODO: Remove with task 416022
        self._add_display_task()
        log_user_sdk_dependencies(self.current_run, self.logger)

        self._console_logger.write("Parent Run ID: " + self.parent_run_id)
        self.logger.info("Parent Run ID: " + self.parent_run_id)

    def _validate_remote_input(self, parent_run_dto: CreateParentRunDto) -> None:
        validation_results = None
        try:
            validation_results = self._jasmine_client.post_validate_service(parent_run_dto)
        except HttpOperationError as e:
            if e.response.status_code == 204:
                self.logger.info("Validation service found the data has no errors.")
            else:
                # Any validation related exception won't fail the experiment.
                self.logger.warning("Non-terminal error returned by validation service.")
        except Exception as e:
            # Any other validation related exception won't fail the experiment.
            self.logger.warning("Validation service meet exceptions, continue training now.")

        if validation_results is not None and len(validation_results.error.details) > 0 \
                and any([d.code != "UpstreamSystem" for d in validation_results.error.details]):
            # If validation service meets error thrown by the upstream service, the run will continue.
            self._console_logger.write("The validation results are following:\n")
            for result in validation_results.error.details:
                if result.code != "UpstreamSystem":
                    self._console_logger.write(result.message + "\n")
            raise ValidationException.create_without_pii(
                "Validation failed on the sample data. "
                "Please fix the data or settings following the validation results.")

    def _create_parent_run_dto(self, target, dataprep_json=None):
        """
        Create CreateParentRunDto.

        :param target: run configuration
        :type target: RunConfiguration or str
        :param dataprep_json: dataprep json string
        :type dataprep_json: str
        :return: CreateParentRunDto to be sent to Jasmine
        :rtype: CreateParentRunDto
        """
        # min to sec conversion
        timeout = None
        if self.automl_settings.iteration_timeout_minutes:
            timeout = self.automl_settings.iteration_timeout_minutes * 60
        parent_run_dto = CreateParentRunDto(target=target,
                                            num_iterations=self.automl_settings.iterations,
                                            training_type=None,  # use self.training_type when jasmine supports it
                                            acquisition_function=None,
                                            metrics=['accuracy'],
                                            primary_metric=self.automl_settings.primary_metric,
                                            train_split=self.automl_settings.validation_size,
                                            max_time_seconds=timeout,
                                            acquisition_parameter=0.0,
                                            num_cross_validation=self.automl_settings.n_cross_validations,
                                            raw_aml_settings_string=str(
                                                self.automl_settings.as_serializable_dict()),
                                            aml_settings_json_string=json.dumps(
                                                self.automl_settings.as_serializable_dict()),
                                            data_prep_json_string=dataprep_json,
                                            enable_subsampling=self.automl_settings.enable_subsampling)
        return parent_run_dto

    def _get_task(self):
        """
        Query Jasmine for the next task.

        :return: dto containing task details
        """
        with log_activity(logger=self.logger, activity_name=TelemetryConstants.GET_PIPELINE_NAME):
            try:
                self.logger.info("Querying Jasmine for next task.")
                return self._jasmine_client.get_next_task(self.parent_run_id)
            except (AzureMLServiceException, HttpOperationError) as e:
                logging_utilities.log_traceback(e, self.logger)
                friendly_http_exception(e, constants.API.GetNextPipeline)
            except Exception as e:
                logging_utilities.log_traceback(e, self.logger)
                raise ServiceException("Error occurred when trying to fetch next iteration from AutoML service.") \
                    from None

    def _check_create_folders(self, path):
        if path is None:
            path = os.getcwd()
        # Expand out the path because os.makedirs can't handle '..' properly
        aml_config_path = os.path.abspath(os.path.join(path, '.azureml'))
        os.makedirs(aml_config_path, exist_ok=True)

    def _update_internal_scores_after_iteration(self, score):
        if self._score_max is None or np.isnan(self._score_max) or score > self._score_max:
            self._score_max = score
        if self._score_min is None or np.isnan(self._score_min) or score < self._score_min:
            self._score_min = score

        if self.automl_settings.metric_operation == constants.OptimizerObjectives.MINIMIZE:
            self._score_best = self._score_min
        elif self.automl_settings.metric_operation == constants.OptimizerObjectives.MAXIMIZE:
            self._score_best = self._score_max

    def _log_data_stat(self, data, data_name, prefix=None):
        if prefix is None:
            prefix = ""
        if type(data) is not np.ndarray and type(data) is not np.array and type(data) is not pd.DataFrame:
            try:
                data = data.to_pandas_dataframe()
            except AttributeError:
                self.logger.warning("The data type is not supported for logging.")
                return
        self.logger.info(
            "{}Input {} datatype is {}, shape is {}, datasize is {}.".format(
                prefix, data_name, type(data), data.shape,
                memory_utilities.get_data_memory_size(data)
            )
        )

    def _add_display_task(self) -> None:
        """Add display task property."""
        task = self.automl_settings.task_type
        if self.automl_settings.is_timeseries:
            task = constants.Tasks.FORECASTING
        # This property is to temporarily fix: 362194.
        # It should be removed promptly.
        assert self.current_run is not None
        self.current_run.add_properties({'display_task_type': task})

    def _fail_parent_run(self, error_details: BaseException, logger: logging.Logger) -> None:
        try:
            if self.current_run is not None:
                self.current_run.fail(error_details=error_details,
                                      error_code=common_utilities.get_error_code(error_details))
            if self._jasmine_client is not None and self.parent_run_id is not None:
                self._jasmine_client.set_parent_run_status(self.parent_run_id, constants.RunState.FAIL_RUN)
        except (AzureMLServiceException, HttpOperationError) as e:
            logging_utilities.log_traceback(e, logger)
            friendly_http_exception(e, constants.API.CreateParentRun)
        except Exception as e:
            logging_utilities.log_traceback(e, logger)
            raise ClientException(
                "Error occurred when trying to set parent run status.") from None

    @staticmethod
    def _set_environment_variables_for_reconstructing_run(run):
        os.environ['AZUREML_ARM_SUBSCRIPTION'] = run.experiment.workspace.subscription_id
        os.environ["AZUREML_RUN_ID"] = run.id
        os.environ["AZUREML_ARM_RESOURCEGROUP"] = run.experiment.workspace.resource_group
        os.environ["AZUREML_ARM_WORKSPACE_NAME"] = run.experiment.workspace.name
        os.environ["AZUREML_ARM_PROJECT_NAME"] = run.experiment.name
        os.environ['AZUREML_RUN_TOKEN'] = run._client.run.get_token().token
        os.environ["AZUREML_SERVICE_ENDPOINT"] = run._client.run.get_cluster_url()

    @staticmethod
    def _is_any_childruns_succeed(run):
        return any([r.status.lower() == constants.RunState.COMPLETE_RUN for r in run.get_children()])

    @staticmethod
    def _is_tensorflow_module_present():
        try:
            return pipeline_spec.tf_wrappers.tf_found
        except Exception:
            return False

    @staticmethod
    def _is_xgboost_module_present():
        try:
            return model_wrappers.xgboost_present
        except Exception:
            return False

    @staticmethod
    def _is_fbprophet_module_present():
        try:
            import fbprophet
            return True
        except ImportError:
            return False
