# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""
The automated machine learning Run class.

Provides methods for starting/stopping runs, monitoring run status, and retrieving model output.
"""
from typing import Dict, Optional, Any, Tuple
import datetime
import json
import logging
import os
import pickle
import sys
import time

import numpy as np
import pandas as pd
from automl.client.core.common import logging_utilities
from azureml.automl.core.data_context import TransformedDataContext
from azureml.automl.core.dataset_utilities import convert_inputs, convert_inputs_dataset
from azureml.automl.core.package_utilities import (_has_version_discrepancies,
                                                   get_sdk_dependencies)
from automl.client.core.runtime.metrics import minimize_or_maximize
from automl.client.core.common.utilities import _get_max_min_comparator
from azureml.automl.core.onnx_convert import OnnxConverter, OnnxConvertConstants

from msrest.exceptions import HttpOperationError

from azureml._restclient.jasmine_client import JasmineClient
from azureml._restclient.constants import AUTOML_RUN_USER_AGENT, RunStatus
from azureml.automl.core.console_interface import ConsoleInterface
from azureml.core import Run
from azureml.core.model import Model
from azureml.exceptions import ExperimentExecutionException, UserErrorException, \
    ServiceException as AzureMLServiceException
from azureml.telemetry import set_diagnostics_collection

from . import _azureautomlclient, _constants_azureml, _logging, constants
from ._azureautomlsettings import AzureAutoMLSettings
from ._cachestorefactory import CacheStoreFactory
from ._constants_azureml import Properties
from ._remote_console_interface import RemoteConsoleInterface
from .exceptions import (ConfigException,
                         InvalidRunState,
                         ScenarioNotSupportedException,
                         ClientException,
                         OnnxConvertException,
                         NotFoundException)
from .utilities import friendly_http_exception

# Task: 287629 Remove when Mix-in available
STATUS = 'status'

RUNNING_STATES = [RunStatus.STARTING, RunStatus.PREPARING, RunStatus.RUNNING,
                  RunStatus.PROVISIONING, RunStatus.QUEUED]
POST_PROCESSING_STATES = [RunStatus.FINALIZING, RunStatus.CANCEL_REQUESTED]

CONTINUE_EXPERIMENT_KEY = 'continue'
CONTINUE_EXPERIMENT_SET = 'Set'
CONTINUE_EXPERIMENT_STATUS_KEY = '_aml_system_automl_status'


class AutoMLRun(Run):
    """
    AutoMLRun has information of the experiment runs that correspond to the AutoML run.

    This class can be used to manage, check status, and retrieve run details
    once a AutoML run is submitted.

    :param experiment: The experiment associated to the run.
    :type experiement: azureml.core.Experiment
    :param run_id: The id associated to the run.
    :type run_id: str
    """

    local_model_path = "model.pkl"
    local_onnx_model_path = "model.onnx"

    def __init__(self, experiment, run_id, **kwargs):
        """
        Initialize an AutoML run.

        :param experiment: The experiment associated to the run.
        :type experiement: azureml.core.Experiment
        :param run_id: The id associated to the run.
        :type run_id: str
        """
        host = kwargs.pop('host', None)
        try:
            user_agent = kwargs.pop('_user_agent', AUTOML_RUN_USER_AGENT)
            self._jasmine_client = JasmineClient(experiment.workspace.service_context,
                                                 experiment.name,
                                                 host=host)
            super(AutoMLRun, self).__init__(experiment=experiment, run_id=run_id,
                                            _user_agent=user_agent,
                                            **kwargs)
        except (AzureMLServiceException, HttpOperationError) as e:
            self._log_traceback(e)
            friendly_http_exception(e, _constants_azureml.API.InstantiateRun)

        self.model_id = None

    @property
    def run_id(self):
        """
        Return run id of the current run.

        :return: run id of the current run.
        :rtype: str
        """
        return self._run_id

    def cancel(self):
        """
        Cancel an AutoML run.

        Return True if the AutoML run is canceled successfully.

        :return: None
        """
        compute_target = json.loads(self.get_properties().get(Properties.AML_SETTINGS)).get('compute_target')
        spark_context = json.loads(self.get_properties().get(Properties.AML_SETTINGS)).get('spark_service')
        if spark_context != 'adb' and compute_target == constants.ComputeTargets.LOCAL:
            raise ScenarioNotSupportedException("Cancel operation is not supported for local runs. Local runs may be "
                                                "canceled by raising a keyboard interrupt.")

        if self._get_status() in RUNNING_STATES:
            try:
                self._jasmine_client.cancel_child_run(self._run_id)
            except (AzureMLServiceException, HttpOperationError) as e:
                self._log_traceback(e)
                friendly_http_exception(e, _constants_azureml.API.CancelChildRun)
            except Exception as e:
                self._log_traceback(e)
                raise ClientException("Failed when communicating with "
                                      "Jasmine service to cancel parent run.") from None
        else:
            raise ConfigException(
                "The AutoML run {} is already in {} state. "
                "This Run cannot be cancelled once in termination state.".
                format(self.run_id, self.get_status()))

    def cancel_iteration(self, iteration):
        """
        Cancel a particular child run.

        :param iteration: Which iteration to cancel.
        :type iteration: int
        :return: None
        """
        try:
            childrun_id = self.run_id + "_" + str(iteration)
            child_run = self._client.run.get_runs_by_run_ids(run_ids=[childrun_id])
        except (AzureMLServiceException, HttpOperationError) as e:
            self._log_traceback(e)
            friendly_http_exception(e, _constants_azureml.API.CancelChildRun)
        if child_run is None or len(child_run) < 1:
            raise ConfigException(
                "The iteration {} of AutoML run {} trying to cancel does not exist.".
                format(iteration, self.run_id))
        if child_run[0].get_status() in RUNNING_STATES:
            try:
                self._jasmine_client.cancel_child_run(child_run.run_id)
            except (AzureMLServiceException, HttpOperationError) as e:
                self._log_traceback(e)
                friendly_http_exception(e, _constants_azureml.API.CancelChildRun)
            except Exception as e:
                self._log_traceback(e)
                raise ClientException("Failed when communicating with "
                                      "Jasmine service to cancel iteration: {0}.".format(iteration)) from None
        else:
            raise ConfigException(
                "The AutoML run {} is already in {} state. "
                "This iteration cannot be cancelled once in termination state.".
                format(childrun_id, child_run[0].get_status()))

    def continue_experiment(
            self,
            data_script=None,
            X=None,
            y=None,
            sample_weight=None,
            X_valid=None,
            y_valid=None,
            sample_weight_valid=None,
            data=None,
            label=None,
            columns=None,
            cv_splits_indices=None,
            spark_context=None,
            experiment_timeout_minutes=None,
            experiment_exit_score=None,
            iterations=None,
            show_output=False,
            training_data=None,
            validation_data=None):
        """
        Continue an existing AutoML Experiment.

        :param data_script: File path to the script containing get_data().
        :type data_script: str
        :param X: Training features.
        :type X: pandas.DataFrame or numpy.ndarray or azureml.dataprep.Dataflow
        :param y: Training labels.
        :type y: pandas.DataFrame or numpy.ndarray or azureml.dataprep.Dataflow
        :param sample_weight: Sample weights for training data.
        :type sample_weight: pandas.DataFrame pr numpy.ndarray or azureml.dataprep.Dataflow
        :param X_valid: validation features.
        :type X_valid: pandas.DataFrame or numpy.ndarray or azureml.dataprep.Dataflow
        :param y_valid: validation labels.
        :type y_valid: pandas.DataFrame or numpy.ndarray or azureml.dataprep.Dataflow
        :param sample_weight_valid: validation set sample weights.
        :type sample_weight_valid: pandas.DataFrame or numpy.ndarray or azureml.dataprep.Dataflow
        :param data: Training features and label.
        :type data: pandas.DataFrame
        :param label: Label column in data.
        :type label: str
        :param columns: whitelist of columns in data to use as features.
        :type columns: list(str)
        :param cv_splits_indices:
            Indices where to split training data for cross validation.
            Each row is a separate cross fold and within each crossfold, provide 2 arrays,
            the first with the indices for samples to use for training data and the second
            with the indices to use for validation data. i.e [[t1, v1], [t2, v2], ...]
            where t1 is the training indices for the first cross fold and v1 is the validation
            indices for the first cross fold.
        :type cv_splits_indices: numpy.ndarray
        :param spark_context: Spark context, only applicable when used inside azure databricks/spark environment.
        :type spark_context: SparkContext
        :param experiment_timeout_minutes: How many additional minutes to run for this experiment for.
        :type experiment_timeout_minutes: int
        :param experiment_exit_score: Terminates the experiment when this score is reached.
        :type experiment_exit_score: int
        :param iterations: How many additional iterations to run for this experiment.
        :type iterations: int
        :param show_output: Flag whether to print output to console.
        :type show_output: bool
        :param training_data: Input training data.
        :type training_data: Dataflow or pandas.DataFrame
        :param validation_data: Validation data.
        :type validation_data: Dataflow or pandas.DataFrame
        :return: AutoML parent run.
        :rtype: azureml.train.automl.run.AutoMLRun
        """
        if not isinstance(iterations, int) and iterations is not None:
            raise ConfigException("iterations expected to be 'int' or 'None'. received '{0}'".format(type(iterations)))
        if not isinstance(experiment_timeout_minutes, int) and experiment_timeout_minutes is not None:
            raise ConfigException("experiment_timeout_minutes expected to be 'int' or 'None'. received '{0}'"
                                  .format(type(experiment_timeout_minutes)))
        if not isinstance(experiment_exit_score, int) and not isinstance(experiment_exit_score, float) and \
                experiment_exit_score is not None:
            raise ConfigException("experiment_exit_score expected to be 'float' or 'None'. received '{0}'"
                                  .format(type(experiment_exit_score)))

        tags = self.get_tags()
        properties = self.get_properties()
        if 'AMLSettingsJsonString' not in properties:
            raise InvalidRunState(
                'Previous run failed before starting any iterations. Please submit a new experiment.')

        original_aml_settings = json.loads(properties['AMLSettingsJsonString'])

        updated_iterations = None
        if iterations is None:
            if 'iterations' in tags:
                iterations = int(tags['iterations'])
            else:
                iterations = int(original_aml_settings['iterations'])
            updated_iterations = iterations
        else:
            run_iters = len(list(self.get_children(_rehydrate_runs=False)))
            updated_iterations = iterations + run_iters

        # Let's reset some relevant properties so that they get re-initialized when the experiment continues.
        original_aml_settings['ensemble_iterations'] = None
        original_aml_settings['experiment_timeout_minutes'] = experiment_timeout_minutes
        original_aml_settings['experiment_exit_score'] = experiment_exit_score
        original_aml_settings['spark_context'] = spark_context
        original_aml_settings['data_script'] = data_script
        original_aml_settings['iterations'] = updated_iterations

        automl_settings = AzureAutoMLSettings(
            experiment=self.experiment,
            **original_aml_settings)

        if automl_settings.spark_service == 'adb' and spark_context is None:
            raise ConfigException(
                'Required parameter spark_context is missing.')

        if automl_settings.spark_service is None and spark_context:
            raise ConfigException(
                'Original training is not in Azure databricks, remove parameter spark_context.')

        # early stopping should always be turned off for continue run
        tags = {
            'iterations': str(automl_settings.iterations),
            'experiment_timeout_minutes': str(automl_settings.experiment_timeout_minutes),
            'experiment_exit_score': str(automl_settings.experiment_exit_score),
            'enable_early_stopping': str(False),
            'start_time_utc': datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S.%fZ")
        }
        # update tags
        self.set_tags(tags)

        if X is not None and y is not None:
            X, y, sample_weight, X_valid, y_valid, sample_weight_valid = convert_inputs(
                X, y, sample_weight,
                X_valid, y_valid, sample_weight_valid
            )
        else:
            training_data, validation_data = convert_inputs_dataset(
                training_data,
                validation_data
            )

        if automl_settings.metric_operation is None:
            automl_settings.metric_operation = minimize_or_maximize(
                automl_settings.primary_metric)
        automl = _azureautomlclient.AzureAutoMLClient(self.experiment, automl_settings)
        automl.parent_run_id = self._run_id
        automl.current_run = self
        automl.automl_settings.spark_context = spark_context
        if show_output:
            automl._console_logger = sys.stdout

        if (automl_settings.compute_target not in (None, constants.ComputeTargets.LOCAL)) or spark_context:
            try:
                timeout_sec = None
                if experiment_timeout_minutes:
                    timeout_sec = experiment_timeout_minutes * 60
                self._jasmine_client.continue_remote_run(
                    self.id,
                    automl_settings.iterations,
                    timeout_sec,
                    automl_settings.experiment_exit_score)

                if automl_settings.spark_context is not None:
                    automl._init_adb_driver_run(X=X,
                                                y=y,
                                                sample_weight=sample_weight,
                                                X_valid=X_valid,
                                                y_valid=y_valid,
                                                sample_weight_valid=sample_weight_valid,
                                                cv_splits_indices=cv_splits_indices,
                                                show_output=show_output,
                                                existing_run=True)
                    # ADB handles show output so return here
                    return self

                if show_output:
                    RemoteConsoleInterface._show_output(self,
                                                        automl._console_logger,
                                                        automl.logger,
                                                        automl_settings.primary_metric)
            except Exception as e:
                self._log_traceback(e)
                raise

            return self

        if 'best_score' in tags:
            best_score = tags['best_score']
        else:
            try:
                best_run, _ = self.get_output()
                best_score = best_run.get_metrics()[automl_settings.primary_metric]
            except Exception:
                best_score = constants.Defaults.DEFAULT_PIPELINE_SCORE

        automl._score_best = best_score
        automl._score_max = best_score
        automl._score_min = best_score

        return automl.fit(
            X=X,
            y=y,
            sample_weight=sample_weight,
            X_valid=X_valid,
            y_valid=y_valid,
            sample_weight_valid=sample_weight_valid,
            cv_splits_indices=cv_splits_indices,
            show_output=show_output,
            existing_run=True,
            training_data=training_data,
            validation_data=validation_data)

    def get_output(self,
                   iteration: Optional[int] = None,
                   metric: Optional[str] = None,
                   return_onnx_model: bool = False,
                   return_split_onnx_model: Optional[OnnxConverter._SplitOnnxModelName] = None,
                   **kwargs: Any
                   ) -> Tuple['AutoMLRun', Any]:
        """
        Return the run and corresponding best pipeline that has already been tested.

        If no input is provided get_output
        will return the best pipeline according to the primary metric. Alternatively,
        you can use either iteration or metric to retrieve a particular iteration or
        the best run per provided metric (respectively).

        If you'd like to inspect the preprocessor(s) and algorithm (estimator) used, you can do so through
        `Model.steps`, similar to `sklearn.pipeline.Pipeline.steps`.
        For instance, the code below shows how to retrieve the estimator.

        .. code-block:: python

            best_run, model = parent_run.get_output()
            estimator = model.steps[-1]

        :param iteration: The iteration number of the corresponding run and fitted model to return.
        :type iteration: int
        :param metric: The metric to use to when selecting the best run and fitted model to return.
        :type metric: str
        :param return_onnx_model: This method will return the converted ONNX model, if user indicated
                                  the enable_onnx_compatible_models config.
        :type metric: bool

        :return: The run, the corresponding fitted model.
        :rtype: azureml.core.run.Run, Model
        """
        if iteration is not None and metric is not None:
            raise ConfigException('Cannot spcify both metric and iteration to register.')

        properties = self.get_properties()

        automl_settings = AzureAutoMLSettings(
            experiment=self.experiment,
            **json.loads(properties['AMLSettingsJsonString']))

        if metric is None:
            metric = automl_settings.primary_metric

        if return_onnx_model and not automl_settings.enable_onnx_compatible_models:
            raise OnnxConvertException("Invalid parameter 'return_onnx_model' passed in.")
        if return_split_onnx_model is not None \
                and not automl_settings.enable_split_onnx_featurizer_estimator_models:
            raise OnnxConvertException("Invalid parameter 'return_split_onnx_model' passed in.")

        if return_onnx_model:
            # Note: if conversion of split models fails, the entire onnx conversion of an iteration will fail.
            # This means that if the conversion of an iteration succeeds, and user set split convert config to true,
            # all the 3 models will be successfully converted.
            if return_split_onnx_model is None:
                model_name = constants.MODEL_PATH_ONNX
            elif return_split_onnx_model == OnnxConverter._SplitOnnxModelName.FeaturizerOnnxModel:
                model_name = OnnxConvertConstants.FeaturizerOnnxModelPath
            elif return_split_onnx_model == OnnxConverter._SplitOnnxModelName.EstimatorOnnxModel:
                model_name = OnnxConvertConstants.EstimatorOnnxModelPath
            model_local = self.local_model_path
        else:
            model_name = constants.MODEL_PATH
            model_local = self.local_model_path

        if metric in constants.Metric.CLASSIFICATION_SET:
            objective = constants.MetricObjective.Classification[metric]
        elif metric in constants.Metric.REGRESSION_SET:
            objective = constants.MetricObjective.Regression[metric]
        else:
            raise ConfigException("Invalid metric.")

        child_runs_sorted_with_scores = []
        if iteration is not None:
            parent_tags = self.get_tags()
            if 'iterations' in parent_tags:
                total_runs = int(parent_tags['iterations'])
            else:
                total_runs = int(self.get_properties()['num_iterations'])

            if not isinstance(iteration, str) and iteration >= total_runs:
                raise NotFoundException("Invalid iteration. Run {0} has {1} iterations."
                                        .format(self.run_id, total_runs))

            try:
                curr_run = Run(experiment=self.experiment,
                               run_id=self.run_id + '_' + str(iteration))
                run_status = curr_run.get_status()
                if run_status != RunStatus.COMPLETED:
                    raise InvalidRunState(
                        "Run {0} is in {1} state.".format(iteration, run_status))
            except (AzureMLServiceException, HttpOperationError) as e:
                if 'ResourceNotFoundException' in e.message:
                    raise InvalidRunState(
                        "Run {0} has not started yet.".format(iteration))
                else:
                    raise
        else:
            children = self.get_children(_rehydrate_runs=False)
            metrics = self.get_metrics(recursive=True)
            curr_run = None
            best_score = None
            comp = _get_max_min_comparator(objective)
            for child in children:
                try:
                    if child._run_dto[STATUS] == RunStatus.COMPLETED:
                        candidate_score = metrics.get(child.id, {}).get(metric, np.nan)
                        if not np.isnan(candidate_score):
                            child_runs_sorted_with_scores.append((child, candidate_score))
                            if best_score is None:
                                best_score = candidate_score
                                curr_run = child
                            else:
                                new_score = comp(best_score, candidate_score)
                                if new_score != best_score:
                                    best_score = new_score
                                    curr_run = child
                except Exception:
                    continue

            if curr_run is None:
                raise NotFoundException("Could not find model with valid score for metric '{0}'".format(metric))

        if return_onnx_model and iteration is None:
            # If returning the ONNX best model,
            # we try to download the best score model, if it's not converted successfully,
            # use the 2nd best score model, and so on.
            err = None
            is_succeeded = False
            if objective == constants.OptimizerObjectives.MAXIMIZE:
                is_desc = True
            elif objective == constants.OptimizerObjectives.MINIMIZE:
                is_desc = False
            else:
                raise ValueError(
                    "Maximization or Minimization could not be determined "
                    "based on current metric.")
            # Sort the child run to score tuple list.
            child_runs_sorted_with_scores.sort(key=lambda obj: obj[1], reverse=is_desc)
            err = None
            for child_run, _ in child_runs_sorted_with_scores:
                try:
                    child_run.download_file(name=model_name, output_file_path=model_local)
                    # We got the successfully converted ONNX model.
                    curr_run = child_run
                    is_succeeded = True
                    break
                except Exception as ex:
                    err = ex
                    continue

            if not is_succeeded:
                assert err is not None
                # Raise the exception if none of the child runs have converted ONNX model.
                raise err.with_traceback(err.__traceback__)
        else:
            # Returning Python model, or returning the specific iteration ONNX model.
            curr_run.download_file(name=model_name, output_file_path=model_local)

        # get the iteration of the best pipeline to check its pacakge compatibility
        iteration = int((curr_run.id).split('_')[-1])
        run_deps = self.get_run_sdk_dependencies(iteration=iteration, check_versions=False)
        if _has_version_discrepancies(run_deps, just_automl=True):
            ver = run_deps['azureml-train-automl']
            logging.warn(
                "Please ensure the version of your local conda dependencies match "
                "the version on which your model was trained in order to properly retrieve your model.".format(ver)
            )

        # back-compat old models
        from automl.client.core.runtime import model_wrappers
        sys.modules['azureml.train.automl.model_wrappers'] = model_wrappers

        if return_onnx_model:
            fitted_model = OnnxConverter.load_onnx_model(model_local)
        else:
            with open(model_local, "rb") as model_file:
                fitted_model = pickle.load(model_file)
        return curr_run, fitted_model

    def summary(self):
        """
        Get a table containing a summary of algorithms attempted and their scores.

        :return: Pandas DataFrame containing AutoML model statistics.
        :rtype: pandas.DataFrame
        """
        children = self.get_children(_rehydrate_runs=False)
        properties = self.get_properties()

        automl_settings = json.loads(properties['AMLSettingsJsonString'])
        primary_metric = properties['primary_metric']
        objective = automl_settings['metric_operation']

        algo_count = {}     # type: Dict[str, int]
        best_score = {}
        for child_run in children:
            metrics = child_run.get_metrics()
            properties = child_run.get_properties()
            score = constants.Defaults.DEFAULT_PIPELINE_SCORE
            if primary_metric in metrics:
                score = metrics[primary_metric]
            if 'run_algorithm' in properties:
                algo = properties['run_algorithm']
            else:
                algo = 'Failed'
            if algo not in algo_count:
                algo_count[algo] = 1
                best_score[algo] = score
            else:
                algo_count[algo] = algo_count[algo] + 1
                if objective == constants.OptimizerObjectives.MINIMIZE:
                    if score < best_score[algo] or np.isnan(best_score[algo]):
                        best_score[algo] = score
                else:
                    if score > best_score[algo] or np.isnan(best_score[algo]):
                        best_score[algo] = score

        algo_comp = pd.DataFrame(columns=['Algorithm', 'Count', 'Best Score'])
        for key in algo_count:
            algo_comp.loc[len(algo_comp)] = [
                key, algo_count[key], best_score[key]]
        return algo_comp

    def get_guardrails(self, to_console: bool = True) -> Dict[str, Any]:
        """Print and returns detailed results from running Guardrail verification."""
        ci = ConsoleInterface('verifier_results')
        verifier_results = {}           # type: Dict[str, Any]
        try:
            verifier_str = self._download_artifact_contents_to_string(
                os.path.join("outputs", "verifier_results.json"))
            verifier_results = json.loads(verifier_str)
            if len(verifier_results['faults']) == 0:
                ci.file_handler.write("Guardrail verification completed without any detected problems.")
            elif to_console:
                ci.print_guardrails(verifier_results['faults'], True)
        except UserErrorException:
            ci.file_handler.write("Current Run does not have Guardrail data.")
        finally:
            return verifier_results

    def register_model(self, model_name=None, description=None, tags=None, iteration=None, metric=None):
        """
        Register the model with AzureML ACI service.

        :param model_name: Name of the model being deployed.
        :type model_name: str
        :param description: Description for the model being deployed.
        :type description: str
        :param tags: Tags for the model being deployed.
        :type tags: dict
        :param iteration: Override for which model to deploy. Deploys the model for a given iteration.
        :type iteration: int
        :param metric: Override for which model to deploy. Deploys the best model for a different metric.
        :type metric: str
        :return: The registered model object.
        :rtype: Model
        """
        best_run, _ = self.get_output(iteration, metric)

        if model_name is not None and len(model_name) > 0:
            best_run.model_id = model_name
        else:
            best_run.model_id = self.run_id.replace('_', '').replace('-', '')[:15]
            if iteration is not None:
                best_run.model_id += str(iteration)
            elif metric is not None:
                best_run.model_id += metric
            else:
                best_run.model_id += 'best'
            best_run.model_id = best_run.model_id.replace('_', '')[:29]
        self.model_id = best_run.model_id
        return best_run.register_model(model_path=constants.MODEL_PATH,
                                       model_name=self.model_id,
                                       tags=tags,
                                       description=description)

    def clean_preprocessor_cache(self):
        """Clean the transformed, preprocessed data cache."""
        try:
            properties = self.get_properties()
            cache_path = None

            if 'AMLSettingsJsonString' not in properties:
                compute_target = constants.ComputeTargets.LOCAL
            else:
                automl_settings = AzureAutoMLSettings(
                    experiment=self.experiment,
                    **json.loads(properties['AMLSettingsJsonString']))
                compute_target = automl_settings.compute_target

            # TODO: Can we have a cleaner way of doing this?
            cache_store = CacheStoreFactory.get_cache_store(
                enable_cache=True,
                run_target=compute_target,
                run_id=self.run_id,
                data_store=self.experiment.workspace.get_default_datastore(),
                temp_location=cache_path)
            transformed_data_context = TransformedDataContext(
                X={},
                cache_store=cache_store)
            transformed_data_context.cleanup()
        except Exception:
            pass

    def retry(self):
        """Return True if the AutoML run is retried successfully."""
        raise NotImplementedError

    def pause(self):
        """Return True if the AutoML run is paused successfully."""
        raise NotImplementedError

    def resume(self):
        """Return True if the AutoML run is resumed successfully."""
        raise NotImplementedError

    def _log_traceback(self, exception: BaseException, settings: Optional[AzureAutoMLSettings] = None) -> None:
        if settings:
            set_diagnostics_collection(
                send_diagnostics=settings.send_telemetry,
                verbosity=settings.telemetry_verbosity
            )
        log_file_name = settings.debug_log if settings else None
        verbosity = settings.verbosity if settings else logging.DEBUG
        logger = _logging.get_logger(log_file_name, verbosity)
        logging_utilities.log_traceback(exception, logger)

    def get_run_sdk_dependencies(
        self,
        iteration=None,
        check_versions=True,
        **kwargs
    ):
        """
        Get the SDK run dependencies for a given run.

        :param iteration:
            The iteration number of the fitted run that going to be retrieved. If None, retrieve the
            parent environment.
        :type iteration: int
        :param check_versions: If True, check the versions with current env. If False, pass.
        :type check_versions: bool
        :return: The dict of dependencies from those retrieved from RunHistory.
        :rtype: dict
        """
        properties = self.get_properties()
        if iteration is not None:
            if iteration < 0:
                raise ConfigException(
                    'Iteration number must be greater than or equal to 0.')
        try:
            if iteration is not None:
                curr_run = AutoMLRun(experiment=self.experiment,
                                     run_id=self.run_id + '_' + str(iteration))
                properties = curr_run.get_properties()
            dependencies_versions = json.loads(
                properties['dependencies_versions'])
            logging.info('All the dependencies and the corresponding versions in the environment are:')
            logging.info(
                ';'.join(
                    [
                        '{}=={}'.format(d, dependencies_versions[d]) for d in sorted(dependencies_versions.keys())
                    ]
                )
            )
        except Exception:
            logging.warning(
                'No dependencies information found in the RunHistory.')
            return dict()

        sdk_dependencies = get_sdk_dependencies(
            all_dependencies_versions=dependencies_versions,
            logger=logging.getLogger(),
            **kwargs
        )
        if check_versions:
            _has_version_discrepancies(sdk_dependencies)

        return sdk_dependencies

    # Task: 287629 Remove when Mix-in available
    def wait_for_completion(self, show_output=False, wait_post_processing=False):
        """
        Wait for the completion of this run.

        Returns the status object after the wait.

        :param show_output: show_output=True shows the run output on sys.stdout.
        :type show_output: bool
        :param wait_post_processing:
            wait_post_processing=True waits for the post processing to
            complete after the run completes.
        :type wait_post_processing: bool
        :return: The status object.
        :rtype: dict
        """
        if show_output:
            try:
                self._stream_run_output(file_handle=sys.stdout)
            except KeyboardInterrupt:
                error_message = "The output streaming for the run interrupted.\n" \
                                "But the run is still executing on the compute target."

                raise ExperimentExecutionException(error_message)
        else:
            running_states = RUNNING_STATES
            if wait_post_processing:
                running_states.extend(POST_PROCESSING_STATES)

            current_status = None
            while current_status is None or current_status in running_states:
                current_status = self.get_tags().get('_aml_system_automl_status', None)
                if current_status is None:
                    current_status = self.get_status()
                time.sleep(3)

        return self.get_details()

    def _get_problem_info_dict(self):
        props = self.get_properties()
        problem_info_str = props[_constants_azureml.Properties.PROBLEM_INFO]
        return json.loads(problem_info_str)

    def _stream_run_output(self, file_handle=sys.stdout):
        """
        Stream the experiment run output to the specified file handle.

        By default the the file handle points to stdout.

        :param file_handle: A file handle to stream the output to.
        :type file_handle: file
        :return:
        """
        properties = self.get_properties()
        primary_metric = properties['primary_metric']
        remote_printer = RemoteConsoleInterface(file_handle, None)
        remote_printer.print_scores(
            self,
            primary_metric)

        file_handle.write("\n")
        file_handle.write("Execution Summary\n")
        file_handle.write("=================\n")
        file_handle.write("RunId: {}\n".format(self.id))
        file_handle.write("\n")
        file_handle.flush()

    def _get_status(self):
        """Combine the continue experiment status with the status pull from RunHistory."""
        tags = self.get_tags()
        # continue run cases
        if CONTINUE_EXPERIMENT_KEY in tags and CONTINUE_EXPERIMENT_STATUS_KEY in tags:
            if tags[CONTINUE_EXPERIMENT_KEY] == CONTINUE_EXPERIMENT_SET:
                return tags[CONTINUE_EXPERIMENT_STATUS_KEY]
        else:
            return self.get_status()
