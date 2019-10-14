# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Validation for AutoML metrics."""
import logging
import numpy as np
import sklearn.utils

from sklearn.base import TransformerMixin
from typing import List, Optional

from automl.client.core.runtime.score import constants, utilities
from automl.client.core.runtime.score._metric_base import NonScalarMetric
from automl.client.core.common.exceptions import ClientException, DataException


def validate_classification(y_test: np.ndarray,
                            y_pred_probs: np.ndarray,
                            metrics: List[str],
                            class_labels: np.ndarray,
                            train_labels: np.ndarray,
                            sample_weight: Optional[np.ndarray],
                            y_transformer: Optional[TransformerMixin]) -> None:
    """
    Validate the inputs for scoring classification.

    :param y_test: Target values.
    :param y_pred_probs: The predicted probabilities for all classes.
    :param metrics: Metrics to compute.
    :param class_labels: All classes found in the full dataset.
    :param train_labels: Classes as seen (trained on) by the trained model.
    :param sample_weight: Weights for the samples.
    :param y_transformer: Used to inverse transform labels.
    """
    for metric in metrics:
        if metric not in constants.CLASSIFICATION_SET:
            raise ClientException("Metric {} not a valid classification metric".format(metric))

    if class_labels is None:
        raise ClientException("class_labels must not be None")

    if train_labels is None:
        raise ClientException("train_labels must not be None")

    _check_y_test_y_pred(y_test, y_pred_probs, y_pred_name='y_pred_probs')
    _check_dim(y_test, 'y_test', 1)
    _check_dim(y_pred_probs, 'y_pred_probs', 2)

    if sample_weight is not None and y_test.shape[0] != sample_weight.shape[0]:
        raise ClientException("Number of samples does not match in y_test ({}) and sample_weight ({})"
                              .format(y_test.shape[0], sample_weight.shape[0]))

    if train_labels.shape[0] != y_pred_probs.shape[1]:
        raise ClientException("train_labels.shape[0] ({}) does not match y_pred_probs.shape[1] ({})."
                              .format(train_labels.shape[0], y_pred_probs.shape[1]))

    if np.setdiff1d(train_labels, class_labels).shape[0] != 0:
        raise ClientException("train_labels contains values not present in class_labels")

    if np.setdiff1d(np.unique(y_test), class_labels).shape[0] != 0:
        raise ClientException("y_test contains value not present in class_labels")

    _check_array(y_test, 'y_test', ensure_2d=False)
    _check_array(y_pred_probs, 'y_pred_probs')


def log_classification_debug(logger: logging.Logger,
                             y_test: np.ndarray,
                             y_pred_probs: np.ndarray,
                             class_labels: np.ndarray,
                             train_labels: np.ndarray,
                             sample_weight: Optional[np.ndarray] = None) -> None:
    """
    Log shapes of classification inputs for debugging.

    :param logger: A logger to log errors and warnings
    :param y_test: Target values
    :param y_pred_probs: The predicted probabilities for all classes
    :param class_labels: All classes found in the full dataset
    :param train_labels: Classes as seen (trained on) by the trained model
    :param sample_weight: Weights for the samples
    """
    unique_y_test = np.unique(y_test)
    debug_data = {
        'y_test': y_test.shape,
        'y_pred_probs': y_pred_probs.shape,
        'unique_y_test': unique_y_test.shape,
        'class_labels': class_labels.shape,
        'train_labels': train_labels.shape,
        'n_missing_train': np.setdiff1d(class_labels, train_labels).shape[0],
        'n_missing_valid': np.setdiff1d(class_labels, unique_y_test).shape[0],
        'sample_weight': None if sample_weight is None else sample_weight.shape
    }

    logger.info("Classification metrics debug: {}".format(debug_data))


def validate_regression(y_test: np.ndarray,
                        y_pred: np.ndarray,
                        metrics: List[str]) -> None:
    """
    Validate the inputs for scoring regression.

    :param y_test: Target values.
    :param y_pred: Target predictions.
    :param metrics: Metrics to compute.
    """
    # TODO: Put test back in once forecasting and regression are decoupled
    # for metric in metrics:
    #     if metric not in constants.REGRESSION_SET:
    #         raise ClientException("Metric {} not a valid regression metric".format(metric))

    _check_y_test_y_pred(y_test, y_pred)
    _check_array(y_test, 'y_test', ensure_2d=False)
    _check_array(y_pred, 'y_pred', ensure_2d=False)


def log_regression_debug(logger: logging.Logger,
                         y_test: np.ndarray,
                         y_pred: np.ndarray,
                         sample_weight: Optional[np.ndarray] = None) -> None:
    """
    Log shapes of regression inputs for debugging.

    :param logger: A logger to log errors and warnings
    :param y_test: Target values
    :param y_pred: Predicted values
    :param sample_weight: Weights for the samples
    """
    debug_data = {
        'y_test': y_test.shape,
        'y_pred': y_pred.shape,
        'sample_weight': None if sample_weight is None else sample_weight.shape
    }

    logger.info("Regression metrics debug: {}".format(debug_data))


def validate_forecasting(y_test: np.ndarray,
                         y_pred: np.ndarray,
                         metrics: List[str]) -> None:
    """
    Validate the inputs for scoring forecasting.

    :param y_test: Target values.
    :param y_pred: Target predictions.
    :param metrics: Metrics to compute.
    """
    for metric in metrics:
        if metric not in constants.FORECASTING_SET:
            raise ClientException("Metric {} not a valid forecasting metric".format(metric))

    _check_y_test_y_pred(y_test, y_pred)
    _check_array(y_test, 'y_test', ensure_2d=False)
    _check_array(y_pred, 'y_pred', ensure_2d=False)


def log_forecasting_debug(logger: logging.Logger,
                          y_test: np.ndarray,
                          y_pred: np.ndarray,
                          sample_weight: Optional[np.ndarray] = None) -> None:
    """
    Log shapes of forecasting inputs for debugging.

    :param logger: A logger to log errors and warnings
    :param y_test: Target values
    :param y_pred: Predicted values
    :param sample_weight: Weights for the samples
    """
    debug_data = {
        'y_test': y_test.shape,
        'y_pred': y_pred.shape,
        'sample_weight': None if sample_weight is None else sample_weight.shape
    }

    logger.info("Forecasting metrics debug: {}".format(debug_data))


def _check_y_test_y_pred(y_test: np.ndarray,
                         y_pred: np.ndarray,
                         y_pred_name: str = 'y_pred') -> None:
    """
    Validate that y_test and y_pred are the same shape.

    :y_test: Actual targets.
    :y_pred: Predicted targets (or probabilities).
    """
    if y_test is None:
        raise ClientException("y_test must not be None")
    if y_pred is None:
        raise ClientException("{} must not be None".format(y_pred_name))
    if y_test.shape[0] != y_pred.shape[0]:
        raise ClientException("Number of samples does not match in y_test ({}) and {} ({})"
                              .format(y_test.shape[0], y_pred_name, y_pred.shape[0]))


def _check_array(arr: np.ndarray,
                 name: str,
                 ensure_2d: bool = True) -> None:
    """
    Check the array for reasonable values.

    :param arr: Array to check.
    :param name: Array name.
    :param ensure_2d: Extra check to ensure 2 dimensional.
    """
    if arr.dtype.kind in set('bcfiu'):
        if np.isnan(arr).any():
            raise ClientException("Elements of {} cannot be NaN".format(name))

        if ~np.isfinite(arr).all():
            raise ClientException("Elements of {} cannot be infinite".format(name))

    if not np.issubdtype(arr.dtype, np.str_):
        try:
            sklearn.utils.check_array(arr, ensure_2d=ensure_2d)
        except ValueError as e:
            raise DataException.from_exception(e, "{} failed sklearn.utils.check_array().".format(name))


def _check_dim(arr: np.array,
               name: str,
               n_dim: int) -> None:
    """
    Check the number of dimensions for the given array.

    :param arr: Array to check.
    :param name: Array name.
    :param n_dim: Expected number of dimensions.
    """
    if arr.ndim != n_dim:
        raise ClientException("{} must be an ndarray with {} dimensions".format(name, n_dim))


def format_1d(arr: np.ndarray) -> np.ndarray:
    """
    Format an array as 1d if possible.

    :param arr: The array to reshape.
    :return: Array of shape (x,).
    """
    if arr is None:
        return arr
    if arr.ndim == 2 and (arr.shape[0] == 1 or arr.shape[1] == 1):
        arr = np.ravel(arr)
    return arr


def log_failed_splits(scores, metric, logger):
    """
    Log if a metric could not be computed for some splits.

    :scores: The scores over all splits for one metric.
    :metric: Name of the metric.
    :logger: Warning and error logger.
    """
    n_splits = len(scores)

    failed_splits = []
    for score_index, score in enumerate(scores):
        if utilities.is_scalar(metric):
            if np.isnan(score):
                failed_splits.append(score_index)
        else:
            if NonScalarMetric.is_error_metric(score):
                failed_splits.append(score_index)
    n_failures = len(failed_splits)
    failed_splits_str = ', '.join([str(idx) for idx in failed_splits])

    if n_failures > 0:
        warn_args = metric, n_failures, n_splits, failed_splits_str
        warn_msg = "Could not compute {} for {}/{} validation splits: {}"
        logger.warning(warn_msg.format(*warn_args))
