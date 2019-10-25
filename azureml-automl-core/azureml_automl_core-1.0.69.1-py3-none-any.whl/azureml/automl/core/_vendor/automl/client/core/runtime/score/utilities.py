# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Utilities for computing model evaluation metrics."""
import numpy as np
import sys

from typing import Any, Dict, List, Optional, Tuple

from automl.client.core.runtime.score import constants
from automl.client.core.common.exceptions import ClientException


def get_metric_task(metric: str) -> str:
    """
    Get the task for a given metric.

    :param metric: The metric to lookup.
    :return: The task type for the given metric.
    """
    if metric in constants.CLASSIFICATION_SET:
        return constants.CLASSIFICATION
    elif metric in constants.REGRESSION_SET:
        return constants.REGRESSION
    elif metric in constants.FORECASTING_SET:
        return constants.FORECASTING
    raise ClientException("Metric {} not found".format(metric))


def minimize_or_maximize(metric: str,
                         task: Optional[str] = None) -> str:
    """
    Select the objective given a metric.

    Some metrics should be minimized and some should be maximized
    :param metric: the name of the metric to look up
    :return: returns one of constants.OptimizerObjectives.
    """
    if task is None:
        task = get_metric_task(metric)
    return constants.OBJECTIVES_TASK_MAP[task][metric]


def is_better(val1: float,
              val2: float,
              metric: Optional[str] = None,
              objective: Optional[str] = None) -> bool:
    """Select the best of two values given metric or objectives.

    :param val1: scalar value
    :param val2: scalar value
    :param metric: the name of the metric to look up
    :param task: one of constants.Tasks.
    :param objective: one of constants.OptimizerObjectives.
    return: returns a boolean of if val1 is better than val2 in the situation
    """
    if objective is None:
        if metric is None:
            raise ClientException("Must specific either Metric or Objective")
        else:
            objective = minimize_or_maximize(metric)
    if objective == constants.MAXIMIZE:
        return val1 > val2
    elif objective == constants.MINIMIZE:
        return val1 < val2
    return False


def get_all_nan(task: str) -> Dict[str, float]:
    """Create a dictionary of metrics to values for the given task.

    All metric values are set to nan initially
    :param task: one of constants.Tasks.
    :return: returns a dictionary of nans for each metric for the task.
    """
    return {m: np.nan for m in constants.METRICS_TASK_MAP[task]}


def get_metric_ranges(task: str,
                      for_assert_sane: Optional[bool] = False) -> Tuple[Dict[str, float], Dict[str, float]]:
    """Get the metric range for the task.

    :param task: string "classification" or "regression"
    :param for_assert_sane: boolean indicates that this is being used
        by assert_metrics_sane and it is unsafe to apply clips.
    :return: returns tuple with min values dict and max value dict.
    """
    minimums = get_min_values(task)
    maximums = get_max_values(task, for_assert_sane=for_assert_sane)
    return minimums, maximums


def get_worst_values(task: str,
                     for_assert_sane: Optional[bool] = False) -> Dict[str, float]:
    """Get the worst values for metrics of the task.

    :param task: string "classification" or "regression"
    :param for_assert_sane: boolean indicates that this is being used
        by assert_metrics_sane and it is unsafe to apply clips.
    :return: returns a dictionary of metrics with the worst values.
    """
    minimums, maximums = get_metric_ranges(
        task, for_assert_sane=for_assert_sane)
    objectives = constants.OBJECTIVES_TASK_MAP[task]
    bad = {m: minimums[m] if obj == constants.MAXIMIZE else maximums[m]
           for m, obj in objectives.items()}
    return bad


def get_min_values(task: str) -> Dict[str, float]:
    """Get the minimum values for metrics for the task.

    :param task: string "classification" or "regression"
    :return: returns a dictionary of metrics with the min values.
    """
    metrics = constants.METRICS_TASK_MAP[task]
    # 0 is the minimum for metrics that are minimized and maximized
    bad = {m: 0.0 for m in metrics}
    bad[constants.R2_SCORE] = -10.0  # R2 is different, clipped to -10.0
    bad[constants.SPEARMAN] = -1.0
    return bad


def get_max_values(task: str,
                   for_assert_sane: Optional[bool] = False) -> Dict[str, float]:
    """Get the maximum values for metrics of the task.

    :param task: string "classification" or "regression"
    :param for_assert_sane: boolean indicates that this is being used
        by assert_metrics_sane and it is unsafe to apply clips.
    :return: returns a dictionary of metrics with the max values.
    """
    objectives = constants.OBJECTIVES_TASK_MAP[task]
    _MAX = constants.MAXIMIZE
    bad = {m: 1.0 if obj == _MAX else sys.float_info.max
           for m, obj in objectives.items()}
    # so the assertions don't fail, could also clip metrics instead
    if not for_assert_sane:
        bad[constants.LOG_LOSS] = 10.0
        bad[constants.NORM_RMSE] = 10.0
        bad[constants.NORM_RMSLE] = 10.0
        bad[constants.NORM_MEAN_ABS_ERROR] = 10.0
        bad[constants.NORM_MEDIAN_ABS_ERROR] = 10.0
    return bad


def assert_metrics_sane(scores: Dict[str, Any],
                        task: str) -> None:
    """Assert that the given metric values are sane.

    The metric values should not be worse than the worst possible values
    for those metrics given the objectives for those metrics
    :param task: Task string, (e.g. "classification" or "regression")
    """
    worst = get_worst_values(task, for_assert_sane=True)
    objectives = constants.OBJECTIVES_TASK_MAP[task]
    for k, v in scores.items():
        if not np.isscalar(v) or np.isnan(v):
            continue
        # This seems to vary a lot.
        if k == constants.EXPLAINED_VARIANCE:
            continue
        if objectives[k] == constants.MAXIMIZE:
            assert v >= worst[k], (
                '{0} is not worse than {1} for metric {2}'.format(
                    worst[k], v, k))
        else:
            assert v <= worst[k], (
                '{0} is not worse than {1} for metric {2}'.format(
                    worst[k], v, k))


def get_scalar_metrics(task: str) -> List[str]:
    """Get the scalar metrics supported for a given task.

    :param task: Task string, (e.g. "classification" or "regression")
    :return: List of the default metrics supported for the task
    """
    return {
        constants.CLASSIFICATION: list(constants.CLASSIFICATION_SCALAR_SET),
        constants.REGRESSION: list(constants.REGRESSION_SCALAR_SET),
        constants.FORECASTING: list(constants.FORECASTING_SCALAR_SET)
    }[task]


def get_default_metrics(task: str) -> List[str]:
    """Get the metrics supported for a given task as a set.

    :param task: Task string, (e.g. "classification" or "regression")
    :return: List of the default metrics supported for the task
    """
    return {
        constants.CLASSIFICATION: list(constants.CLASSIFICATION_SET),
        constants.REGRESSION: list(constants.REGRESSION_SET),
        constants.FORECASTING: list(constants.FORECASTING_SET)
    }[task]


def is_scalar(metric_name: str) -> bool:
    """
    Check whether a given metric is scalar or nonscalar.

    :param metric_name: the name of the metric found in constants.py
    :return: boolean for if the metric is scalar
    """
    if metric_name in constants.FULL_SCALAR_SET:
        return True
    elif metric_name in constants.FULL_NONSCALAR_SET:
        return False
    raise ClientException("{} metric is not supported".format(metric_name))
