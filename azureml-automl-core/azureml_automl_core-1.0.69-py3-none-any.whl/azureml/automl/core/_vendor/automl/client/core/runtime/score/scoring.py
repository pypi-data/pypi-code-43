# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Computation of AutoML model evaluation metrics."""
import logging
import numpy as np
import sklearn.preprocessing

from abc import abstractmethod
from sklearn.base import TransformerMixin
from typing import Any, cast, Dict, List, Optional, Type, Union

from automl.client.core.common import logging_utilities
from automl.client.core.runtime.score import _scoring_utilities, _validation, constants, utilities
from automl.client.core.runtime.score._metric_base import Metric, NonScalarMetric


def score_classification(y_test: np.ndarray,
                         y_pred_probs: np.ndarray,
                         metrics: List[str],
                         class_labels: np.ndarray,
                         train_labels: np.ndarray,
                         sample_weight: Optional[np.ndarray] = None,
                         y_transformer: Optional[TransformerMixin] = None,
                         logger: Optional[logging.Logger] = None) -> Dict[str, Union[float, Dict[str, Any]]]:
    """
    Compute model evaluation metrics for a classification task.

    All class labels for y should come
    as seen by the fitted model (i.e. if the fitted model uses a y transformer the labels
    should also come transformed).

    All metrics present in `metrics` will be present in the output dictionary with either
    the value(s) calculated or `nan` if the calculation failed.

    :param y_test: The target values (Transformed if using a y transformer)
    :param y_pred_probs: The predicted probabilities for all classes.
    :param metrics: Classification metrics to compute
    :param class_labels: All classes found in the full dataset (includes train/valid/test sets).
        These should be transformed if using a y transformer.
    :param train_labels: Classes as seen (trained on) by the trained model. These values
        should correspond to the columns of y_pred_probs in the correct order.
    :param sample_weight: Weights for the samples (Does not need
        to match sample weights on the fitted model)
    :param y_transformer: Used to inverse transform labels from `y_test`. Required for non-scalar metrics.
    :param logger: A logger to log errors and warnings
    :return: A dictionary mapping metric name to metric score.
    """
    if logger is None:
        logger = logging_utilities.NULL_LOGGER

    y_test = _validation.format_1d(y_test)

    _validation.validate_classification(y_test, y_pred_probs, metrics,
                                        class_labels, train_labels,
                                        sample_weight, y_transformer)

    _validation.log_classification_debug(logger, y_test, y_pred_probs, class_labels,
                                         train_labels, sample_weight=sample_weight)

    # Sort the class labels
    # This is required for both binarization of targets
    # and for matching the columns of predictions
    class_labels = np.unique(class_labels)

    # Some metrics use an eps of 1e-15 by default, which results in nans for float32.
    if y_pred_probs.dtype == np.float32:
        y_pred_probs = y_pred_probs.astype(np.float64)

    # Pad the predictions with 0 columns in case the model wasn't fit on the entire set of class labels
    y_pred_probs_padded = _scoring_utilities.pad_predictions(y_pred_probs, train_labels, class_labels)

    # Choose the class with the highest probability to be the predicted class
    # We can use class_labels here because we have already padded
    y_pred = class_labels[np.argmax(y_pred_probs_padded, axis=1)]

    # Non-scalar metrics operate on the actual class labels
    # If a transformer was passed, use it to get the original labels
    y_test_original, y_pred_original, class_labels_original = _scoring_utilities.classification_label_decode(
        y_transformer, y_test, y_pred, class_labels)

    # Label encode all labels so sklearn classification metrics work
    y_test_encoded, y_pred_encoded, class_labels_encoded = _scoring_utilities.classification_label_encode(
        y_test_original, y_pred_original, class_labels_original)

    encoding_binarizer = _scoring_utilities.LabelEncodingBinarizer()
    encoding_binarizer.fit(class_labels)
    y_test_bin = encoding_binarizer.transform(y_test)

    results = {}
    for name in metrics:
        try:
            metric_class = _scoring_utilities.get_metric_class(name)
            test_targets = y_test_encoded if utilities.is_scalar(name) else y_test_original
            pred_targets = y_pred_encoded if utilities.is_scalar(name) else y_pred_original
            labels = class_labels_encoded if utilities.is_scalar(name) else class_labels_original

            metric = metric_class(test_targets, y_pred_probs_padded, y_test_bin, pred_targets, labels,
                                  sample_weight=sample_weight, logger=logger)
            results[name] = metric.compute()
        except Exception as e:
            logging_utilities.log_traceback(e, logger, is_critical=False)
            if utilities.is_scalar(name):
                results[name] = np.nan
            else:
                results[name] = NonScalarMetric.get_error_metric()

    utilities.assert_metrics_sane(results, constants.CLASSIFICATION)
    return results


def score_regression(y_test: np.ndarray,
                     y_pred: np.ndarray,
                     metrics: List[str],
                     y_max: Optional[float] = None,
                     y_min: Optional[float] = None,
                     y_std: Optional[float] = None,
                     sample_weight: Optional[np.ndarray] = None,
                     bin_info: Optional[Dict[str, float]] = None,
                     logger: Optional[logging.Logger] = None) -> Dict[str, Union[float, Dict[str, Any]]]:
    """
    Compute model evaluation metrics for a regression task.

    The optional parameters `y_min`, `y_min`, and `y_min` should be based on the
        target column y from the full dataset.

    - `y_max` and `y_min` should be used to control the normalization of
    normalized metrics. The effect will be division by max - min.
    - `y_std` is used to estimate a sensible range for displaying non-scalar
    regression metrics.

    If the metric is undefined given the input data, the score will show
        as nan in the returned dictionary.

    :param y_test: The target values.
    :param y_pred: The predicted values.
    :param metrics: List of metric names for metrics to calculate.
    :type metrics: list
    :param y_max: The max target value.
    :param y_min: The min target value.
    :param y_std: The standard deviation of targets value.
    :param sample_weight:
        The sample weight to be used on metrics calculation. This does not need
        to match sample weights on the fitted model.
    :param bin_info:
        The binning information for true values. This should be calculated from
        :class:`ClientDatasets` :func:`make_bin_info`. Required for calculating
        non-scalar metrics.
    :param logger: A logger to log errors and warnings
    :return: A dictionary mapping metric name to metric score.
    """
    if logger is None:
        logger = logging_utilities.NULL_LOGGER

    # Lenient on shape of y_test and y_pred
    y_test = _validation.format_1d(y_test)
    y_pred = _validation.format_1d(y_pred)

    _validation.validate_regression(y_test, y_pred, metrics)
    _validation.log_regression_debug(logger, y_test, y_pred, sample_weight=sample_weight)

    y_min = np.min(y_test) if y_min is None else y_min
    y_max = np.max(y_test) if y_max is None else y_max
    y_std = np.std(y_test) if y_std is None else y_std

    results = {}
    for name in metrics:
        try:
            metric_class = _scoring_utilities.get_metric_class(name)
            metric = metric_class(y_test, y_pred, y_min=y_min, y_max=y_max, y_std=y_std,
                                  bin_info=bin_info, sample_weight=sample_weight, logger=logger)
            results[name] = metric.compute()
        except Exception as e:
            logging_utilities.log_traceback(e, logger, is_critical=False)
            if utilities.is_scalar(name):
                results[name] = np.nan
            else:
                results[name] = NonScalarMetric.get_error_metric()

    utilities.assert_metrics_sane(results, constants.REGRESSION)
    return results


def score_forecasting(y_test: np.ndarray,
                      y_pred: np.ndarray,
                      metrics: List[str],
                      horizons: np.ndarray,
                      y_max: Optional[float] = None,
                      y_min: Optional[float] = None,
                      y_std: Optional[float] = None,
                      sample_weight: Optional[np.ndarray] = None,
                      bin_info: Optional[Dict[str, float]] = None,
                      logger: Optional[logging.Logger] = None) -> Dict[str, Union[float, Dict[str, Any]]]:
    """
    Compute model evaluation metrics for a forecasting task.

    `y_max`, `y_min`, and `y_std` should be based on `y_test` information unless
    you would like to compute multiple metrics for comparison (ex. cross validation),
    in which case, you should use a common range and standard deviation. You may
    also pass in `y_max`, `y_min`, and `y_std` if you do not want it to be calculated.

    All metrics present in `metrics` will be present in the output dictionary with either
    the value(s) calculated or `nan` if metric calculation failed.

    :param y_test: The target values.
    :param y_pred: The predicted values.
    :param metrics: List of metric names for metrics to calculate.
    :type metrics: list
    :param horizons: The horizon of each prediction. If missing or not relevant, pass None.
    :param y_max: The max target value.
    :param y_min: The min target value.
    :param y_std: The standard deviation of targets value.
    :param sample_weight:
        The sample weight to be used on metrics calculation. This does not need
        to match sample weights on the fitted model.
    :param bin_info:
        The binning information for true values. This should be calculated from
        :class:`ClientDatasets` :func:`make_bin_info`. Required for calculating
        non-scalar metrics.
    :param logger: A logger to log errors and warnings
    :return: A dictionary mapping metric name to metric score.
    """
    if logger is None:
        logger = logging_utilities.NULL_LOGGER

    if len(horizons) != len(y_pred) or len(y_pred) != len(y_test):
        raise ValueError("Data to calculate metrics doesn't align.")

    # Lenient on shape of y_test and y_pred
    y_test = _validation.format_1d(y_test)
    y_pred = _validation.format_1d(y_pred)

    _validation.validate_forecasting(y_test, y_pred, metrics)
    _validation.log_forecasting_debug(logger, y_test, y_pred, sample_weight=sample_weight)

    results = {}
    for name in metrics:
        if name in constants.FORECASTING_NONSCALAR_SET:
            try:
                metric_class = _scoring_utilities.get_metric_class(name)
                metric = metric_class(y_test, y_pred, horizons,
                                      y_std=y_std, bin_info=bin_info, logger=logger)
                results[name] = metric.compute()
            except Exception as e:
                logging_utilities.log_traceback(e, logger, is_critical=False)
                if utilities.is_scalar(name):
                    results[name] = np.nan
                else:
                    results[name] = NonScalarMetric.get_error_metric()
                raise e
    return results


def aggregate_scores(
        scores: List[Dict[Any, Any]],
        metrics: List[str],
        logger: Optional[logging.Logger] = None) -> Dict[str, Union[float, Dict[str, Any]]]:
    """
    Compute mean scores across validation folds.

    :param scores: List of results from scoring functions.
    :param metrics: List of metrics to aggregate.
    :return: Dictionary containing the aggregated scores.
    """
    if logger is None:
        logger = logging_utilities.NULL_LOGGER

    means = {}      # type: Dict[str, Union[float, Dict[str, Any]]]
    for name in metrics:
        if name not in scores[0]:
            logger.warning("Tried to aggregate metric {}, but {} was not found in scores".format(name, name))
            continue

        split_results = [score[name] for score in scores if name in score]
        _validation.log_failed_splits(split_results, name, logger)
        metric_class = _scoring_utilities.get_metric_class(name)
        try:
            means[name] = metric_class.aggregate(split_results)
        except Exception as e:
            logging_utilities.log_traceback(e, logger, is_critical=False)
            means[name] = NonScalarMetric.get_error_metric()

    for train_type in constants.ALL_TIME:
        train_times = [res[train_type] for res in scores if train_type in res]
        if train_times:
            means[train_type] = float(np.mean(train_times))

    return means
