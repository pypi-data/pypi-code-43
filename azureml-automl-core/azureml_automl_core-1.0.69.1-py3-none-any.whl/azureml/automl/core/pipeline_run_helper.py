# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Helper methods to execute an AutoML pipeline fit."""
import copy
import json
import logging
import os
from typing import cast, Any, Dict, List, Optional, Tuple

import sklearn.pipeline
from sklearn.pipeline import Pipeline as SKPipeline

from automl.client.core.common import constants
from automl.client.core.common import logging_utilities as logging_utilities
from automl.client.core.common import utilities
from automl.client.core.common.activity_logger import ActivityLogger
from automl.client.core.common.exceptions import ClientException
from automl.client.core.runtime import metrics
from automl.client.core.runtime import pipeline_spec as pipeline_spec_module
from automl.client.core.runtime.datasets import DatasetBase
from automl.client.core.runtime.execution_context import ExecutionContext
from automl.client.core.runtime.model_wrappers import \
    RegressionPipeline, PipelineWithYTransformations, ForecastingPipelineWrapper
from automl.client.core.runtime.resource_limits import DEFAULT_RESOURCE_LIMITS, SafeEnforceLimits
from automl.client.core.runtime.runner import ClientRunner
from .automl_base_settings import AutoMLBaseSettings
from .automl_pipeline import AutoMLPipeline
from .automl_run_context import AutoMLAbstractRunContext
from .featurization.streaming import StreamingFeaturizationTransformer
from .streaming_pipeline_wrapper import StreamingPipelineWrapper

SOURCE_WRAPPER_MODULE = 'automl.client.core.runtime.model_wrappers'


class PipelineRunOutput:
    """Data class used to encapsulate return values from calling run_pipeline."""

    def __init__(self, automl_settings: AutoMLBaseSettings, pipeline_obj: SKPipeline, training_type: str):
        """
        Initialize a PipelineRunOutput object.

        :param automl_settings: the settings object used for pipeline execution
        :param pipeline_obj: the pipeline being executed
        :param training_type: the training type
        """
        self._training_type = training_type
        self._run_template = 'automl_child'
        self._run_preprocessor, self._run_algorithm = self._get_preprocessor_and_algorithm(automl_settings,
                                                                                           pipeline_obj)
        self._fit_time = 0.0
        self._scores = constants.Defaults.INVALID_PIPELINE_VALIDATION_SCORES
        self._fitted_pipeline = constants.Defaults.INVALID_PIPELINE_OBJECT  # type: Optional[SKPipeline]
        self._fitted_pipelines_train = constants.Defaults.INVALID_PIPELINE_OBJECT  # type: Optional[List[SKPipeline]]

    def record_pipeline_output(self,
                               scores: Dict[str, Any],
                               fit_time: float,
                               fitted_pipeline: SKPipeline,
                               fitted_pipelines_train: Optional[List[SKPipeline]]) -> None:
        """
        Save output from a successful pipeline execution.

        :param scores: a dictionary containing metric scores
        :param fit_time: the time taken to execute the pipeline, in seconds
        :param fitted_pipeline: the fitted model
        :param fitted_pipelines_train: the partially trained pipelines when using cross validation
        :return:
        """
        self._scores = scores
        self._fit_time = fit_time
        self._fitted_pipeline = fitted_pipeline
        self._fitted_pipelines_train = fitted_pipelines_train

    @property
    def fit_time(self) -> float:
        """
        Get the fit time.

        TODO: when Jasmine PR #181653 goes in, this will only describe the fit time, not fit + predict time.
        """
        return self._fit_time

    @property
    def scores(self) -> Dict[str, Any]:
        """Get the scores."""
        return self._scores

    @property
    def fitted_pipeline(self) -> Optional[SKPipeline]:
        """Get the fitted model."""
        return self._fitted_pipeline

    @property
    def fitted_pipelines_train(self) -> Optional[List[SKPipeline]]:
        """Get the partially trained fitted models."""
        return self._fitted_pipelines_train

    @property
    def run_properties(self) -> Optional[str]:
        """Get the pipeline run properties."""
        if self.fitted_pipeline is None:
            return None
        try:
            pipeline_step_str = str(self.fitted_pipeline.steps[1][1])
            return pipeline_step_str[pipeline_step_str.find("(") + 1:
                                     pipeline_step_str.find(")")]
        except IndexError:
            return None

    @property
    def training_type(self) -> str:
        """Get the training type."""
        return self._training_type

    @property
    def pretrain_props(self) -> Dict[str, Optional[str]]:
        """Get the pretrain properties."""
        return {
            'run_template': self._run_template,
            'run_preprocessor': self._run_preprocessor,
            'run_algorithm': self._run_algorithm
        }

    @property
    def pretrain_props_sanitized(self) -> Dict[str, str]:
        """Get the pretrain properties with None converted to empty string."""
        return utilities.convert_dict_values_to_str(self.pretrain_props)

    @classmethod
    def _get_preprocessor_and_algorithm(cls,
                                        automl_settings: AutoMLBaseSettings,
                                        pipeline_obj: SKPipeline) -> Tuple[Optional[str], Optional[str]]:
        """
        Given a sklearn pipeline, retrieve the preprocessor and algorithm names.

        :param pipeline_obj: sklearn.pipeline.Pipeline
        :return: a tuple of preprocessor and algorithm names
        """
        try:
            preprocessor = None
            # for the Ensemble pipelines we will not have any preprocessors
            if len(pipeline_obj.steps) == 1:
                algorithm = pipeline_obj.steps[0][0]
            else:
                if not automl_settings.enable_streaming:
                    preprocessor = pipeline_obj.steps[0][0]
                algorithm = pipeline_obj.steps[1][0]
            return preprocessor, cls._map_algorithm_name(automl_settings.task_type, algorithm)
        except Exception:
            return None, None

    @staticmethod
    def _map_algorithm_name(task_type: str, run_algorithm: str) -> str:
        if task_type == constants.Tasks.CLASSIFICATION:
            return constants.ModelNameMappings.ClassNameToCustomerFacingModelMapClassification.get(run_algorithm,
                                                                                                   run_algorithm)
        elif task_type == constants.Tasks.REGRESSION:
            return constants.ModelNameMappings.ClassNameToCustomerFacingModelMapRegression.get(run_algorithm,
                                                                                               run_algorithm)
        else:
            raise ValueError('Invalid task type provided.')


def run_pipeline(automl_settings: AutoMLBaseSettings,
                 automl_pipeline: AutoMLPipeline,
                 automl_run_context: AutoMLAbstractRunContext,
                 iteration_timeout_min: Optional[int],
                 dataset: DatasetBase,
                 logger: logging.Logger,
                 remote: bool) -> PipelineRunOutput:
    """
    Run a pipeline using the given settings and context.

    :param automl_settings: settings object to use for this job.
    :param automl_pipeline: the pipeline definition to use for this job.
    :param automl_run_context: the run context to use for this job.
    :param iteration_timeout_min: upper bound for how long this job can take. Passing None disables timeout.
    :param dataset: the data to use for this job.
    :param logger: the logger to use for this job.
    :param remote: whether we are running remotely or not.
    :return: a PipelineRunOutput object containing the results
    """
    with logging_utilities.log_activity(logger, activity_name=constants.TelemetryConstants.RUN_PIPELINE_NAME,
                                        custom_dimensions={'run_id': automl_run_context.run_id}):

        execution_context = ExecutionContext(run_id=automl_run_context.run_id)

        task = automl_settings.task_type
        if automl_settings.is_timeseries:
            task = constants.Subtasks.FORECASTING
        metrics_to_calculate = metrics.get_default_metrics(task)

        # for CV, we'll save the partially trained models on each split,
        # along with the model trained on full set

        pipeline_spec, training_type, problem_info = \
            _get_training_args(dataset=dataset,
                               pipeline_script=automl_pipeline.pipeline_script,
                               max_cores_per_iteration=automl_settings.max_cores_per_iteration,
                               logger=logger)

        if automl_settings.is_timeseries:
            problem_info.timeseries_param_dict = utilities._get_ts_params_dict(automl_settings)

        problem_info.gpu_training_param_dict = utilities._get_gpu_training_params_dict(automl_settings)
        pipeline_obj = pipeline_spec.instantiate_pipeline_spec(
            problem_info,
            preprocess_pipeline=dataset.get_preprocessor_pipeline_step(),
            dataset_metadata=dataset.dataset_metadata)
        pipeline_run_output = PipelineRunOutput(automl_settings, pipeline_obj, training_type)

        with automl_run_context.get_run() as run:
            run.add_properties(pipeline_run_output.pretrain_props_sanitized)

        # min to sec conversion
        timeout = None
        if iteration_timeout_min is not None:
            timeout = iteration_timeout_min * 60
            logger.debug("Remaining time for iteration: {} s.".format(timeout))

        log_config = logging_utilities.LogConfig(
            automl_settings.debug_log, automl_settings.verbosity,
            'automl-client-core-common')
        if isinstance(logger, ActivityLogger):
            logger.set_custom_dimensions_on_log_config(log_config)

        runtime_constraints = DEFAULT_RESOURCE_LIMITS.copy()
        runtime_constraints['mem_in_mb'] = automl_settings.mem_in_mb
        runtime_constraints['wall_time_in_s'] = timeout
        problem_info.runtime_constraints = runtime_constraints

        runner = ClientRunner(dataset, metrics=metrics_to_calculate,
                              task=automl_settings.task_type,
                              log_config=log_config,
                              execution_context=execution_context)

        results, status = runner.run(dataset,
                                     pipeline_spec,
                                     problem_info,
                                     sets_to_run=[training_type],
                                     is_ensemble_iteration=automl_pipeline.is_ensemble_pipeline,
                                     subsample_percent=automl_pipeline.training_percent,
                                     subsample_seed=automl_settings.subsample_seed,
                                     enforce_limits=True,
                                     include_models=True)

        if isinstance(status, BaseException):
            raise status.with_traceback(status.__traceback__)
        if results is None:
            raise ClientException("Failed to train pipeline. Status: {}".format(status))

        fitted_pipelines_train = constants.Defaults.INVALID_PIPELINE_OBJECT

        # for cross validation train the model on full data set.
        if not automl_pipeline.is_ensemble_pipeline:
            results = _map_results(results, training_type)
            if results is not None and len(results) > 2:
                if training_type in \
                        [constants.TrainingType.CrossValidation, constants.TrainingType.MeanCrossValidation]:
                    result_full, status = runner.run(
                        dataset, pipeline_spec, problem_info, sets_to_run=[
                            constants.TrainingType.TrainFull],
                        include_models=True)
                    if isinstance(status, BaseException):
                        raise status.with_traceback(status.__traceback__)
                    if result_full is None:
                        raise ClientException("Failed while training full result. Status: {}".format(status))
                    if len(result_full) <= 2:
                        raise ClientException("Expected to get at least 3 values from training full result but only "
                                              "got {}.".format(len(result_full)))

                    result_full = _map_results(result_full, constants.TrainingType.TrainFull)

                    fitted_pipelines_train = results[2]
                    # put fully fitted model in results
                    results = (results[0], results[1], result_full[2])

        score_valid, fit_time, fitted_pipeline = results
        if isinstance(fitted_pipeline, list) and len(fitted_pipeline):
            fitted_pipeline = fitted_pipeline[0]

        if automl_settings.enable_streaming:
            fitted_pipeline = StreamingPipelineWrapper(
                cast(StreamingFeaturizationTransformer, dataset.get_preprocessor()),
                fitted_pipeline)

        if automl_settings.task_type == constants.Tasks.REGRESSION and not automl_settings.is_timeseries and\
                not automl_settings.enable_streaming:
            # add stddev to regression pipelines for error bars on predictions
            stddev = score_valid[constants.Metric.Residuals]['data'].get(metrics.ResidualsMetric.STDDEV)
            fitted_pipeline = RegressionPipeline(fitted_pipeline, stddev)

        augmented_pipeline, augmented_pipelines_train = _augment_transformers(dataset,
                                                                              fitted_pipeline,
                                                                              fitted_pipelines_train)
        # Forecasting pipeline require all transformers to be on their place
        # that is why we are creating it on the augmented pipeline.
        if automl_settings.is_timeseries:
            stddevs = []
            # add stddev to regression pipelines for error bars on predictions
            for horizon in score_valid[constants.Metric.ForecastResiduals]['data'].keys():
                stddevs.append(score_valid[constants.Metric.ForecastResiduals]
                               ['data'][horizon][metrics.ForecastResidualsMetric.STDDEV])
            augmented_pipeline = ForecastingPipelineWrapper(augmented_pipeline, stddev=stddevs)

        pipeline_run_output.record_pipeline_output(score_valid,
                                                   fit_time,
                                                   augmented_pipeline,
                                                   augmented_pipelines_train)
        return pipeline_run_output


def _get_pipeline(pipeline_script, problem_info, logger=None):
    """
    Get the Pipeline object.

    :param pipeline_script: returned from service that is a dictionary of pipeline
    : spec
    : or for backward compatibility a dictionary of normal and sparse pipeline
    : definition that can be eval'd
    :param problem_info: The metadata on the dataset.
    :return: a tuple of ProblemInfo object and a PipelineSpec object.
    """
    pipeline_dict = json.loads(pipeline_script)

    # Wrap the standard scaler.
    scaler = [o for o in pipeline_dict["objects"]
              if o['spec_class'] == pipeline_spec_module.PREPROC_NAME and o['class_name'] == 'StandardScaler']
    if len(scaler) == 1:
        scaler[0]['class_name'] = 'StandardScalerWrapper'
        scaler[0]['module'] = SOURCE_WRAPPER_MODULE

    # rename the Ensemble class name to VotingEnsemble to distinguish from other Ensemble implementations
    voting_ensemble = [o for o in pipeline_dict["objects"]
                       if o['spec_class'] == pipeline_spec_module.SKLEARN_NAME and o['class_name'] == 'Ensemble']
    if len(voting_ensemble) == 1:
        voting_ensemble[0]['class_name'] = 'VotingEnsemble'

    # If there are any single threaded pipelines, force the number of threads to 1.
    pinfo = problem_info
    if problem_info.num_threads != 1:
        stmodel = [o for o in pipeline_dict["objects"]
                   if o['spec_class'] == pipeline_spec_module.SKLEARN_NAME and
                   any([(algo_name in o['class_name']) for algo_name in constants.SINGLE_THREADED_ALGORITHMS])]
        if len(stmodel) == 1:
            pinfo = copy.deepcopy(problem_info)
            pinfo.num_threads = 1
            if logger:
                logger.warning("resetting the number of threads to 1\
                               for pipeline with {0}".
                               format(stmodel[0]['class_name']))
    spec = pipeline_spec_module.PipelineSpec.from_dict(pipeline_dict)
    return pinfo, spec


def _get_training_args(dataset,
                       pipeline_script=None,
                       max_cores_per_iteration=None,
                       logger=None):

    problem_info = dataset.get_problem_info()
    problem_info.num_threads = max_cores_per_iteration
    pipeline_spec = None
    if pipeline_script:
        problem_info, pipeline_spec = _get_pipeline(pipeline_script, problem_info, logger)
    return pipeline_spec, dataset.get_training_type(), problem_info


def _map_results(results, training_type):
    training_types = constants.TrainingType
    result_types = constants.TrainingResultsType

    if training_type in [training_types.TrainAndValidation, training_types.TrainValidateTest]:
        status = results[result_types.TRAIN_VALIDATE_STATUS]
        if status:
            raise ClientException(status)
        scores = results[result_types.VALIDATION_METRICS]
        train_time = results[result_types.VALIDATION_METRICS][result_types.TRAIN_TIME]
        model = results[result_types.MODELS][training_type]
    elif training_type == training_types.TrainFull:
        status = results[result_types.TRAIN_FULL_STATUS]
        if status:
            raise ClientException(status)
        scores = results[result_types.TRAIN_FROM_FULL_METRICS]
        train_time = results[result_types.TRAIN_FROM_FULL_METRICS][result_types.TRAIN_TIME]
        model = results[result_types.MODELS][training_type]
    elif training_type == training_types.CrossValidation:
        status = results[result_types.CV_STATUS]
        if status:
            raise ClientException(status)
        scores = results[result_types.CV_METRICS]
        train_time = [x[result_types.TRAIN_TIME]
                      for x in results[result_types.CV_METRICS]]
        model = results[result_types.MODELS][training_type]
    elif training_type == training_types.MeanCrossValidation:
        status = results[result_types.CV_STATUS]
        if status:
            raise ClientException(status)
        scores = results[result_types.CV_MEAN_METRICS]
        train_time = results[result_types.CV_MEAN_METRICS][result_types.TRAIN_TIME]
        model = results[result_types.MODELS][training_types.CrossValidation]
    else:
        raise ClientException('Invalid training type {} specified.'.format(training_type))

    return scores, train_time, model


def _augment_transformers(dataset, fitted_pipeline, fitted_pipelines_train):
    transformers = dataset.get_transformers()
    x_transformer = transformers.get(constants.Transformers.X_TRANSFORMER)
    lag_transformer = transformers.get(constants.Transformers.LAG_TRANSFORMER)
    ts_transformer = transformers.get(constants.Transformers.TIMESERIES_TRANSFORMER)
    y_transformer = transformers.get(constants.Transformers.Y_TRANSFORMER)

    # Augment the pipeline with our own transformers
    if (x_transformer is not None or lag_transformer is not None or ts_transformer is not None) and \
            fitted_pipeline != constants.Defaults.INVALID_PIPELINE_OBJECT:
        fitted_pipeline = _add_transformer_x(
            x_transformer, lag_transformer, ts_transformer, fitted_pipeline)
        if fitted_pipelines_train != constants.Defaults.INVALID_PIPELINE_OBJECT:
            transformed_train_pipelines = []
            for pipe in fitted_pipelines_train:
                transformed_train_pipelines.append(
                    _add_transformer_x(x_transformer, lag_transformer, ts_transformer, pipe))
            fitted_pipelines_train = transformed_train_pipelines

    if y_transformer is not None:
        # if y_transformer is not None, add a wrapper of the fitted model with transformer.
        if isinstance(fitted_pipeline, sklearn.pipeline.Pipeline) and \
                fitted_pipeline != constants.Defaults.INVALID_PIPELINE_OBJECT:
            fitted_pipeline = PipelineWithYTransformations(
                fitted_pipeline, "LabelEncoder", y_transformer)
        if isinstance(fitted_pipelines_train, sklearn.pipeline.Pipeline) and \
                fitted_pipelines_train != constants.Defaults.INVALID_PIPELINE_OBJECT:
            fitted_pipeline = PipelineWithYTransformations(
                fitted_pipelines_train, "LabelEncoder", y_transformer)

    return fitted_pipeline, fitted_pipelines_train


def _add_transformer_x(transformer, lag_transformer, ts_transformer, pipeline_spec):
    """
    Add transformer as first step of the pipeline.

    :param pipeline_spec: pipeline to which the transformer should be added
    :param transformer: a pipeline compatible transformation that implements fit, transform and predict
    :return: pipeline with transformer prepended
    """
    insert_at = 0
    if transformer is not None:
        pipeline_spec.steps.insert(insert_at, (constants.Transformers.X_TRANSFORMER, transformer))
        insert_at += 1
    if lag_transformer is not None:
        pipeline_spec.steps.insert(insert_at, (constants.Transformers.LAG_TRANSFORMER, lag_transformer))
        insert_at += 1
    if ts_transformer is not None:
        pipeline_spec.steps.insert(insert_at, (constants.Transformers.TIMESERIES_TRANSFORMER, ts_transformer))
        insert_at += 1

    return pipeline_spec
