# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Class that runs automl run on ADB worker node."""
import datetime
import json
import logging
import os
from six import raise_from
import sys
import traceback
from typing import cast, Union, Any, List, Optional, Dict

import gc
from azureml._base_sdk_common.service_discovery import HISTORY_SERVICE_ENDPOINT_KEY
from azureml._restclient.jasmine_client import JasmineClient
from azureml._restclient.experiment_client import ExperimentClient
from azureml._restclient.service_context import ServiceContext
from azureml.core import Run
from azureml.core.authentication import AzureMLTokenAuthentication
from azureml.core.experiment import Experiment
from azureml.core.workspace import Workspace
from azureml._common.exceptions import AzureMLException
from azureml.telemetry import set_diagnostics_collection

from automl.client.core.common import logging_utilities as log_utils
from azureml.train.automl.exceptions import ClientException
from automl.client.core.common import utilities
from automl.client.core.runtime.cache_store import CacheStore
from automl.client.core.runtime.datasets import ClientDatasets
from azureml.automl.core import data_transformation
from azureml.automl.core import fit_pipeline as fit_pipeline_helper
from azureml.automl.core import training_utilities
from azureml.automl.core.automl_pipeline import AutoMLPipeline
from azureml.automl.core.data_context import RawDataContext, TransformedDataContext
from azureml.automl.core.streaming_data_context import StreamingTransformedDataContext
from azureml.automl.core.faults_verifier import VerifierManager
from azureml.automl.core.onnx_convert import OnnxConverter, OnnxConvertConstants
from azureml.automl.core.systemusage_telemetry import SystemResourceUsageTelemetryFactory
from azureml.train.automl._amlloguploader import _AMLLogUploader
from . import _logging
from ._adb_get_data import get_input_datamodel_from_dataprep_json, _input_data_model
from ._automl import _set_problem_info
from ._azureautomlruncontext import AzureAutoMLRunContext
from ._azureautomlsettings import AzureAutoMLSettings
from ._cachestorefactory import CacheStoreFactory
from ._execute_with_retry import ExecuteWithRetry
from .run import AutoMLRun
from ._automl_feature_config_manager import AutoMLFeatureConfigManager
from .utilities import _get_package_version
from .automl_explain_utilities import _automl_perform_best_run_explain_model


MAX_RETRY_COUNT_ON_EXCEPTION = 5
BACK_OFF_FACTOR = 2
MAX_RETRY_COUNT_DURING_SETUP = 10000
MAX_WAIT_IN_SECONDS = 300
SLEEP_TIME = 10
JASMINE_CLIENT = "JasmineClient"
EXPERIMENT_CLIENT = "ExperimentClient"


def adb_run_experiment(input_params):
    """
    Read run configuration, get next pipeline, and call fit iteration.

    :param input_params: List of input parameters.
    :type input_params: list
    :return:
    :rtype: None
    """
    worker_id = input_params[0]
    run_context = input_params[1]
    subscription_id = run_context.get('subscription_id', None)
    resource_group = run_context.get('resource_group', None)
    workspace_name = run_context.get('workspace_name', None)
    location = run_context.get('location', None)
    aml_token = run_context.get('aml_token', None)
    aml_token_expiry = run_context.get('aml_token_expiry', None)
    experiment_name = run_context.get('experiment_name', None)
    parent_run_id = run_context.get('parent_run_id', None)
    service_url = run_context.get('service_url', None)
    dataprep_json = run_context.get('dataprep_json', None)
    automl_settings_str = run_context.get('automl_settings_str', None)
    _set_env_variables(subscription_id,
                       resource_group,
                       workspace_name,
                       experiment_name,
                       aml_token,
                       aml_token_expiry,
                       service_url)

    adb_experiment = _AdbAutomlExperiment(parent_run_id,
                                          subscription_id,
                                          resource_group,
                                          workspace_name,
                                          experiment_name,
                                          aml_token,
                                          aml_token_expiry,
                                          service_url,
                                          location,
                                          automl_settings_str,
                                          dataprep_json,
                                          worker_id)
    adb_experiment.run()


def _set_env_variables(subscription_id, resource_group, workspace_name, experiment_name,
                       aml_token, aml_token_expiry, service_url):
    df_value_list = [subscription_id, resource_group, workspace_name, experiment_name,
                     aml_token, aml_token_expiry, service_url]
    var = None
    if any(var is None for var in df_value_list):
        raise ValueError("{0}: Value can't be None".format(var))
    os.environ["AZUREML_ARM_SUBSCRIPTION"] = subscription_id
    os.environ["AZUREML_ARM_RESOURCEGROUP"] = resource_group
    os.environ["AZUREML_ARM_WORKSPACE_NAME"] = workspace_name
    os.environ["AZUREML_ARM_PROJECT_NAME"] = experiment_name
    os.environ["AZUREML_RUN_TOKEN"] = aml_token
    os.environ["AZUREML_RUN_TOKEN_EXPIRY"] = str(aml_token_expiry)
    os.environ["AZUREML_SERVICE_ENDPOINT"] = service_url


def log_message(logger=None, logging_level=logging.INFO, parent_run_id=None, worker_id=None, message=None):
    """
    Use to log messages.

    :param logger: The logger used to write message.
    :type logger: logging.Logger
    :param logging_level: The logging level to use.
    :type logging_level: str
    :param parent_run_id: The associated parent run ID.
    :type parent_run_id: str
    :param worker_id: The associated worker node ID.
    :type worker_id: str
    :param message: The associated message.
    :type message: str
    :return:
    :rtype: None
    """
    print("{0}, {1}, {2}, {3}".format(datetime.datetime.utcnow(), parent_run_id, worker_id, message))

    if logger is None:
        return

    if logging_level == logging.ERROR:
        logger.error("{0}, {1}, {2}, {3}".format(parent_run_id, worker_id, message, traceback.format_exc()))
    elif logging_level == logging.DEBUG:
        logger.debug("{0}, {1}, {2}".format(parent_run_id, worker_id, message))
    elif logging_level == logging.WARNING:
        logger.warning("{0}, {1}, {2}".format(parent_run_id, worker_id, message))
    else:
        logger.info("{0}, {1}, {2}".format(parent_run_id, worker_id, message))


class _AdbAutomlExperiment():

    DATASET_CACHED_KEY = 'dataset_cached_object'
    CACHE_STORE_KEY_ONNX_CONVERTER_INIT_METADATA = '_CACHE_STORE_KEY_ONNX_CONVERTER_INIT_METADATA_'

    def __init__(self,
                 parent_run_id,
                 subscription_id,
                 resource_group,
                 workspace_name,
                 experiment_name,
                 aml_token,
                 aml_token_expiry,
                 service_url,
                 location,
                 automl_settings_str,
                 dataprep_json,
                 worker_id):
        self.parent_run_id = parent_run_id
        self.subscription_id = subscription_id
        self.resource_group = resource_group
        self.workspace_name = workspace_name
        self.experiment_name = experiment_name
        self.aml_token = aml_token
        self.aml_token_expiry = aml_token_expiry
        self.service_url = service_url
        self.location = location
        self.worker_id = worker_id
        self.automl_settings_str = automl_settings_str
        self.dataset = None  # type: Optional[ClientDatasets]

        os.environ["AZUREML_RUN_TOKEN"] = self.aml_token
        os.environ["AZUREML_RUN_TOKEN_EXPIRY"] = str(self.aml_token_expiry)

        self.experiment_client = self._create_client(EXPERIMENT_CLIENT)
        self.feature_config_manager = AutoMLFeatureConfigManager(jasmine_client=self._create_client(JASMINE_CLIENT))
        self.automl_settings = AzureAutoMLSettings(
            self._rehydrate_experiment(), **json.loads(self.automl_settings_str))
        print("{0}, {1}, {2}, Enabling telemetry with verbosity {3}".format(datetime.datetime.utcnow(),
                                                                            self.parent_run_id,
                                                                            self.worker_id,
                                                                            self.automl_settings.telemetry_verbosity))
        set_diagnostics_collection(send_diagnostics=self.automl_settings.send_telemetry,
                                   verbosity=self.automl_settings.telemetry_verbosity)
        self.logger = _logging.get_logger(
            self.automl_settings.debug_log, self.automl_settings.verbosity, self.automl_settings)
        self.logger.addHandler(logging.StreamHandler(sys.stdout))
        self.logger.update_default_property('parent_run_id', self.parent_run_id)

        self._usage_telemetry = SystemResourceUsageTelemetryFactory.get_system_usage_telemetry(
            self.logger)
        self._usage_telemetry.start()

        self.dataprep_json = dataprep_json
        self.jasmine_client_exception_count = 0

        try:
            # Note that this is due to known issue in shap library
            # Until that issue is fixed this is temporary mitigation specific
            # to AzureDatabricks.
            import matplotlib as mpl
            mpl.use('AGG')
        except Exception as e:
            self.log_message(message="Failed set the matplot backend. {}".format(e), logging_level=logging.ERROR)

    def _should_retry(self, output, exception, current_retry):
        pipeline_dto = output
        if pipeline_dto is not None:
            # reset exception counter since we were able to establish connnection
            self.jasmine_client_exception_count = 0
            should_retry = ((pipeline_dto.pipeline_spec is None or pipeline_dto.pipeline_spec == '') and
                            not pipeline_dto.is_experiment_over)
            should_retry = (should_retry and
                            ((pipeline_dto.childrun_id is not None or pipeline_dto.childrun_id == '') and
                             not self._is_special_run(pipeline_dto.childrun_id)))
            return (should_retry, BACK_OFF_FACTOR)
        elif exception is not None:
            self.jasmine_client_exception_count += 1
            if self.jasmine_client_exception_count == MAX_RETRY_COUNT_ON_EXCEPTION:
                return (False, BACK_OFF_FACTOR)

            return (True, BACK_OFF_FACTOR)

        return (False, BACK_OFF_FACTOR)

    def _is_special_run(self, run_id):
        return run_id.endswith("setup") or run_id.endswith("ModelExplain")

    def _get_next_pipeline(self):
        jasmine_client = self._create_client(JASMINE_CLIENT)
        pipeline_dto = jasmine_client.get_next_pipeline(
            self.parent_run_id, self.worker_id)
        return pipeline_dto

    def log_message(self, message, logging_level=logging.DEBUG):
        log_message(logger=self.logger,
                    logging_level=logging_level,
                    parent_run_id=self.parent_run_id,
                    worker_id=self.worker_id,
                    message=message)

    def run(self):

        parent_run_id = self.parent_run_id
        worker_id = self.worker_id
        logger = self.logger
        log_message(logger=logger, parent_run_id=parent_run_id, worker_id=worker_id,
                    message="Starting experiment run on worker node...")

        try:
            while (True):
                execute_with_retry = ExecuteWithRetry(
                    MAX_RETRY_COUNT_DURING_SETUP,
                    MAX_WAIT_IN_SECONDS,
                    self._should_retry,
                    self.log_message,
                    "jasmine_client.get_next_pipeline()")
                pipeline_dto = execute_with_retry.execute(
                    self._get_next_pipeline,
                    func_name="get_next_pipeline")
                if pipeline_dto.is_experiment_over:
                    log_message(logger=logger, parent_run_id=parent_run_id, worker_id=worker_id,
                                message="Experiment finished.")
                    break
                child_run_id = pipeline_dto.childrun_id
                self.logger.update_default_property('child_run_id', child_run_id)
                os.environ["AZUREML_RUN_ID"] = child_run_id
                self.fit_iteration(pipeline_dto, child_run_id)
        except Exception as e:
            log_message(logger=logger, logging_level=logging.ERROR, parent_run_id=parent_run_id,
                        worker_id=worker_id, message=e)
            raise
        finally:
            try:
                parent_run = self._rehydrate_run(parent_run_id)
                filename, file_extension = os.path.splitext(self.automl_settings.debug_log)
                if os.path.exists(self.automl_settings.debug_log):
                    if not self.automl_settings.debug_log.startswith("/dbfs"):
                        formatted_file_name = "logs/{0}_{1}_{2}{3}".format(
                            filename, str(worker_id),
                            datetime.datetime.utcnow().strftime("%Y-%m-%d-%H%M%SZ"),
                            file_extension)

                        parent_run.upload_file(formatted_file_name, self.automl_settings.debug_log)
            except Exception as e:
                log_message(logger=logger, logging_level=logging.WARNING, parent_run_id=parent_run_id,
                            worker_id=worker_id, message=e)

        log_message(logger=logger, parent_run_id=parent_run_id, worker_id=worker_id,
                    message="Finished experiment run on worker node.")

    def _rehydrate_experiment(self):
        auth = AzureMLTokenAuthentication.create(self.aml_token,
                                                 AzureMLTokenAuthentication._convert_to_datetime(
                                                     self.aml_token_expiry),
                                                 self.service_url,
                                                 self.subscription_id,
                                                 self.resource_group,
                                                 self.workspace_name,
                                                 self.experiment_name,
                                                 self.parent_run_id)
        workspace = Workspace(self.subscription_id,
                              self.resource_group, self.workspace_name,
                              auth=auth,
                              _location=self.location,
                              _disable_service_check=True)
        experiment = Experiment(workspace, self.experiment_name)
        return experiment

    def _rehydrate_run(self, run_id):
        return Run(self._rehydrate_experiment(), run_id)

    def fit_iteration(self, pipeline_dto, run_id):
        """
        Fit iteration method.

        :param pipeline_dto: Pipeline details to fit.
        :type pipeline_dto: PipelineDto
        :param run_id: run id.
        :type run_id: string
        """
        run_id = pipeline_dto.childrun_id
        pipeline_id = pipeline_dto.pipeline_id

        train_frac = 1.0
        if hasattr(pipeline_dto, 'training_percent'):
            train_frac = float(pipeline_dto.training_percent) / 100

        """
        # TODO: Fix pipeline spec logging (#438111)
        log_message(logger=self.logger, parent_run_id=self.parent_run_id, worker_id=self.worker_id,
                    message="Received pipeline: {0} for run id '{1}'".format(pipeline_dto.pipeline_spec, run_id))
        """
        self.logger.info('Received pipeline ID {}'.format(pipeline_id))

        verifier = VerifierManager()

        # This is due to token expiry issue
        current_run = self._rehydrate_run(run_id)

        with _AMLLogUploader(current_run, self.worker_id):
            try:
                current_run.start()
                log_message(logger=self.logger, parent_run_id=self.parent_run_id, worker_id=self.worker_id,
                            message="{0}: Starting childrun...".format(run_id))
                log_message(logger=self.logger, parent_run_id=self.parent_run_id, worker_id=self.worker_id,
                            message="{0}: Execution path {1}".format(run_id, os.path.realpath(__file__)))
                onnx_cvt = None     # type: Optional[OnnxConverter]
                pkg_ver = _get_package_version()
                if (run_id.endswith("setup")):
                    self.logger.info('Beginning setup iteration: {}.'.format(run_id))
                    input_data = get_input_datamodel_from_dataprep_json(
                        self.dataprep_json, self.log_message, automl_settings=self.automl_settings, logger=self.logger,
                        verifier=verifier)

                    with self.logger.log_activity(self.logger, activity_name='validate_training_data'):
                        training_utilities.validate_training_data(
                            X=input_data.X,
                            y=input_data.y,
                            X_valid=input_data.X_valid,
                            y_valid=input_data.y_valid,
                            sample_weight=input_data.sample_weight,
                            sample_weight_valid=input_data.sample_weight_valid,
                            cv_splits_indices=input_data.cv_splits_indices,
                            automl_settings=self.automl_settings)

                    _X = input_data.X
                    _y = input_data.y
                    transformed_data_context = None
                    cache_store = self._get_cache_store()
                    self.logger.info('Using {} for caching transformed data.'.format(type(cache_store).__name__))

                    if self.automl_settings.enable_onnx_compatible_models:
                        # Initialize the ONNX converter with the raw data and save metadata in the cache store.
                        enable_split_onnx_models = self.automl_settings.enable_split_onnx_featurizer_estimator_models
                        onnx_cvt = \
                            OnnxConverter(logger=self.logger,
                                          version=pkg_ver,
                                          is_onnx_compatible=self.automl_settings.enable_onnx_compatible_models,
                                          enable_split_onnx_featurizer_estimator_models=enable_split_onnx_models)
                        self._initialize_onnx_converter_with_cache_store(onnx_cvt=onnx_cvt,
                                                                         input_data=input_data,
                                                                         parent_run_id=self.parent_run_id,
                                                                         cache_store=cache_store,
                                                                         logger=self.logger)

                    if (self.automl_settings.enable_cache is True or
                            self.automl_settings.preprocess or
                            self.automl_settings.is_timeseries):
                        transformed_data_context = self._get_transformed_data_context(input_data,
                                                                                      cache_store,
                                                                                      verifier)
                        # We have a featurized data set now, which means either we had caching enabled or the
                        # data needed pre-processing. Either way, we save the hard work done to transform the data
                        # on the Azure Blob Store cache / local disk, from where other worker nodes can download from.
                        self.dataset = training_utilities.init_client_dataset(
                            transformed_data_context=transformed_data_context,
                            cache_store=cache_store,
                            automl_settings=self.automl_settings,
                            remote=False,
                            init_all_stats=False,
                            keep_in_memory=False)
                        cache_store.set(self.DATASET_CACHED_KEY, self.dataset)
                        self.logger.info("Initialized ClientDatasets from transformed_data_context during setup.")

                        _X = transformed_data_context.X
                        _y = transformed_data_context.y

                    with self.logger.log_activity(self.logger, activity_name='_set_problem_info'):
                        # P.S. The set_problem_info method also featurizes the data.
                        _set_problem_info(X=_X,
                                          y=_y,
                                          automl_settings=self.automl_settings,
                                          current_run=current_run,
                                          transformed_data_context=transformed_data_context,
                                          cache_store=cache_store,
                                          is_adb_run=True,
                                          logger=self.logger)

                    log_message(logger=self.logger, parent_run_id=self.parent_run_id, worker_id=self.worker_id,
                                message="{0}: Cache {1}, set_problem_info completed ..".
                                format(run_id, self.automl_settings.enable_cache))

                    if verifier is not None:
                        parent_run = self._rehydrate_run(self.parent_run_id)
                        parent_run_context = AzureAutoMLRunContext(parent_run, False)
                        verifier.write_result_file(parent_run_context, self.logger)

                    # Setup's finished. Eagerly clean up the input and/or featurized data.
                    # The model iteration workers will either recreate the featurized data (cache=False)
                    # or load the data from the Azure Blob Store cache (cache=True)
                    _X = None
                    _y = None
                    self.clear_input_data([transformed_data_context, input_data])
                    self.logger.info('Setup iteration "{}" finished successfully.'.format(run_id))
                elif (run_id.lower().endswith("ModelExplain".lower())):
                    log_message(logger=self.logger, parent_run_id=self.parent_run_id, worker_id=self.worker_id,
                                message="Model explain for best run starts.")
                    # Rehydrate the parent run
                    parent_run = AutoMLRun(self._rehydrate_experiment(), self.parent_run_id)
                    # Recover the dataset from cache store
                    self._recover_dataset(current_run, verifier)
                    # Perform model explanations for best run
                    _automl_perform_best_run_explain_model(parent_run, self.dataset, self.automl_settings,
                                                           self.logger, current_run)
                    current_run.complete()
                    log_message(logger=self.logger, parent_run_id=self.parent_run_id, worker_id=self.worker_id,
                                message="Model explain for best run ends.")
                else:
                    # worker node
                    self.logger.info('Beginning fit iteration: {}.'.format(run_id))
                    # if transformed_data_context is not set and if cache is enabled and preprocess is set to true
                    # try to load from cache
                    cache_store = self._get_cache_store()

                    if self.automl_settings.enable_onnx_compatible_models:
                        enable_split_onnx_models = self.automl_settings.enable_split_onnx_featurizer_estimator_models
                        onnx_cvt = \
                            OnnxConverter(logger=self.logger,
                                          version=pkg_ver,
                                          is_onnx_compatible=self.automl_settings.enable_onnx_compatible_models,
                                          enable_split_onnx_featurizer_estimator_models=enable_split_onnx_models)
                        onnx_mdl_name = 'AutoML_ONNX_Model_[{}]'.format(self.parent_run_id)
                        onnx_mdl_desc = {'ParentRunId': self.parent_run_id}

                    self._recover_dataset(current_run, verifier, onnx_cvt=onnx_cvt)

                    if self.automl_settings.enable_onnx_compatible_models and onnx_cvt is not None:
                        if cache_store is not None and not onnx_cvt.is_initialized():
                            # Try to initialize the ONNX converter with cached converter metadata if it's
                            # not initialized.
                            self.logger.info('Get ONNX converter init metadata for run {}.'.format(run_id))
                            cache_store.load()
                            cached_data_dict = cache_store.get([self.CACHE_STORE_KEY_ONNX_CONVERTER_INIT_METADATA])
                            if cached_data_dict is not None and cached_data_dict:
                                onnx_cvt_init_metadata_dict = cached_data_dict.get(
                                    self.CACHE_STORE_KEY_ONNX_CONVERTER_INIT_METADATA,
                                    None)  # type: Optional[Dict[str, Any]]
                                if onnx_cvt_init_metadata_dict is not None:
                                    self.logger.info(
                                        'Initialize ONNX converter with cached metadata run {}.'.format(run_id))
                                    onnx_cvt.initialize_with_metadata(metadata_dict=onnx_cvt_init_metadata_dict,
                                                                      model_name=onnx_mdl_name,
                                                                      model_desc=onnx_mdl_desc)

                        if onnx_cvt.is_initialized():
                            self.logger.info('Successfully initialized ONNX converter for run {}.'.format(run_id))
                        else:
                            self.logger.info('Failed to initialize ONNX converter for run {}.'.format(run_id))

                    automl_run_context = AzureAutoMLRunContext(Run.get_context(), is_adb_run=True)
                    automl_pipeline = AutoMLPipeline(automl_run_context, pipeline_dto.pipeline_spec, pipeline_id,
                                                     train_frac)

                    parent_run = self._rehydrate_run(self.parent_run_id)
                    result = fit_pipeline_helper.fit_pipeline(
                        automl_pipeline=automl_pipeline,
                        automl_settings=self.automl_settings,
                        automl_run_context=automl_run_context,
                        remote=True,
                        logger=self.logger,
                        dataset=self.dataset,
                        onnx_cvt=onnx_cvt,
                        bypassing_model_explain=parent_run.get_tags().get('model_explain_run'))

                    log_message(logger=self.logger, parent_run_id=self.parent_run_id, worker_id=self.worker_id,
                                message="result : {0}".format(result))
                    if result.errors:
                        err_type = next(iter(result.errors))
                        exception_info = result.errors[err_type]
                        exception_obj = cast(BaseException, exception_info['exception'])
                        exception_tb = cast(str, exception_info['traceback'])
                        log_message(logger=self.logger, logging_level=logging.ERROR,
                                    parent_run_id=self.parent_run_id, worker_id=self.worker_id,
                                    message="exception : Type {0} InnerException {1}".format(
                                        err_type, str(exception_obj)))
                        log_message(logger=self.logger, parent_run_id=self.parent_run_id,
                                    worker_id=self.worker_id, message="traceback : Type {0} Traceback : {1}".
                                    format(err_type, exception_tb))
                        if exception_info['is_critical']:
                            raise exception_obj.with_traceback(exception_obj.__traceback__)

                    score = result.score
                    duration = result.actual_time
                    log_message(logger=self.logger, parent_run_id=self.parent_run_id,
                                worker_id=self.worker_id, message="Score: {0}".format(score))
                    log_message(logger=self.logger, parent_run_id=self.parent_run_id,
                                worker_id=self.worker_id, message="Duration: {0}".format(duration))

                current_run.complete()
                log_message(logger=self.logger, parent_run_id=self.parent_run_id, worker_id=self.worker_id,
                            message="{0}: Fit iteration completed successfully.".format(run_id))

            except Exception as e:
                log_message(logger=self.logger, logging_level=logging.ERROR, parent_run_id=self.parent_run_id,
                            worker_id=self.worker_id, message=str(e))
                if current_run is not None:
                    current_run.fail(
                        error_details=e,
                        error_code=utilities.get_error_code(e))
                if (run_id.endswith("setup")):
                    try:
                        errors = {'errors': str({'exception': e})}
                        current_run.add_properties(errors)
                    except AzureMLException as ex:
                        self.log_message(message="{}: Failed to add 'errors' properties to run due to exception - {}"
                                         .format(run_id, ex),
                                         logging_level=logging.ERROR)
                        raise
                    except Exception as e:
                        raise_from(ClientException("{}: Setup iteration failed".format(run_id)), e)

    def _recover_dataset(self, current_run, verifier, onnx_cvt=None):
        """Recover the dataset object for training and model explanation iteration."""

        self.logger.info('Recovering dataset from cache store for run {}.'.format(current_run.id))

        cache_store = self._get_cache_store()

        if (self.dataset is None or
                self.automl_settings.enable_cache or
                self.automl_settings.preprocess or
                self.automl_settings.is_timeseries):
            current_run.add_properties({'LoadedFromCache': str(self.automl_settings.enable_cache)})
            self.dataset = self._load_data_from_cache(cache_store)

        if self.dataset is None:
            # No cached data available. Need to recreate the transformed data.
            input_data = get_input_datamodel_from_dataprep_json(self.dataprep_json,
                                                                self.log_message,
                                                                automl_settings=self.automl_settings,
                                                                logger=self.logger)

            if self.automl_settings.enable_onnx_compatible_models and onnx_cvt is not None:
                # Initialize the ONNX converter with the raw data and save metadata in the cache store.
                self._initialize_onnx_converter_with_cache_store(onnx_cvt=onnx_cvt,
                                                                 input_data=input_data,
                                                                 parent_run_id=self.parent_run_id,
                                                                 cache_store=cache_store,
                                                                 logger=self.logger)

            log_message(logger=self.logger, parent_run_id=self.parent_run_id, worker_id=self.worker_id,
                        message="Transformed_data_context is none, using dprep for fit")

            transformed_data_context = self._get_transformed_data_context(input_data,
                                                                          cache_store,
                                                                          verifier)

            self.dataset = training_utilities.init_client_dataset(
                transformed_data_context=transformed_data_context,
                cache_store=cache_store,
                automl_settings=self.automl_settings,
                remote=False,
                init_all_stats=False,
                keep_in_memory=False)

            self.logger.info(
                "Initialized ClientDatasets object from transformed_data_context.. "
                "dropping transformed_data_context.")
            self.clear_input_data([transformed_data_context])

        self.logger.info('Successfully recovering dataset from cache store for run {}.'.format(current_run.id))

    def _create_client(self, client_type):
        auth = AzureMLTokenAuthentication.create(self.aml_token,
                                                 AzureMLTokenAuthentication._convert_to_datetime(
                                                     self.aml_token_expiry),
                                                 self.service_url,
                                                 self.subscription_id,
                                                 self.resource_group,
                                                 self.workspace_name,
                                                 self.experiment_name,
                                                 self.parent_run_id)
        os.environ[HISTORY_SERVICE_ENDPOINT_KEY] = self.service_url
        service_context = ServiceContext(self.subscription_id,
                                         self.resource_group,
                                         self.workspace_name,
                                         None,
                                         auth)
        if(client_type == JASMINE_CLIENT):
            return JasmineClient(service_context, self.experiment_name,
                                 user_agent=client_type)
        elif(client_type == EXPERIMENT_CLIENT):
            return ExperimentClient(service_context, self.experiment_name,
                                    user_agent=client_type)

    def _get_transformed_data_context(self,
                                      input_data: _input_data_model,
                                      cache_store: CacheStore,
                                      verifier: VerifierManager) \
            -> Union[TransformedDataContext, StreamingTransformedDataContext]:
        with self.logger.log_activity(self.logger, activity_name='_setup_cache'):
            try:
                log_message(logger=self.logger, parent_run_id=self.parent_run_id, worker_id=self.worker_id,
                            message="Trying to setup cache")

                raw_data_context = RawDataContext(automl_settings_obj=self.automl_settings,
                                                  X=input_data.X,
                                                  y=input_data.y,
                                                  X_valid=input_data.X_valid,
                                                  y_valid=input_data.y_valid,
                                                  sample_weight=input_data.sample_weight,
                                                  sample_weight_valid=input_data.sample_weight_valid,
                                                  x_raw_column_names=input_data.x_raw_column_names,
                                                  cv_splits_indices=input_data.cv_splits_indices)

                feature_sweeping_config = self.feature_config_manager.get_feature_sweeping_config(
                    enable_feature_sweeping=self.automl_settings.enable_feature_sweeping,
                    parent_run_id=self.parent_run_id,
                    task_type=self.automl_settings.task_type)
                with self.logger.log_activity(self.logger, activity_name='transform_data'):
                    transformed_data_context = data_transformation\
                        .transform_data(raw_data_context=raw_data_context,
                                        preprocess=self.automl_settings.preprocess,
                                        logger=self.logger,
                                        cache_store=cache_store,
                                        is_onnx_compatible=self.automl_settings.enable_onnx_compatible_models,
                                        enable_feature_sweeping=self.automl_settings.enable_feature_sweeping,
                                        enable_dnn=self.automl_settings.enable_dnn,
                                        verifier=verifier,
                                        feature_sweeping_config=feature_sweeping_config)

                log_message(logger=self.logger, parent_run_id=self.parent_run_id, worker_id=self.worker_id,
                            message="Cache is setup")

                return transformed_data_context
            except Exception as e:
                log_message(logger=self.logger, logging_level=logging.ERROR, parent_run_id=self.parent_run_id,
                            worker_id=self.worker_id, message="Featurization failed with exception {0}".
                            format(e))
                raise

    def _load_data_from_cache(self, cache_store: CacheStore) -> Optional[ClientDatasets]:
        with self.logger.log_activity(self.logger, activity_name='_load_data_from_cache'):
            try:
                log_message(logger=self.logger, parent_run_id=self.parent_run_id, worker_id=self.worker_id,
                            message="Loading from cache")
                cache_store.load()
                dataset_dict = cache_store.get([self.DATASET_CACHED_KEY])
                if dataset_dict is not None:
                    return dataset_dict.get(self.DATASET_CACHED_KEY)
                log_message(logger=self.logger, parent_run_id=self.parent_run_id, worker_id=self.worker_id,
                            message="Failed to load from cache, failed to find {} in cache_store.".
                            format(self.DATASET_CACHED_KEY))
                return None
            except Exception as e:
                log_message(logger=self.logger, logging_level=logging.ERROR, parent_run_id=self.parent_run_id,
                            worker_id=self.worker_id,
                            message="Continuing without cache as trying to load from cache failed with exception {0}".
                            format(e))
                return None

    def _get_cache_store(self):
        data_store = self._get_data_store()

        return CacheStoreFactory.get_cache_store(enable_cache=True,
                                                 run_target='adb',
                                                 run_id=self.parent_run_id,
                                                 logger=self.logger,
                                                 data_store=data_store)

    def _get_data_store(self):
        try:
            experiment = self._rehydrate_experiment()
            return experiment.workspace.get_default_datastore()
        except Exception as e:
            log_message(logger=self.logger, logging_level=logging.ERROR, parent_run_id=self.parent_run_id,
                        worker_id=self.worker_id,
                        message="No default data store found {0}".
                        format(e))
            return None

    def _initialize_onnx_converter_with_cache_store(self,
                                                    onnx_cvt: OnnxConverter,
                                                    input_data: _input_data_model,
                                                    parent_run_id: str,
                                                    cache_store: Optional[CacheStore],
                                                    logger: logging.Logger) -> None:
        # Initialize the ONNX converter with the raw data and save metadata in the cache store.
        if cache_store is not None and self.automl_settings.enable_onnx_compatible_models:
            onnx_mdl_name = '{}[{}]'.format(OnnxConvertConstants.OnnxModelNamePrefix, parent_run_id)
            onnx_mdl_desc = {'ParentRunId': parent_run_id}
            logger.info('Initialize ONNX converter for run {}.'.format(parent_run_id))
            onnx_cvt.initialize_input(X=input_data.X,
                                      x_raw_column_names=input_data.x_raw_column_names,
                                      model_name=onnx_mdl_name,
                                      model_desc=onnx_mdl_desc)
            onnx_cvt_init_metadata_dict = onnx_cvt.get_init_metadata_dict()
            # If the cache store and the onnx converter init metadata are valid, save it into cache store.
            if (onnx_cvt_init_metadata_dict is not None and
                    onnx_cvt_init_metadata_dict):
                logger.info('Successfully initialized ONNX converter for run {}.'.format(parent_run_id))
                logger.info('Begin saving onnx initialization metadata for run {}.'.format(parent_run_id))
                cache_store.set(self.CACHE_STORE_KEY_ONNX_CONVERTER_INIT_METADATA, onnx_cvt_init_metadata_dict)
                logger.info('Successfully Saved onnx initialization metadata for run {}.'.format(parent_run_id))
            else:
                logger.info('Failed to initialize ONNX converter for run {}.'.format(parent_run_id))

    def __del__(self):
        """
        Clean up AutoML loggers and close files.
        """
        log_utils.cleanup_log_map(self.automl_settings.debug_log,
                                  self.automl_settings.verbosity)

        if self._usage_telemetry is not None:
            self._usage_telemetry.stop()

    def clear_input_data(self, input_data_list: List[Union[TransformedDataContext, Any]]) -> None:
        for input_data in input_data_list:
            if input_data is not None:
                input_data.X = None
                input_data.y = None
                input_data.X_valid = None
                input_data.y_valid = None
                if isinstance(input_data, TransformedDataContext):
                    input_data.cv_splits = None
                self._gc_object(input_data)

    def _gc_object(self, obj):
        if obj is not None:
            del obj
            gc.collect()
