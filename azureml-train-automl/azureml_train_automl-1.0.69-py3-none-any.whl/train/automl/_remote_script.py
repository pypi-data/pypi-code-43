# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Methods for AutoML remote runs."""
import json
import logging
import os
import sys
import time
from typing import Any, cast, Dict, Optional, Tuple, Union
from typing import List

import azureml.dataprep as dprep
from azureml._history.utils.constants import LOGS_AZUREML_DIR
from azureml._restclient.jasmine_client import JasmineClient
from azureml.core import Datastore, Run, Dataset
from azureml.data.azure_storage_datastore import AbstractAzureStorageDatastore
from azureml.data.constants import WORKSPACE_BLOB_DATASTORE
from azureml.dataprep.api.dataflow import DataflowValidationError
from azureml.telemetry import set_diagnostics_collection

from automl.client.core.common import constants
from automl.client.core.common import logging_utilities
from automl.client.core.common import utilities
from automl.client.core.common.exceptions import AutoMLException
from automl.client.core.common.activity_logger import TelemetryActivityLogger
from automl.client.core.runtime.cache_store import CacheStore
from automl.client.core.runtime.datasets import DatasetBase
from automl.client.core.runtime.cache_store import CacheException

from azureml.automl.core import data_transformation
from azureml.automl.core import dataprep_utilities
from azureml.automl.core import fit_pipeline as fit_pipeline_helper
from azureml.automl.core import training_utilities
from azureml.automl.core._experiment_observer import ExperimentStatus, ExperimentObserver
from azureml.automl.core.automl_pipeline import AutoMLPipeline
from azureml.automl.core.data_context import RawDataContext, TransformedDataContext
from azureml.automl.core.streaming_data_context import StreamingTransformedDataContext
from azureml.automl.core.faults_verifier import VerifierManager
from azureml.automl.core.onnx_convert import OnnxConverter, OnnxConvertConstants
from azureml.train.automl.constants import ComputeTargets
from azureml.train.automl.run import AutoMLRun
from azureml.train.automl.automl_explain_utilities import _automl_auto_mode_explain_model,\
    _automl_perform_best_run_explain_model, ModelExplanationRunId
from . import _automl
from ._azure_experiment_observer import AzureExperimentObserver
from ._azureautomlruncontext import AzureAutoMLRunContext
from ._azureautomlsettings import AzureAutoMLSettings
from ._cachestorefactory import CacheStoreFactory
from ._logging import get_logger
from .exceptions import ClientException, ConfigException, DataException
from .utilities import _load_user_script, _get_package_version
from ._automl_feature_config_manager import AutoMLFeatureConfigManager


CACHE_STORE_KEY_ONNX_CONVERTER_INIT_METADATA = '_CACHE_STORE_KEY_ONNX_CONVERTER_INIT_METADATA_'

# The base dataset object can be cached in the setup iteration (to be later re-used during model training),
# with the following key
DATASET_BASE_CACHE_KEY = 'dataset_cached_object'


def _parse_settings(automl_settings: str) -> Tuple[AzureAutoMLSettings, TelemetryActivityLogger]:
    if not os.path.exists(LOGS_AZUREML_DIR):
        os.makedirs(LOGS_AZUREML_DIR, exist_ok=True)
    automl_settings_obj = AzureAutoMLSettings.from_string_or_dict(automl_settings)
    set_diagnostics_collection(send_diagnostics=automl_settings_obj.send_telemetry,
                               verbosity=automl_settings_obj.telemetry_verbosity)
    handler = logging.StreamHandler(stream=sys.stdout)
    handler.setLevel(logging.DEBUG)
    handler.setFormatter(logging.Formatter('[%(levelname)s] %(message)s'))
    logger = get_logger(
        log_file_name=os.path.join(LOGS_AZUREML_DIR, "azureml_automl.log"), automl_settings=automl_settings_obj)
    logger.addHandler(handler)
    logger.setLevel(logging.DEBUG)
    return automl_settings_obj, logger


def _split_data_train_valid(logger: logging.Logger,
                            training_data: dprep.Dataflow) -> Tuple[dprep.Dataflow, dprep.Dataflow]:
    logger.info('Splitting input dataset into train & validation datasets')
    num_validation_rows = min(
        0.1 * training_data.shape[0],
        training_utilities.LargeDatasetLimit.MAX_ROWS_TO_SUBSAMPLE_FOR_VALIDATION_SET)
    sample_probability = num_validation_rows / training_data.shape[0]
    validation_data, training_data = training_data.random_split(sample_probability, seed=42)
    return validation_data, training_data


def _get_data_from_serialized_dataflow(dataprep_json: str,
                                       logger: logging.Logger,
                                       automl_settings_obj: AzureAutoMLSettings) -> Dict[str, Any]:
    logger.info('Deserializing dataflow.')
    dataflow_dict = dataprep_utilities.load_dataflows_from_json(dataprep_json)

    if automl_settings_obj.enable_streaming:
        if 'training_data' not in dataflow_dict \
                or automl_settings_obj.label_column_name is None:
            raise ConfigException("Streaming does not support X and y settings. "
                                  "Please provide 'training_data', 'validation_data' as DataFlow objects and "
                                  "'label_column_name' for target column name in AutoMLConfig.")

        fit_iteration_parameters_dict = dataflow_dict.copy()
        training_data = fit_iteration_parameters_dict.get('training_data')
        if training_data is None:
            raise DataflowValidationError("Training_data is not present in DataPrep JSON string")
        validation_data = fit_iteration_parameters_dict.get('validation_data')

        if validation_data is not None:
            # we're going to subsample the validation set to ensure we can compute the metrics in memory
            data_profile = validation_data.get_profile()
            validation_samples_count = data_profile.row_count
            max_validation_size = training_utilities.LargeDatasetLimit.MAX_ROWS_TO_SUBSAMPLE_FOR_VALIDATION_SET
            if validation_samples_count > max_validation_size:
                sample_probability = max_validation_size / validation_samples_count
                logger.warning(
                    'Subsampling the validation from {} samples with a probability of {}.'
                    .format(validation_samples_count, sample_probability))
                validation_data = validation_data.take_sample(probability=sample_probability, seed=42)
        else:
            validation_data, training_data = _split_data_train_valid(logger, training_data)

        fit_iteration_parameters_dict['training_data'] = training_data
        fit_iteration_parameters_dict['validation_data'] = validation_data

        columns_list = [automl_settings_obj.label_column_name]
        if automl_settings_obj.weight_column_name is not None:
            columns_list.append(automl_settings_obj.weight_column_name)

        # fill in x and y here so that other stuff works.
        fit_iteration_parameters_dict['X'] = training_data.drop_columns(columns_list)
        fit_iteration_parameters_dict['y'] = training_data.keep_columns(
            automl_settings_obj.label_column_name)
        fit_iteration_parameters_dict['X_valid'] = validation_data.drop_columns(columns_list)
        fit_iteration_parameters_dict['y_valid'] = validation_data.keep_columns(
            automl_settings_obj.label_column_name)

        fit_iteration_parameters_dict['x_raw_column_names'] = fit_iteration_parameters_dict['X'].head(1).columns.values

        if automl_settings_obj.weight_column_name is not None:
            fit_iteration_parameters_dict['sample_weight'] = training_data.keep_columns(
                automl_settings_obj.weight_column_name)
            fit_iteration_parameters_dict['sample_weight_valid'] = validation_data.keep_columns(
                automl_settings_obj.weight_column_name)

    else:
        if 'training_data' in dataflow_dict and automl_settings_obj.label_column_name is not None:
            df = dataflow_dict.get('training_data')  # type: dprep.Dataflow
            X, y, sample_weight = training_utilities._extract_data_from_combined_dataflow(
                df, automl_settings_obj.label_column_name, automl_settings_obj.weight_column_name)
            dataflow_dict['X'] = X
            dataflow_dict['y'] = y
            dataflow_dict['sample_weight'] = sample_weight
            dataflow_dict.pop('training_data')
        if 'validation_data' in dataflow_dict and automl_settings_obj.label_column_name is not None:
            df = dataflow_dict.get('validation_data')
            X_valid, y_valid, sample_weight_valid = training_utilities._extract_data_from_combined_dataflow(
                df, automl_settings_obj.label_column_name, automl_settings_obj.weight_column_name)
            dataflow_dict['X_valid'] = X_valid
            dataflow_dict['y_valid'] = y_valid
            dataflow_dict['sample_weight_valid'] = sample_weight_valid
            dataflow_dict.pop('validation_data')
        data_columns = ['X_valid', 'sample_weight', 'sample_weight_valid']
        label_columns = ['y', 'y_valid']

        fit_iteration_parameters_dict = {
            k: dataprep_utilities.retrieve_numpy_array(dataflow_dict.get(k))
            for k in data_columns
        }
        X = dataprep_utilities.retrieve_pandas_dataframe(dataflow_dict.get('X'))
        fit_iteration_parameters_dict['x_raw_column_names'] = X.columns.values
        if X.shape[1] == 1:
            # if the DF is a single column ensure the resulting output is a 1 dim array by converting
            # to series first.
            fit_iteration_parameters_dict['X'] = X[X.columns[0]].values
        else:
            fit_iteration_parameters_dict['X'] = X.values

        for k in label_columns:
            fit_iteration_parameters_dict[k] = dataprep_utilities.retrieve_numpy_array(
                dataflow_dict.get(k))

        cv_splits_dataflows = []
        i = 0
        while 'cv_splits_indices_{0}'.format(i) in dataflow_dict:
            cv_splits_dataflows.append(
                dataflow_dict['cv_splits_indices_{0}'.format(i)])
            i = i + 1

        fit_iteration_parameters_dict['cv_splits_indices'] = None if len(cv_splits_dataflows) == 0 \
            else dataprep_utilities.resolve_cv_splits_indices(cv_splits_dataflows)

    return fit_iteration_parameters_dict


def _get_inferred_types_dataflow(dflow: dprep.Dataflow,
                                 logger: logging.Logger) -> dprep.Dataflow:
    logger.info('Inferring type for feature columns.')
    set_column_type_dflow = dflow.builders.set_column_types()
    set_column_type_dflow.learn()
    set_column_type_dflow.ambiguous_date_conversions_drop()
    return set_column_type_dflow.to_dataflow()


def _get_dict_from_dataflow(dflow: Any,
                            automl_settings_obj: AzureAutoMLSettings,
                            logger: logging.Logger,
                            feature_columns: List[str],
                            label_column: str) -> Dict[str, Any]:
    fit_iteration_parameters_dict = {}  # type: Dict[str, Any]
    if not automl_settings_obj.enable_streaming:
        if len(feature_columns) == 0:
            X = dflow.drop_columns(label_column)
        else:
            X = dflow.keep_columns(feature_columns)

        X = _get_inferred_types_dataflow(X, logger)
        y = dflow.keep_columns(label_column)
        if automl_settings_obj.task_type == constants.Tasks.REGRESSION:
            y = y.to_number(label_column)

        logger.info('X: {}'.format(X))
        logger.info('y: {}'.format(y))

        _X = dataprep_utilities.retrieve_pandas_dataframe(X)
        _y = dataprep_utilities.retrieve_numpy_array(y)

        fit_iteration_parameters_dict = {
            "X": _X.values,
            "y": _y,
            "sample_weight": None,
            "x_raw_column_names": _X.columns.values,
            "X_valid": None,
            "y_valid": None,
            "sample_weight_valid": None,
            "X_test": None,
            "y_test": None,
            "cv_splits_indices": None,
        }
    else:
        if len(feature_columns) > 0:
            feature_columns_with_label = feature_columns + [label_column]
            dflow1 = dflow.keep_columns(feature_columns_with_label)
            training_data = dflow1
        else:
            training_data = dflow

        training_data = _get_inferred_types_dataflow(training_data, logger)
        validation_data, training_data = _split_data_train_valid(logger, training_data)

        fit_iteration_parameters_dict['training_data'] = training_data
        fit_iteration_parameters_dict['validation_data'] = validation_data
        fit_iteration_parameters_dict["X"] = training_data.drop_columns(label_column)
        fit_iteration_parameters_dict["y"] = training_data.keep_columns(label_column)
        fit_iteration_parameters_dict["x_raw_column_names"] = fit_iteration_parameters_dict["X"].head(1)\
            .columns.tolist()
        fit_iteration_parameters_dict["X_valid"] = validation_data.drop_columns(label_column)
        fit_iteration_parameters_dict["y_valid"] = validation_data.keep_columns(label_column)

    return fit_iteration_parameters_dict


def _get_data_from_dataprep_options(dataprep_json_obj: Dict[str, Any],
                                    automl_settings_obj: AzureAutoMLSettings,
                                    logger: logging.Logger) -> Dict[str, Any]:
    logger.info('Creating dataflow from options.')
    data_store_name = dataprep_json_obj['datastoreName']  # mandatory
    data_path = dataprep_json_obj['dataPath']  # mandatory
    label_column = dataprep_json_obj['label']  # mandatory
    separator = dataprep_json_obj.get('columnSeparator', ',')
    quoting = dataprep_json_obj.get('ignoreNewlineInQuotes', False)
    skip_rows = dataprep_json_obj.get('skipRows', 0)
    feature_columns = dataprep_json_obj.get('features', [])
    encoding = getattr(dprep.FileEncoding, cast(str, dataprep_json_obj.get('encoding')), dprep.FileEncoding.UTF8)
    if dataprep_json_obj.get('promoteHeader', True):
        header = dprep.PromoteHeadersMode.CONSTANTGROUPED
    else:
        header = dprep.PromoteHeadersMode.NONE
    ws = Run.get_context().experiment.workspace
    data_store = Datastore(ws, data_store_name)
    dflow = dprep.read_csv(path=data_store.path(data_path),
                           separator=separator,
                           header=header,
                           encoding=encoding,
                           quoting=quoting,
                           skip_rows=skip_rows)
    return _get_dict_from_dataflow(dflow, automl_settings_obj, logger, feature_columns, label_column)


def _get_data_from_dataset_options(dataprep_json_obj: Dict[str, Any],
                                   automl_settings_obj: AzureAutoMLSettings,
                                   logger: logging.Logger) -> Dict[str, Any]:
    logger.info('Creating dataflow from dataset.')
    dataset_id = dataprep_json_obj['datasetId']  # mandatory
    label_column = dataprep_json_obj['label']  # mandatory
    feature_columns = dataprep_json_obj.get('features', [])

    ws = Run.get_context().experiment.workspace
    dataset = Dataset.get(ws, id=dataset_id)
    dflow = dataset.definition
    return _get_dict_from_dataflow(dflow, automl_settings_obj, logger, feature_columns, label_column)


def _get_data_from_dataprep(dataprep_json: str,
                            automl_settings_obj: AzureAutoMLSettings,
                            logger: logging.Logger) -> Dict[str, Any]:
    try:
        logger.info('Resolving dataflows using dprep json.')
        logger.info('DataPrep version: {}'.format(dprep.__version__))
        try:
            from azureml._base_sdk_common import _ClientSessionId
            logger.info('DataPrep log client session id: {}'.format(_ClientSessionId))
        except Exception:
            logger.info('Cannot get DataPrep log client session id')

        dataprep_json_obj = json.loads(dataprep_json)
        if 'activities' in dataprep_json_obj:
            # json is serialized dataflows
            fit_iteration_parameters_dict = _get_data_from_serialized_dataflow(dataprep_json,
                                                                               logger,
                                                                               automl_settings_obj)
        elif 'datasetId' in dataprep_json_obj:
            # json is dataset options
            fit_iteration_parameters_dict = _get_data_from_dataset_options(dataprep_json_obj,
                                                                           automl_settings_obj,
                                                                           logger)
        else:
            # json is dataprep options
            fit_iteration_parameters_dict = _get_data_from_dataprep_options(dataprep_json_obj,
                                                                            automl_settings_obj,
                                                                            logger)
        logger.info('Successfully retrieved data using dataprep.')
        return fit_iteration_parameters_dict
    except Exception as e:
        msg = str(e)
        if "The provided path is not valid." in msg:
            raise ConfigException.from_exception(e)
        elif "Required secrets are missing. Please call use_secrets to register the missing secrets." in msg:
            raise ConfigException.from_exception(e)
        elif isinstance(e, json.JSONDecodeError):
            raise ConfigException.from_exception(e, 'Invalid dataprep JSON string passed.')
        elif isinstance(e, DataflowValidationError):
            raise DataException.from_exception(e)
        elif not isinstance(e, AutoMLException):
            raise ClientException.from_exception(e)
        else:
            raise


def _init_directory(directory: Optional[str], logger: logging.Logger) -> str:
    if directory is None:
        directory = os.getcwd()
        logger.info('Directory was None, using current working directory.')
    logger.info('Adding {} to system path.'.format(directory))
    sys.path.append(directory)
    # create the outputs folder
    logger.info('Creating output folder {}.'.format(os.path.abspath('./outputs')))
    os.makedirs('./outputs', exist_ok=True)
    return directory


def _get_parent_run_id(run_id: str) -> str:
    parent_run_length = run_id.rfind("_")
    return run_id[0:parent_run_length]


def _prepare_data(dataprep_json: str,
                  automl_settings_obj: AzureAutoMLSettings,
                  script_directory: str,
                  entry_point: str,
                  logger: logging.Logger,
                  verifier: Optional[VerifierManager] = None) -> Dict[str, Any]:
    if dataprep_json:
        data_dict = _get_data_from_dataprep(dataprep_json, automl_settings_obj, logger)
    else:
        script_path = os.path.join(script_directory, entry_point)
        user_module = _load_user_script(script_path, logger, False)
        data_dict = training_utilities._extract_user_data(user_module)

    data_dict['X'], data_dict['y'], data_dict['X_valid'], data_dict['y_valid'] = \
        automl_settings_obj.rule_based_validation(data_dict.get('X'),
                                                  data_dict.get('y'),
                                                  data_dict.get('X_valid'),
                                                  data_dict.get('y_valid'),
                                                  data_dict.get('cv_splits_indices'),
                                                  logger=logger,
                                                  verifier=verifier)
    return data_dict


def _transform_and_validate_input_data(
        fit_iteration_parameters_dict: Dict[str, Any],
        automl_settings_obj: AzureAutoMLSettings,
        logger: logging.Logger,
        cache_store: Optional[CacheStore],
        experiment_observer: Optional[ExperimentObserver] = None,
        verifier: Optional[VerifierManager] = None
) -> Union[TransformedDataContext, StreamingTransformedDataContext]:
    start = time.time()
    logger.info('Getting transformed data context.')
    raw_data_context = RawDataContext(automl_settings_obj=automl_settings_obj,
                                      X=fit_iteration_parameters_dict.get('X'),
                                      y=fit_iteration_parameters_dict.get('y'),
                                      X_valid=fit_iteration_parameters_dict.get('X_valid'),
                                      y_valid=fit_iteration_parameters_dict.get('y_valid'),
                                      sample_weight=fit_iteration_parameters_dict.get('sample_weight'),
                                      sample_weight_valid=fit_iteration_parameters_dict.get('sample_weight_valid'),
                                      x_raw_column_names=fit_iteration_parameters_dict.get('x_raw_column_names'),
                                      cv_splits_indices=fit_iteration_parameters_dict.get('cv_splits_indices'),
                                      training_data=fit_iteration_parameters_dict.get('training_data'),
                                      validation_data=fit_iteration_parameters_dict.get('validation_data')
                                      )
    if cache_store is not None:
        logger.info('Using {} for caching transformed data.'.format(type(cache_store).__name__))

    experiment = None
    parent_run_id = None
    try:
        experiment, run_id = Run._load_scope()
        parent_run_id = _get_parent_run_id(run_id)
    except Exception:
        pass  # No environment variable found, so must be running from unit test.

    feature_sweeping_config = {}  # type: Dict[str, Any]
    if experiment is not None and parent_run_id is not None:
        jasmine_client = JasmineClient(experiment.workspace.service_context, experiment.name,
                                       user_agent=type(JasmineClient).__name__)
        feature_config_manager = AutoMLFeatureConfigManager(jasmine_client=jasmine_client)
        feature_sweeping_config = feature_config_manager.get_feature_sweeping_config(
            enable_feature_sweeping=automl_settings_obj.enable_feature_sweeping,
            parent_run_id=parent_run_id,
            task_type=automl_settings_obj.task_type)

    transformed_data_context = data_transformation.transform_data(
        raw_data_context=raw_data_context,
        preprocess=automl_settings_obj.preprocess,
        cache_store=cache_store,
        is_onnx_compatible=automl_settings_obj.enable_onnx_compatible_models,
        enable_feature_sweeping=automl_settings_obj.enable_feature_sweeping,
        enable_dnn=automl_settings_obj.enable_dnn,
        experiment_observer=experiment_observer,
        logger=logger,
        verifier=verifier,
        enable_streaming=automl_settings_obj.enable_streaming,
        feature_sweeping_config=feature_sweeping_config)

    end = time.time()
    logger.info('Got transformed data context after {}s.'.format(end - start))
    return transformed_data_context


def _set_problem_info_for_setup(
        setup_run: Run,
        fit_iteration_parameters_dict: Dict[str, Any],
        automl_settings_obj: AzureAutoMLSettings,
        logger: logging.Logger,
        cache_store: Optional[CacheStore],
        experiment_observer: ExperimentObserver,
        verifier: Optional[VerifierManager] = None) -> Union[TransformedDataContext, StreamingTransformedDataContext]:

    if cache_store is not None:
        try:
            transformed_data_context = _transform_and_validate_input_data(
                fit_iteration_parameters_dict,
                automl_settings_obj,
                logger,
                cache_store,
                experiment_observer,
                verifier=verifier)
            logger.info('Setting problem info.')
            _automl._set_problem_info(
                transformed_data_context.X,
                transformed_data_context.y,
                automl_settings=automl_settings_obj,
                current_run=setup_run,
                transformed_data_context=transformed_data_context,
                cache_store=cache_store,
                logger=logger
            )
            return transformed_data_context
        except CacheException as e:
            # Log warning and retry without caching.
            logger.warning('Setup failed ({}), falling back to alternative method.'.format(e))

    logger.info('Start setting problem info using old model.')
    transformed_data_context = _transform_and_validate_input_data(
        fit_iteration_parameters_dict,
        automl_settings_obj,
        logger,
        cache_store=None,
        experiment_observer=experiment_observer, verifier=verifier)
    _automl._set_problem_info(
        X=fit_iteration_parameters_dict.get('X'),
        y=fit_iteration_parameters_dict.get('y'),
        automl_settings=automl_settings_obj,
        current_run=setup_run,
        logger=logger,
        transformed_data_context=transformed_data_context
    )
    return transformed_data_context


def _get_cache_data_store(current_run: Run, logger: logging.Logger) -> Optional[AbstractAzureStorageDatastore]:
    data_store = None
    start = time.time()
    try:
        data_store = current_run.experiment.workspace.get_default_datastore()
        logger.info('Successfully got the cache data store, caching enabled.')
    except Exception as e:
        logger.warning('Failed to get the cache data store ({}), '
                       'trying to set {} as default data store.'.format(e, WORKSPACE_BLOB_DATASTORE))
        try:
            Datastore.get(current_run.experiment.workspace, WORKSPACE_BLOB_DATASTORE).set_as_default()
            data_store = current_run.experiment.workspace.get_default_datastore()
            logger.info('Successfully got the cache data store after setting default data store, caching enabled.')
        except Exception as e:
            raise ClientException('Failed to get the cache data store ({})'.format(e))
    end = time.time()
    logger.info('Took {} seconds to retrieve cache data store'.format(end - start))
    return data_store


def _initialize_onnx_converter_with_cache_store(automl_settings_obj: AzureAutoMLSettings,
                                                onnx_cvt: OnnxConverter,
                                                fit_iteration_parameters_dict: Dict[str, Any],
                                                parent_run_id: str,
                                                cache_store: Optional[CacheStore],
                                                logger: logging.Logger) -> None:
    if automl_settings_obj.enable_onnx_compatible_models:
        # Initialize the ONNX converter, get the converter metadata.
        onnx_mdl_name = '{}[{}]'.format(OnnxConvertConstants.OnnxModelNamePrefix, parent_run_id)
        onnx_mdl_desc = {'ParentRunId': parent_run_id}
        logger.info('Initialize ONNX converter for run {}.'.format(parent_run_id))
        onnx_cvt.initialize_input(X=fit_iteration_parameters_dict.get('X'),
                                  x_raw_column_names=fit_iteration_parameters_dict.get("x_raw_column_names"),
                                  model_name=onnx_mdl_name,
                                  model_desc=onnx_mdl_desc)
        onnx_cvt_init_metadata_dict = onnx_cvt.get_init_metadata_dict()
        # If the cache store and the onnx converter init metadata are valid, save it into cache store.
        if (cache_store is not None and
                onnx_cvt_init_metadata_dict is not None and
                onnx_cvt_init_metadata_dict):
            logger.info('Successfully initialized ONNX converter for run {}.'.format(parent_run_id))
            logger.info('Begin saving onnx initialization metadata for run {}.'.format(parent_run_id))
            cache_store.add([CACHE_STORE_KEY_ONNX_CONVERTER_INIT_METADATA], [onnx_cvt_init_metadata_dict])
            logger.info('Successfully Saved onnx initialization metadata for run {}.'.format(parent_run_id))
        else:
            logger.info('Failed to initialize ONNX converter for run {}.'.format(parent_run_id))


def _load_data_from_cache(cache_store: CacheStore, logger: logging.Logger) -> Optional[DatasetBase]:
    try:
        cache_store.load()
        dataset_dict = cache_store.get([DATASET_BASE_CACHE_KEY])
        if dataset_dict is not None:
            result = dataset_dict.get(DATASET_BASE_CACHE_KEY, None)    # type: Optional[DatasetBase]
            if result:
                logger.info('Successfully loaded the AutoML Dataset from cache.')
                return result
        logger.warning("Failed to find {} in cache_store.".format(DATASET_BASE_CACHE_KEY))
        return None
    except CacheException as e:
        logger.warning("Failed to initialize Datasets from the cache, proceeding with re-transforming the "
                       "input data. Reason: {}".format(e))
        return None
    except Exception as e:
        logger.warning('Fatal exception encountered while trying to load data from cache: {}'.format(e))
        raise e


def _recover_dataset(
        script_directory: str,
        automl_settings: str,
        run_id: str,
        dataprep_json: str,
        entry_point: str,
        onnx_cvt: Optional[Any] = None,
        **kwargs: Any
) -> Any:
    automl_settings_obj, logger = _parse_settings(automl_settings)
    current_run = Run.get_submitted_run()
    logger.update_default_properties({
        "parent_run_id": _get_parent_run_id(current_run.id),
        "child_run_id": current_run.id
    })
    script_directory = _init_directory(directory=script_directory, logger=logger)
    data_store = _get_cache_data_store(current_run, logger)
    parent_run_id = _get_parent_run_id(run_id)

    cache_store = _get_cache_store(data_store=data_store, run_id=parent_run_id, logger=logger)
    dataset = _load_data_from_cache(cache_store, logger)

    if dataset is None:
        logger.info('Could not load data from cache, preparing to pull data from dataprep or user script.')
        fit_iteration_parameters_dict = _prepare_data(
            dataprep_json=dataprep_json,
            automl_settings_obj=automl_settings_obj,
            script_directory=script_directory,
            entry_point=entry_point,
            logger=logger
        )   # type: Dict[str, Any]

        if fit_iteration_parameters_dict is None:
            raise DataException('Invalid raw data returned from _prepare_data().')

        # Initialize the ONNX converter with raw data and cache the metadata.
        if automl_settings_obj.enable_onnx_compatible_models and onnx_cvt is not None:
            _initialize_onnx_converter_with_cache_store(
                automl_settings_obj=automl_settings_obj,
                onnx_cvt=onnx_cvt,
                fit_iteration_parameters_dict=fit_iteration_parameters_dict,
                parent_run_id=parent_run_id,
                cache_store=cache_store,
                logger=logger)

        transformed_data_context = _transform_and_validate_input_data(fit_iteration_parameters_dict,
                                                                      automl_settings_obj=automl_settings_obj,
                                                                      logger=logger,
                                                                      cache_store=cache_store)

        dataset = training_utilities.init_dataset(
            transformed_data_context=transformed_data_context,
            cache_store=cache_store,
            automl_settings=automl_settings_obj,
            remote=True,
            init_all_stats=False,
            keep_in_memory=False)
        logger.info("Initialized AutoML Dataset from transformed_data_context.")

        logger.info("Deleting transformed_data_context.")
        del transformed_data_context

        logger.info("Deleting input data")
        del fit_iteration_parameters_dict
    else:
        logger.info("Recovered dataset using datastore")

    return dataset


def model_exp_wrapper(
        script_directory: str,
        automl_settings: str,
        run_id: str,
        child_run_id: str,
        dataprep_json: str,
        entry_point: str,
        **kwargs: Any
) -> Dict[str, Any]:
    """
    Code for best run model explanations iteration in remote runs.
    """
    model_exp_output = {}  # type: Dict[str, Any]
    automl_settings_obj, logger = _parse_settings(automl_settings)
    pkg_ver = _get_package_version()
    logger.info('Using SDK version {}'.format(pkg_ver))
    current_run = Run.get_submitted_run()
    try:
        logger.update_default_properties({
            "parent_run_id": _get_parent_run_id(current_run.id),
            "child_run_id": current_run.id
        })
        parent_run_id = _get_parent_run_id(run_id)
        dataset = _recover_dataset(script_directory, automl_settings, run_id,
                                   dataprep_json, entry_point)

        if not child_run_id:
            logger.info('Beginning best run remote model explanations for run {}.'.format(parent_run_id))
            print('Beginning best run remote model explanations for run {}.'.format(parent_run_id))

            # Get the best run model explanation
            parent_run = AutoMLRun(current_run.experiment, parent_run_id)
            experiment_observer = AzureExperimentObserver(parent_run, file_logger=logger)
            _automl_perform_best_run_explain_model(parent_run, dataset, automl_settings_obj,
                                                   logger, current_run=current_run,
                                                   experiment_observer=experiment_observer)
        else:
            logger.info('Beginning on-demand remote model explanations for run {}.'.format(child_run_id))
            print('Beginning on-demand remote model explanations for run {}.'.format(child_run_id))

            child_run = Run(current_run.experiment, child_run_id)
            if current_run is not None:
                child_run.set_tags({ModelExplanationRunId: str(current_run.id)})

            # Get the model explanation for the child run
            with dataset.open_dataset():
                _automl_auto_mode_explain_model(child_run, dataset,
                                                automl_settings_obj.max_cores_per_iteration,
                                                logger)

        return model_exp_output
    except Exception as e:
        logger.info("Error in fit_pipeline part of driver_wrapper.")
        current_run.fail(
            error_details=e, error_code=utilities.get_error_code(e))
        raise


def driver_wrapper(
        script_directory: str,
        automl_settings: str,
        run_id: str,
        training_percent: int,
        iteration: int,
        pipeline_spec: str,
        pipeline_id: str,
        dataprep_json: str,
        entry_point: str,
        **kwargs: Any
) -> Dict[str, Any]:
    """
    Code for iterations in remote runs.
    """
    automl_settings_obj, logger = _parse_settings(automl_settings)
    pkg_ver = _get_package_version()
    logger.info('Using SDK version {}'.format(pkg_ver))
    current_run = Run.get_submitted_run()
    try:
        logger.update_default_properties({
            "parent_run_id": _get_parent_run_id(current_run.id),
            "child_run_id": current_run.id
        })
        logger.info('Beginning AutoML remote driver for run {}.'.format(run_id))

        script_directory = _init_directory(directory=script_directory, logger=logger)
        data_store = _get_cache_data_store(current_run, logger)
        parent_run_id = _get_parent_run_id(run_id)
        cache_store = _get_cache_store(data_store=data_store, run_id=parent_run_id, logger=logger)

        set_automl_settings_streaming_compatible(logger, dataprep_json, automl_settings_obj)

        onnx_cvt = None
        if automl_settings_obj.enable_onnx_compatible_models:
            enable_split_onnx_models = automl_settings_obj.enable_split_onnx_featurizer_estimator_models
            onnx_cvt = OnnxConverter(logger=logger,
                                     version=pkg_ver,
                                     is_onnx_compatible=automl_settings_obj.enable_onnx_compatible_models,
                                     enable_split_onnx_featurizer_estimator_models=enable_split_onnx_models)
            onnx_mdl_name = 'AutoML_ONNX_Model_[{}]'.format(parent_run_id)
            onnx_mdl_desc = {'ParentRunId': parent_run_id}

        dataset = _recover_dataset(script_directory, automl_settings, run_id,
                                   dataprep_json, entry_point, onnx_cvt)

        if automl_settings_obj.enable_onnx_compatible_models and onnx_cvt is not None:
            if cache_store is not None and not onnx_cvt.is_initialized():
                # Try to initialize the ONNX converter with cached converter metadata if it wasn't initialized
                # in the previous step.
                logger.info('Get ONNX converter init metadata for run {}.'.format(run_id))
                cache_store.load()
                cached_data_dict = cache_store.get([CACHE_STORE_KEY_ONNX_CONVERTER_INIT_METADATA])
                if cached_data_dict is not None and cached_data_dict:
                    onnx_cvt_init_metadata_dict = cached_data_dict.get(
                        CACHE_STORE_KEY_ONNX_CONVERTER_INIT_METADATA, None)  # type: Optional[Dict[str, Any]]
                    if onnx_cvt_init_metadata_dict is not None:
                        logger.info('Initialize ONNX converter with cached metadata run {}.'.format(run_id))
                        onnx_cvt.initialize_with_metadata(metadata_dict=onnx_cvt_init_metadata_dict,
                                                          model_name=onnx_mdl_name,
                                                          model_desc=onnx_mdl_desc)

            if onnx_cvt.is_initialized():
                logger.info('Successfully initialized ONNX converter for run {}.'.format(run_id))
            else:
                logger.info('Failed to initialize ONNX converter for run {}.'.format(run_id))

        logger.info('Starting the run.')
        child_run_metrics = Run.get_context()
        automl_run_context = AzureAutoMLRunContext(child_run_metrics)
        automl_pipeline = AutoMLPipeline(automl_run_context, pipeline_spec, pipeline_id, training_percent / 100)

        # Dataset will have a valid value for # of CV splits if we were to do auto CV.
        # Set the value of n_cross_validations in AutoML settings if that were the case
        if automl_settings_obj.n_cross_validations is None and dataset.get_num_auto_cv_splits() is not None:
            n_cv = dataset.get_num_auto_cv_splits()
            logger.info("Number of cross-validations in Dataset is {}.".format(n_cv))
            automl_settings_obj.n_cross_validations = None if n_cv == 0 else n_cv

    except Exception as e:
        logger.info("Error in preparing part of driver_wrapper.")
        current_run.fail(
            error_details=e, error_code=utilities.get_error_code(e))
        logging_utilities.log_traceback(e, logger)
        raise

    try:
        parent_run = Run(current_run.experiment, parent_run_id)
        # exception if fit_pipeline should already been logged and saved to rundto.error.
        fit_output = fit_pipeline_helper.fit_pipeline(
            automl_pipeline=automl_pipeline,
            automl_settings=automl_settings_obj,
            automl_run_context=automl_run_context,
            remote=True,
            logger=logger,
            dataset=dataset,
            onnx_cvt=onnx_cvt,
            bypassing_model_explain=parent_run.get_tags().get('model_explain_run'))
        result = fit_output.get_output_dict()
        logger.info('Fit pipeline returned result {}'.format(result))
        if fit_output.errors:
            for fit_exception in fit_output.errors.values():
                if fit_exception.get("is_critical"):
                    exception = cast(BaseException, fit_exception.get("exception"))
                    raise exception.with_traceback(exception.__traceback__)
        score = fit_output.primary_metric
        duration = fit_output.actual_time
        logger.info('Child run completed with score {} after {} seconds.'.format(score, duration))
        return result
    except Exception as e:
        logger.info("Error in fit_pipeline part of driver_wrapper.")
        current_run.fail(
            error_details=e, error_code=utilities.get_error_code(e))
        raise


def _get_cache_store(data_store: Optional[AbstractAzureStorageDatastore],
                     run_id: str,
                     logger: logging.Logger) -> CacheStore:
    cache_location = '{0}/{1}'.format('_remote_cache_directory_', run_id)

    os.makedirs(cache_location, exist_ok=True)
    return CacheStoreFactory.get_cache_store(enable_cache=True,
                                             run_target=ComputeTargets.AMLCOMPUTE,
                                             run_id=run_id,
                                             temp_location=cache_location,
                                             logger=logger,
                                             data_store=data_store)


def set_automl_settings_streaming_compatible(logger: logging.Logger,
                                             dataprep_json: str,
                                             automl_settings_obj: AzureAutoMLSettings) -> None:
    # if streaming is enabled do checks if automl settings are compatible.
    if automl_settings_obj.enable_streaming:
        # disable streaming if it is ADB or forecasting
        if automl_settings_obj.spark_context is not None:
            logger.warning('On ADB streaming is not supported, so disable streaming')
            automl_settings_obj.enable_streaming = False
            return

        if automl_settings_obj.is_timeseries is True:
            logger.warning('For forecasting streaming is not supported, so disable streaming')
            automl_settings_obj.enable_streaming = False
            return

        # check if UX and update the settings appropriately
        dataprep_json_obj = json.loads(dataprep_json)
        if 'activities' not in dataprep_json_obj:
            # for UI we need to set the label_column_name
            if automl_settings_obj.label_column_name is None:
                automl_settings_obj.label_column_name = dataprep_json_obj.get('label', None)
                logger.info('Set label_column_name to be {}.'.format(automl_settings_obj.label_column_name))

            if automl_settings_obj.n_cross_validations is not None:
                # set n_cross_validations to None as we have decided to do streaming
                automl_settings_obj.n_cross_validations = None
                logger.info('Set n_cross_validations to be None.')

        if automl_settings_obj.n_cross_validations is not None:
            raise ConfigException("Streaming is enabled due to the size of the data."
                                  "'n_cross_validations' option is not supported. Please re-run without that setting.")

        if(automl_settings_obj.enable_stack_ensembling is True):
            logger.warning('Streaming is enabled due to the size of the data, so disabling stack ensemble')
            automl_settings_obj.enable_stack_ensembling = False

        if(automl_settings_obj.enable_ensembling is True):
            logger.warning('Streaming is enabled due to the size of the data, so disabling voting ensemble')
            automl_settings_obj.enable_ensembling = False

        if automl_settings_obj.model_explainability is True:
            raise ConfigException("Streaming is enabled due to the size of the data."
                                  "'model_explainability' option is not supported. Please re-run without that "
                                  "setting.")

        if automl_settings_obj.enable_onnx_compatible_models is True:
            raise ConfigException("Streaming is enabled due to the size of the data."
                                  "'enable_onnx_compatible_models' option is not supported. Please re-run without "
                                  "that setting.")


def setup_wrapper(
        script_directory: Optional[str],
        dataprep_json: str,
        entry_point: str,
        automl_settings: str,
        task_type: str,
        preprocess: Optional[bool],
        enable_subsampling: bool,
        num_iterations: int,
        **kwargs: Any
) -> None:
    """
    Code for setup iterations for AutoML remote runs.
    """

    verifier = VerifierManager()

    parent_run = None
    automl_settings_obj, logger = _parse_settings(automl_settings)
    pkg_ver = _get_package_version()
    logger.info('Using SDK version {}'.format(pkg_ver))
    setup_run = Run.get_submitted_run()
    try:
        parent_run_id = _get_parent_run_id(setup_run.id)
        # get the parent run instance to be able to report preprocessing progress on it and set error.
        parent_run = Run(setup_run.experiment, parent_run_id)

        logger.update_default_properties({
            "parent_run_id": parent_run_id,
            "child_run_id": setup_run.id
        })
        logger.info('Beginning AutoML remote setup iteration for run {}.'.format(setup_run.id))

        script_directory = _init_directory(directory=script_directory, logger=logger)
        cache_data_store = _get_cache_data_store(setup_run, logger)

        set_automl_settings_streaming_compatible(logger, dataprep_json, automl_settings_obj)

        fit_iteration_parameters_dict = _prepare_data(
            dataprep_json=dataprep_json,
            automl_settings_obj=automl_settings_obj,
            script_directory=script_directory,
            entry_point=entry_point,
            logger=logger,
            verifier=verifier
        )

        experiment_observer = AzureExperimentObserver(parent_run, file_logger=logger)

        # Get the cache store.
        cache_store = _get_cache_store(data_store=cache_data_store, run_id=parent_run_id, logger=logger)

        if automl_settings_obj.enable_onnx_compatible_models:
            # Initialize the ONNX converter and save metadata in the cache store.
            enable_split_onnx_models = automl_settings_obj.enable_split_onnx_featurizer_estimator_models
            onnx_cvt = OnnxConverter(logger=logger,
                                     version=pkg_ver,
                                     is_onnx_compatible=automl_settings_obj.enable_onnx_compatible_models,
                                     enable_split_onnx_featurizer_estimator_models=enable_split_onnx_models)
            _initialize_onnx_converter_with_cache_store(automl_settings_obj=automl_settings_obj,
                                                        onnx_cvt=onnx_cvt,
                                                        fit_iteration_parameters_dict=fit_iteration_parameters_dict,
                                                        parent_run_id=parent_run_id,
                                                        cache_store=cache_store,
                                                        logger=logger)

        # Validate training data.
        logger.info('Validating training data.')
        X = fit_iteration_parameters_dict.get('X')
        y = fit_iteration_parameters_dict.get('y')
        X_valid = fit_iteration_parameters_dict.get('X_valid')
        y_valid = fit_iteration_parameters_dict.get('y_valid')
        sample_weight = fit_iteration_parameters_dict.get('sample_weight')
        sample_weight_valid = fit_iteration_parameters_dict.get('sample_weight_valid')
        cv_splits_indices = fit_iteration_parameters_dict.get('cv_splits_indices')
        x_raw_column_names = fit_iteration_parameters_dict.get('x_raw_column_names')

        if automl_settings_obj.enable_streaming and cv_splits_indices is not None:
            raise ConfigException("Streaming is enabled due to the size of the data."
                                  "'cv_splits_indices' option is not supported. Please re-run without that setting.")

        training_utilities.validate_training_data(
            X=X,
            y=y,
            X_valid=X_valid,
            y_valid=y_valid,
            sample_weight=sample_weight,
            sample_weight_valid=sample_weight_valid,
            cv_splits_indices=cv_splits_indices,
            automl_settings=automl_settings_obj)
        if automl_settings_obj.is_timeseries:
            training_utilities.validate_timeseries_training_data(
                X=X,
                y=y,
                X_valid=X_valid,
                y_valid=y_valid,
                sample_weight=sample_weight,
                sample_weight_valid=sample_weight_valid,
                cv_splits_indices=cv_splits_indices,
                x_raw_column_names=x_raw_column_names,
                automl_settings=automl_settings_obj
            )

        logger.info('Input data successfully validated.')

        # Transform raw input, validate and save to cache store.
        logger.info('Set problem info. AutoML remote setup iteration for run {}.'.format(setup_run.id))
        transformed_data_context = _set_problem_info_for_setup(setup_run,
                                                               fit_iteration_parameters_dict,
                                                               automl_settings_obj,
                                                               logger,
                                                               cache_store,
                                                               experiment_observer,
                                                               verifier=verifier)

        try:
            dataset = training_utilities.init_dataset(
                transformed_data_context=transformed_data_context,
                cache_store=cache_store,
                automl_settings=automl_settings_obj,
                remote=True,
                init_all_stats=False,
                keep_in_memory=False)
            cache_store.set(DATASET_BASE_CACHE_KEY, dataset)
            logger.info("Initialized Datasets from transformed_data_context during setup.")
        except Exception as e:
            logger.warning("Failed to initialize Datasets object from transformed_data_context. We will need to "
                           "re-transform the input data for every individual iteration moving forward."
                           "Exception: {}".format(e))

        if verifier is not None:
            parent_run_context = AzureAutoMLRunContext(parent_run)
            verifier.write_result_file(parent_run_context, logger)

        logger.info('Setup for run id {} finished successfully.'.format(setup_run.id))

        experiment_observer.report_status(ExperimentStatus.ModelSelection, "Beginning model selection.")
    except Exception as e:
        setup_run.fail(
            error_details=e, error_code=utilities.get_error_code(e))
        logger.info("Error in setup_wrapper.")
        logging_utilities.log_traceback(e, logger)
        raise
