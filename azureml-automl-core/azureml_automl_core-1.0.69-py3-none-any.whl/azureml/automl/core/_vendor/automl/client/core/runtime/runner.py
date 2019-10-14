# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Class for running experiments."""
from typing import Any, Callable, cast, Dict, List, Optional, Set, Tuple, Union
import datetime
import traceback

import pandas as pd
import numpy as np
import scipy
import sklearn.pipeline

import azureml.dataprep as dprep

from automl.client.core.common import constants
from automl.client.core.common import logging_utilities as log_utils
from . import resource_limits
from automl.client.core.common.activity_logger import ActivityLogger, TelemetryActivityLogger, DummyActivityLogger
from automl.client.core.common.constants import (
    Tasks, TrainingResultsType, TrainingType, Sample_Weights_Unsupported)
from .datasets import DatasetBase
from .execution_context import ExecutionContext
from .nimbus_wrappers import NimbusMlPipelineWrapper
from .pipeline_spec import PipelineSpec
from .problem_info import ProblemInfo
from .resource_limits import SafeEnforceLimits
from .score import scoring, utilities as scoring_utilities, constants as scoring_constants


class ClientRunner:
    """Runner which encapsulates the fit() method for various AutoML models."""

    def __init__(self,
                 datasets: DatasetBase,
                 metrics: Optional[Set[str]] = None,
                 task: str = constants.Tasks.CLASSIFICATION,
                 log_config: Optional[log_utils.LogConfig] = None,
                 execution_context: Optional[ExecutionContext] = None):
        """
        Construct the ClientRunner.

        :param datasets: A DatasetBase object.
        :param metrics: The metric that AutoML will optimize for model selection.
        :param task: string, 'classification' or 'regression'
        :param log_config: LogConfig, log config for logger reconstruction
        :param execution_context: ExecutionContext, the execution context from parent context
        """
        assert task in ['classification', 'regression']
        self.task = task

        self.metrics = scoring_utilities.get_scalar_metrics(self.task) if metrics is None else list(metrics)

        self.datasets = datasets

        self._log_config = log_config
        self.execution_context = execution_context

    @property
    def activity_logger(self) -> ActivityLogger:
        """
        Lazily instantiate an activity logger.

        :return:
        """
        return self._get_activity_logger()

    def time_fit(self, m, X, y, sample_weight=None):
        """
        Run the fit and calculate the time elapsed.

        :param m: The model to run the fit.
        :param X: Input data.
        :param y: Target values.
        :param sample_weight: Sample weights for training data.
        :return: The time elapsed for fit.
        """
        with self.activity_logger.log_activity(logger=None,
                                               activity_name=constants.TelemetryConstants.TIME_FIT_NAME):
            t = datetime.datetime.utcnow()  # time.process_time()
            ClientRunner.fit_pipeline(m, X, y, sample_weight)
            elapsed_time = datetime.datetime.utcnow() - t

            return elapsed_time.total_seconds()

    def time_fit_input_dataset(self,
                               m: Any,
                               training_data: Union[dprep.Dataflow, pd.DataFrame],
                               label_column_name: str,
                               weight_column_name: str) -> Any:
        """
        Run the fit and calculate the time elapsed.

        :param m: The model to run the fit.
        :param training_data: Input data.
        :param label_column_name: Target column name.
        :param weight_column_name: Sample weight column name for training data.
        :return: The time elapsed for fit.
        """
        with self.activity_logger.log_activity(logger=None,
                                               activity_name=constants.TelemetryConstants.TIME_FIT_NAME):
            t = datetime.datetime.utcnow()  # time.process_time()
            ClientRunner.fit_pipeline_input_dataset(m, training_data)
            elapsed_time = datetime.datetime.utcnow() - t

            return elapsed_time.total_seconds()

    def _run_train_valid(self, dataset, pipeline_spec,
                         problem_info,
                         random_state=None):
        """
        Run the training and validation.

        :param dataset: The DatasetBase object used for the run.
        :param pipeline_spec: The PipelineSpec object used for the run.
        :return: A dictionary of metric name -> score, fit time and the instantiated pipeline.
        """
        with self.activity_logger.log_activity(logger=None,
                                               activity_name=constants.TelemetryConstants.RUN_TRAIN_VALID_NAME):
            X_train, y_train, sample_weight_train = dataset.get_train_set()
            X_valid, y_valid, sample_weight_valid = dataset.get_valid_set()

            pipeline = pipeline_spec.instantiate_pipeline_spec(
                problem_info,
                random_state=random_state,
                is_sparse=dataset.get_is_sparse(),
                preprocess_pipeline=dataset.get_preprocessor_pipeline_step(),
                dataset_metadata=dataset.dataset_metadata)

            if isinstance(pipeline, NimbusMlPipelineWrapper):
                fit_time = self.time_fit_input_dataset(pipeline,
                                                       dataset.training_data,
                                                       dataset.label_column_name,
                                                       dataset.weight_column_name)
            else:
                fit_time = self.time_fit(
                    pipeline, X_train, y_train, sample_weight=sample_weight_train)

            score_valid = self._compute_metrics(X_valid, y_valid, y_train,
                                                pipeline, dataset,
                                                sample_weight=sample_weight_valid,
                                                problem_info=problem_info)
            return score_valid, fit_time, pipeline

    def _run_train_full(self, dataset, pipeline_spec,
                        problem_info,
                        random_state=None):
        """
        Run the full training.

        :param dataset: The ClientDatasets object used for the run.
        :param pipeline_spec: The PipelineSpec object used for the run.
        :return: A dictionary of metric name -> score, fit time and the instantiated pipeline.
        """
        with self.activity_logger.log_activity(logger=None,
                                               activity_name=constants.TelemetryConstants.RUN_TRAIN_FULL_NAME):
            if dataset.has_training_set():
                X_train, y_train, sample_weight_train = dataset.get_train_set()
                X_valid, y_valid, sample_weight_valid = dataset.get_valid_set()
                X_full = (
                    scipy.sparse.vstack((X_train, X_valid))
                    if scipy.sparse.issparse(X_train)
                    else np.concatenate((X_train, X_valid)))
                y_full = np.concatenate((y_train, y_valid))

                if sample_weight_valid is not None:
                    sample_weight_full = np.concatenate(
                        (sample_weight_train, sample_weight_valid))
                else:
                    sample_weight_full = None
            else:
                X_full, y_full, sample_weight_full = dataset.get_full_set()

            pipeline = pipeline_spec.instantiate_pipeline_spec(
                problem_info,
                random_state=random_state,
                is_sparse=dataset.get_is_sparse(),
                preprocess_pipeline=dataset.get_preprocessor_pipeline_step())

            if isinstance(pipeline, NimbusMlPipelineWrapper):
                fit_time = self.time_fit_input_dataset(pipeline,
                                                       dataset.training_data,
                                                       dataset.label_column_name,
                                                       dataset.weight_column_name)
            else:
                fit_time = self.time_fit(
                    pipeline, X_full, y_full, sample_weight=sample_weight_full)

            # Note that y_full is passed here as both validation targets
            # and as training targets because the full set is used for
            # training and validation.
            score_full = self._compute_metrics(X_full, y_full, y_full,
                                               pipeline, dataset,
                                               sample_weight=sample_weight_full)

            return score_full, fit_time, pipeline, X_full, y_full

    def _run_cv(self, dataset, pipeline_spec, problem_info,
                random_state=None):
        """
        Run the fit of given pipeline spec with CV splits of the input dataset.

        :param dataset: The ClientDatasets object used for the run.
        :param pipeline_spec: The PipelineSpec object used for the run.
        :param problem_info: The ProblemInfo object used for the run.
        :param random_state: RandomState instance or None, optional, default = None.
        :return: Dictionaries of metric name -> score, fit times and the instantiated pipelines.
        """
        with self.activity_logger.log_activity(logger=None,
                                               activity_name=constants.TelemetryConstants.RUN_CV_NAME):
            scores = []
            fit_times = []
            models = []

            for X_train, y_train, sample_wt_train, X_test, y_test, sample_wt_test \
                    in dataset.get_CV_splits():
                m = pipeline_spec.instantiate_pipeline_spec(
                    problem_info, random_state=random_state, is_sparse=dataset.get_is_sparse())

                fit_time = self.time_fit(m, X_train, y_train, sample_wt_train)
                score = self._compute_metrics(X_test, y_test, y_train,
                                              m, dataset,
                                              sample_weight=sample_wt_test)

                scores.append(score)
                fit_times.append(fit_time)
                models.append(m)
            return scores, fit_times, models

    def _run_cv_mean(self, dataset, pipeline_spec, problem_info,
                     cv_results=None,
                     random_state=False):
        """
        Run the fit to get the mean of scores and fit time, with CV splits of the input dataset.

        :param dataset: The ClientDatasets object used for the run.
        :param pipeline_spec: The PipelineSpec object used for the run.
        :param problem_info: The ProblemInfo object used for the run.
        :param cv_results: The result of a _run_cv method.
        :param random_state: RandomState instance or None, optional, default = None.
        :return: Mean values of the scores and fit times, and the instantiated pipelines.
        """
        with self.activity_logger.log_activity(logger=None,
                                               activity_name=constants.TelemetryConstants.RUN_CV_MEAN_NAME):
            if cv_results is None:
                scores, fit_times, fit_models = self._run_cv(
                    dataset, pipeline_spec, problem_info,
                    random_state=random_state)
            else:
                scores, fit_times, fit_models = cv_results

            mean_scores = scoring.aggregate_scores(scores, self.metrics, logger=self.activity_logger)
            mean_fit_time = float(np.mean(fit_times))
            return mean_scores, mean_fit_time, fit_models

    def _run(self, dataset, pipeline_spec, problem_info, sets_to_run,
             subsample_percent=None, random_state=None, include_models=False,
             subsample_seed=0):
        """
        Run the fit with different purpose with specific run sets.

        :param dataset: A DatasetBase object with information about the dataset.
        :param pipeline_spec: A pipeline specification (obtained from the API).
        :param problem_info: A ProblemInfo object.
        :param sets_to_run: Which experiment types to run (e.g. CV,
            train_valid, etc).
        :param subsample_percent: A multiple of 5 between 5 and 100, inclusive.
        :param random_state: int or RandomState object to seed random
            operations.
        :param include_models:
        :return: train, validation, and test scores for the experiments
            specified in sets_to_run.
        """
        with self.activity_logger.log_activity(logger=None,
                                               activity_name=constants.TelemetryConstants.RUN_NAME):
            with dataset.open_dataset():
                results = {TrainingResultsType.MODELS: {}}  # type: Dict[str, Any]
                training_percent = subsample_percent or problem_info.training_percent
                if training_percent is not None and training_percent < 100:
                    # train on a subset of the training dataset.
                    results[TrainingResultsType.TRAIN_PERCENT] = training_percent
                    dataset = dataset.get_subsampled_dataset(
                        training_percent, random_state=subsample_seed)
                else:
                    results[TrainingResultsType.TRAIN_PERCENT] = 100

                if constants.TrainingType.TrainAndValidation in sets_to_run:
                    results[TrainingResultsType.TRAIN_VALIDATE_STATUS] = 0
                    try:
                        score_full, fit_time, fit_model = self._run_train_valid(
                            dataset, pipeline_spec, problem_info,
                            random_state=random_state)
                        results[TrainingResultsType.VALIDATION_METRICS] = score_full
                        results[TrainingResultsType.MODELS][
                            constants.TrainingType.TrainAndValidation] = fit_model
                        results[TrainingResultsType.VALIDATION_METRICS][
                            TrainingResultsType.FIT_TIME] = fit_time
                        results[TrainingResultsType.VALIDATION_METRICS][TrainingResultsType.TRAIN_TIME] = \
                            results[TrainingResultsType.VALIDATION_METRICS][TrainingResultsType.FIT_TIME] + \
                            results[TrainingResultsType.VALIDATION_METRICS][TrainingResultsType.PREDICT_TIME]
                    except ValueError:
                        results[TrainingResultsType.TRAIN_VALIDATE_STATUS] = \
                            traceback.format_exc()
                        results[TrainingResultsType.VALIDATION_METRICS] = None

                if constants.TrainingType.TrainValidateTest in sets_to_run:
                    results[TrainingResultsType.TRAIN_VALIDATE_STATUS] = 0

                    try:
                        score_full, fit_time, fit_model = self._run_train_valid(
                            dataset, pipeline_spec, problem_info,
                            random_state=random_state)
                        results[TrainingResultsType.VALIDATION_METRICS] = score_full
                        results[TrainingResultsType.MODELS][
                            constants.TrainingType.TrainValidateTest] = fit_model
                        X_train, y_train, sample_weight_train = dataset.get_train_set()
                        scores = self._compute_metrics(X_train, y_train, y_train,
                                                       fit_model, dataset,
                                                       sample_weight=sample_weight_train)
                        results[TrainingResultsType.TRAIN_METRICS] = scores
                        results[TrainingResultsType.TRAIN_METRICS][
                            TrainingResultsType.FIT_TIME] = fit_time
                        results[TrainingResultsType.TRAIN_METRICS][TrainingResultsType.TRAIN_TIME] = \
                            results[TrainingResultsType.TRAIN_METRICS][TrainingResultsType.FIT_TIME] + \
                            results[TrainingResultsType.TRAIN_METRICS][TrainingResultsType.PREDICT_TIME]
                        X_test, y_test, sample_weight_test = dataset.get_test_set()
                        scores = self._compute_metrics(X_test, y_test, y_train,
                                                       fit_model, dataset,
                                                       sample_weight=sample_weight_test)
                        results[TrainingResultsType.TEST_METRICS] = scores
                    except ValueError:
                        results[TrainingResultsType.TRAIN_VALIDATE_STATUS] = \
                            traceback.format_exc()
                        results[TrainingResultsType.VALIDATION_METRICS] = None
                        results[TrainingResultsType.TRAIN_METRICS] = None
                        results[TrainingResultsType.TEST_METRICS] = None

                if constants.TrainingType.TrainFull in sets_to_run:
                    results[TrainingResultsType.TRAIN_FULL_STATUS] = 0
                    try:
                        score_full, fit_time, fit_model, _, y_full = self._run_train_full(
                            dataset, pipeline_spec, problem_info,
                            random_state=random_state)

                        results[TrainingResultsType.MODELS][
                            constants.TrainingType.TrainFull] = fit_model
                        results[TrainingResultsType.TRAIN_FROM_FULL_METRICS] = score_full
                        results[TrainingResultsType.TRAIN_FROM_FULL_METRICS][
                            TrainingResultsType.FIT_TIME] = fit_time
                        results[TrainingResultsType.TRAIN_FROM_FULL_METRICS][TrainingResultsType.TRAIN_TIME] = \
                            results[TrainingResultsType.TRAIN_FROM_FULL_METRICS][TrainingResultsType.FIT_TIME] + \
                            results[TrainingResultsType.TRAIN_FROM_FULL_METRICS][TrainingResultsType.PREDICT_TIME]

                        if dataset.has_test_set():
                            X_test, y_test, sample_weight_test = dataset.get_test_set()
                            scores = self._compute_metrics(X_test, y_test, y_full,
                                                           fit_model, dataset,
                                                           sample_weight=sample_weight_test)
                            results[TrainingResultsType.TEST_FROM_FULL_METRICS] = scores
                    except ValueError:
                        results[TrainingResultsType.TRAIN_FULL_STATUS] = \
                            traceback.format_exc()
                        results[TrainingResultsType.TRAIN_FROM_FULL_METRICS] = None
                        results[TrainingResultsType.TEST_FROM_FULL_METRICS] = None

                if (constants.TrainingType.CrossValidation in sets_to_run or
                        constants.TrainingType.MeanCrossValidation in sets_to_run):
                    results[TrainingResultsType.CV_STATUS] = 0
                    try:
                        scores, fit_times, fit_model = self._run_cv(
                            dataset, pipeline_spec, problem_info,
                            random_state=random_state)
                        results[TrainingResultsType.MODELS][
                            constants.TrainingType.CrossValidation] = fit_model
                        for i in range(len(scores)):
                            score = scores[i]
                            fit_time = fit_times[i]
                            score[TrainingResultsType.FIT_TIME] = fit_time
                            score[TrainingResultsType.TRAIN_TIME] = score[TrainingResultsType.FIT_TIME] + score[
                                TrainingResultsType.PREDICT_TIME]
                        results[TrainingResultsType.CV_METRICS] = scores

                        mean_scores, mean_time, fit_model = self._run_cv_mean(
                            dataset, pipeline_spec, problem_info,
                            cv_results=(scores, fit_times, fit_model))

                        results[TrainingResultsType.CV_MEAN_METRICS] = mean_scores
                    except ValueError:
                        results[TrainingResultsType.CV_STATUS] = \
                            traceback.format_exc()
                        results[TrainingResultsType.CV_MEAN_METRICS] = None
                        results[TrainingResultsType.CV_METRICS] = None

                if not include_models:
                    del results[TrainingResultsType.MODELS]

                return results

    def _compute_metrics(self, X_valid, y_valid, y_train,
                         model, dataset, sample_weight=None, problem_info=None):
        """Compute the metrics.

        Wrapper for compute_metrics_classification and compute_metrics_regression
        Branches are based on the task and get the appropriate parameters needed
        to compute metrics from the dataset.
        :param X_valid: The inputs to test/compute metrics.
        :param y_valid: The targets to test/compute metrics.
        :param y_train: The targets to train the model.
        :param model: The model to make predictions.
        :param dataset: ClientDataset object that contains information
            about the dataset (see datasets.py).
        :param sample_weight: The weights for each sample to use when computing the
            score for each metric.
        :param problem_info: The ProblemInfo object used for the run.
        :return: A dictionary of metric name -> score.
        """
        with self.activity_logger.log_activity(logger=None,
                                               activity_name=constants.TelemetryConstants.COMPUTE_METRICS_NAME):
            start = datetime.datetime.utcnow()
            y_pred = self._predict(self.task, model, X_valid)
            # computing metrics time should be neglible so this is the time we want
            predict_time = datetime.datetime.utcnow() - start

            # if y_valid is a Dataflow, convert it to a numpy array
            # (we are assuming that y_valid is small enough to fit into memory)
            if isinstance(y_valid, dprep.Dataflow):
                y_valid = y_valid.to_pandas_dataframe().iloc[:, 0].values

            # if sample_weight is a Dataflow, convert it to a numpy array
            # (we are assuming that sample_weight is small enough to fit into memory)
            if isinstance(sample_weight, dprep.Dataflow):
                sample_weight = sample_weight.to_pandas_dataframe().iloc[:, 0].values

            if self.task == Tasks.CLASSIFICATION:
                y_transformer = dataset.get_y_transformer()
                class_labels = self._get_class_labels(dataset)
                train_labels = self._get_trained_labels(model, y_train=y_train,
                                                        dataset=dataset, problem_info=problem_info)

                # ensure that labels sent into metrics code are numeric or string
                if not np.issubdtype(y_valid.dtype, np.number):
                    y_valid = y_valid.astype(str)
                    class_labels = class_labels.astype(str)
                    train_labels = train_labels.astype(str)

                # Remove empty string labels because NimbusML/ML.NET ignores them when
                # reporting predict_proba for classification tasks
                train_labels = np.array([label for label in train_labels if label != '' and label is not None])

                scores = scoring.score_classification(
                    y_valid, y_pred, self.metrics, class_labels, train_labels,
                    sample_weight=sample_weight, y_transformer=y_transformer,
                    logger=self.activity_logger)
            elif self.task == Tasks.REGRESSION:
                y_min, y_max = dataset.get_y_range()
                bin_info = dataset.get_bin_info()

                y_std = None
                if problem_info is None or not problem_info.enable_streaming:
                    y_std = dataset.get_y_std()

                scores = scoring.score_regression(
                    y_valid, y_pred, self.metrics,
                    y_min=y_min, y_max=y_max, y_std=y_std,
                    bin_info=bin_info,
                    sample_weight=sample_weight,
                    logger=self.activity_logger)

                if dataset.is_timeseries():
                    additional_metrics = list(scoring_constants.FORECASTING_SET)
                    try:
                        if isinstance(X_valid, pd.DataFrame):
                            horizons = X_valid[constants.TimeSeriesInternal.HORIZON_NAME].values
                        else:
                            tst = dataset.get_transformer(constants.Transformers.TIMESERIES_TRANSFORMER)
                            horizon_idx = (tst.get_engineered_feature_names().
                                           index(constants.TimeSeriesInternal.HORIZON_NAME))
                            horizons = X_valid[:, horizon_idx]
                    except (KeyError, ValueError):
                        # if no horizon is present we are doing a basic forecast
                        # we can assume all horizons are the same
                        horizons = [None] * len(y_pred)

                    additional_scores = scoring.score_forecasting(
                        y_valid, y_pred, additional_metrics, horizons,
                        y_min=y_min, y_max=y_max, y_std=y_std,
                        bin_info=bin_info,
                        sample_weight=sample_weight,
                        logger=self.activity_logger)
                    scores.update(additional_scores)
            else:
                raise NotImplementedError
            scores[TrainingResultsType.PREDICT_TIME] = predict_time.total_seconds()
            return scores

    def _predict(self, task, model, X_valid):
        """
        Return predictions from the given model with a provided task type.

        :param task: The task type (see constants.py).
        :param model: The model used to make predictions.
        :param X_valid: The inputs on which to predict.
        :return: The predictions of the model on X_valid
            The shape of the array returned depends on the task type
            Classification will return probabilities for each class.
        """
        with self.activity_logger.log_activity(logger=None,
                                               activity_name=constants.TelemetryConstants.PREDICT_NAME):
            if task == Tasks.CLASSIFICATION:
                return model.predict_proba(X_valid)
            elif task == Tasks.REGRESSION:
                return model.predict(X_valid)
            else:
                raise NotImplementedError

    def _get_class_labels(self, dataset):
        """
        Get the full set of class labels from the dataset.

        Sometimes the class_labels attribute is not set on the ClientDatasets object if the
        object is constructed with the meta_data parameter. In this case we need to compute
        the unique labels by hand in order to compute metrics.

        :param dataset: The DatasetBase object that contains information about the dataset.
        :return: The labels from the full dataset.
        """
        class_labels = dataset.get_class_labels()
        if class_labels is not None:
            return class_labels
        _, y, _ = dataset.get_full_set()
        return np.unique(y[~np.isnan(y)])

    def _get_trained_labels(self, model, y_train=None, dataset=None, problem_info=None):
        """
        Return the class labels that a model has been trained on.

        Sometimes a model is only trained on a subset of the class labels from
        the dataset. This is especially common with cross validation and
        custom validation sets. This function returns the class labels that
        a model has been trained on.
        If the model is a regression model the function returns np.unique of y_train,
        but this function shouldn't be used for regression
        :param model: The model used to make predictions.
        :param y_train: Targets used during model training.
        :param dataset: The DatasetBase object that contains information about the dataset.
        :param problem_info: The ProblemInfo object used for the run.
        :return: The labels used when training the model.
        """
        if hasattr(model, "classes_") and model.classes_ is not None:
            return model.classes_
        if problem_info is not None and problem_info.enable_streaming and dataset is not None:
            return dataset.get_train_class_labels()
        if y_train is None:
            raise ValueError("y_train must be passed if the model does not support the classes_ attribute")
        return np.unique(y_train)

    def run(self,
            dataset: DatasetBase,
            pipeline_spec: PipelineSpec,
            problem_info: ProblemInfo,
            sets_to_run: Optional[List[str]] = None,
            subsample_percent: Optional[float] = None,
            enforce_limits: bool = True,
            is_ensemble_iteration: bool = False,
            random_state: Optional[int] = None,
            include_models: bool = False,
            subsample_seed: Optional[int] = 0) -> Tuple[Any, Optional[BaseException]]:
        """
        Run the specific run task.

        :param dataset:
        :param pipeline_spec: A pipeline specification (obtained from the API).
            Not to be confused with a sklearn Pipeline object.
        :param problem_info:
        :param sets_to_run:
        :param subsample_percent:
        :param enforce_limits: If true, run in a subprocess.
        :param is_ensemble_iteration: bool to indicate whether
            it is an ensemble iteration
        :param random_state: random_state for random operations
        :param include_models:
        :param subsample_seed: a int for seeding subsample operations
        :return: A dict of results, filled in with TrainingResultsType keys.
        """
        if sets_to_run is None:
            sets_to_run = list(constants.TrainingType.FULL_SET)

        kwargs = {'sets_to_run': sets_to_run,
                  'subsample_percent': subsample_percent,
                  'random_state': random_state,
                  'subsample_seed': subsample_seed,
                  'include_models': include_models}

        func = cast('Callable[..., Any]', self._run_ensembling_internal if is_ensemble_iteration else self._run)

        if pipeline_spec.supports_constrained_fit():
            constraints = resource_limits.DEFAULT_RESOURCE_LIMITS
            enforce_limits = False
        else:
            constraints = problem_info.runtime_constraints

        limiter = SafeEnforceLimits(enable_limiting=enforce_limits, logger=self.activity_logger, **constraints)
        result, exit_status, _ = limiter.execute(func, *(dataset, pipeline_spec, problem_info), **kwargs)
        return result, exit_status

    def _run_ensembling_internal(self, dataset, pipeline_spec, problem_info, sets_to_run, **kwargs):
        with self.activity_logger.log_activity(logger=None,
                                               activity_name=constants.TelemetryConstants.RUN_ENSEMBLING_NAME):
            with dataset.open_dataset():
                pipeline = pipeline_spec.instantiate_pipeline_spec(
                    problem_info, is_sparse=dataset.get_is_sparse())
                if TrainingType.MeanCrossValidation in sets_to_run:
                    training_type = constants.TrainingType.MeanCrossValidation
                else:
                    training_type = constants.TrainingType.TrainAndValidation

                fit_time, fitted_ensemble_model, scoring_ensembles = \
                    self.time_fit_ensemble(pipeline, training_type, dataset)
                fitted_pipeline = sklearn.pipeline.make_pipeline(fitted_ensemble_model)

                if training_type == TrainingType.TrainAndValidation:
                    _, y_train, _ = dataset.get_train_set()
                    X_valid, y_valid, sample_weight_valid = dataset.get_valid_set()
                    score_valid = self._compute_metrics(
                        X_valid, y_valid, y_train,
                        fitted_pipeline, dataset,
                        sample_weight=sample_weight_valid)
                elif training_type == TrainingType.MeanCrossValidation:
                    fold_index = 0
                    scores = []
                    for _, y_train, _, X_test, y_test, sample_wt_test in dataset.get_CV_splits():
                        m = scoring_ensembles[fold_index]
                        score = self._compute_metrics(
                            X_test, y_test, y_train,
                            m, dataset,
                            sample_weight=sample_wt_test)
                        scores.append(score)
                        fold_index += 1
                    score_valid = scoring.aggregate_scores(scores, self.metrics)
                return score_valid, fit_time, fitted_pipeline

    def time_fit_ensemble(self, m, training_type, dataset):
        """
        Run the ensemble fit of the given model.

        :param m: The model to run the fit.
        :param X: Input data.
        :param y: Target values.
        :return: Elapsed time in seconds, the fitted ensemble with all the selected models.
        """
        with self.activity_logger.log_activity(logger=None,
                                               activity_name=constants.TelemetryConstants.TIME_FIT_ENSEMBLE_NAME):
            t = datetime.datetime.utcnow()  # time.process_time()
            fitted_ensemble_model, scoring_ensembles = m._final_estimator.fit_ensemble(
                training_type, dataset)
            elapsed_time = datetime.datetime.utcnow() - t
            return elapsed_time.seconds, fitted_ensemble_model, scoring_ensembles

    def _get_activity_logger(self) -> ActivityLogger:
        if self._log_config is None:
            return DummyActivityLogger()
        else:
            filename, verbosity, namespace = self._log_config.get_params()
            component_name = self._log_config.get_component_name()
            custom_dimensions = self._log_config.get_custom_dimensions()
            logger = TelemetryActivityLogger(namespace=namespace,
                                             filename=filename,
                                             verbosity=verbosity,
                                             component_name=component_name,
                                             custom_dimensions=custom_dimensions)
            if self.execution_context is not None:
                child_run_id = self.execution_context.run_id
                logger.update_default_properties(
                    {
                        "parent_run_id": self.execution_context.parent_run_id,
                        "child_run_id": child_run_id,
                        # TODO Child run is "RunId" in StandardFields
                        "run_id": child_run_id
                    }
                )

        return logger

    @staticmethod
    def fit_pipeline(pipeline_obj, X, y, sample_weight=None):
        """
        Fit a pipeline.

        Helper function to fit a pipeline, encapsulating sample_weight capability for models supporting it.

        :param pipeline_obj: The pipeline to run the fit on.
        :param X: Input data.
        :param y: Target values.
        :param sample_weight: Sample weights for training data.
        """
        kwargs = {}     # type: Dict[str, Any]
        if isinstance(pipeline_obj, sklearn.pipeline.Pipeline) and sample_weight is not None:
            # get model's name in steps array
            clf = pipeline_obj.steps[-1][0]
            if clf not in Sample_Weights_Unsupported:
                # pipeline expects kwargs to be formatted as stepname__arg.
                # The arg is then passed to fit of stepname
                kwargs = {clf + "__sample_weight": sample_weight}
        if isinstance(X, dprep.Dataflow) and isinstance(y, dprep.Dataflow):
            pipeline_obj.fit(X, y, **kwargs)
        else:
            pipeline_obj.fit(X, y.ravel(), **kwargs)
        return pipeline_obj

    @staticmethod
    def fit_pipeline_input_dataset(pipeline_obj: Any,
                                   training_data: Union[dprep.Dataflow, pd.DataFrame]) -> None:
        """
        Fit a pipeline.

        Helper function to fit a pipeline, encapsulating sample_weight capability for models supporting it.

        :param pipeline_obj: The pipeline to run the fit on.
        :param training_data: Input data.
        """
        kwargs = {}     # type: Dict[str, Any]
        if isinstance(training_data, dprep.Dataflow):
            pipeline_obj.fit(training_data, **kwargs)
        else:
            # TODO make this work for pandas dataframe for non streaming case.
            # https://msdata.visualstudio.com/Vienna/_workitems/edit/507123
            pass


if __name__ == '__main__':
    pass
