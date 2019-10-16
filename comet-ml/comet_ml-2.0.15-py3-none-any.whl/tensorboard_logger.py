# -*- coding: utf-8 -*-
# *******************************************************
#   ____                     _               _
#  / ___|___  _ __ ___   ___| |_   _ __ ___ | |
# | |   / _ \| '_ ` _ \ / _ \ __| | '_ ` _ \| |
# | |__| (_) | | | | | |  __/ |_ _| | | | | | |
#  \____\___/|_| |_| |_|\___|\__(_)_| |_| |_|_|
#
#  Sign up for free at http://www.comet.ml
#  Copyright (C) 2015-2019 Comet ML INC
#  This file can not be copied and/or distributed without the express
#  permission of Comet ML Inc.
# *******************************************************


import logging

from ._logging import check_module
from ._typing import Any, Dict, List, Tuple
from .utils import Histogram

LOGGER = logging.getLogger(__name__)
LOG_METRICS = True
LOG_HISTOGRAMS = True


def extract_from_add_summary(file_writer, summary, global_step):
    # type: (Any, Any, int) -> Tuple[Dict[str, float], List[Any], int]
    from tensorflow.core.framework import summary_pb2

    extracted_metrics = {}  # type: Dict[str, float]
    extracted_histo = []  # type: List[Any]

    if isinstance(summary, bytes):
        summ = summary_pb2.Summary()
        summ.ParseFromString(summary)
        summary = summ

    for value in summary.value:
        field = value.WhichOneof("value")

        if field == "simple_value":
            extracted_metrics[value.tag] = value.simple_value
        elif field == "histo":
            # TODO: Test ME!
            extracted_histo.append(value.histo)

    return extracted_metrics, extracted_histo, global_step


def convert_histograms(histo):
    """
    Convert tensorboard summary histogram format into a Comet histogram.
    """
    histogram = Histogram()
    values = histo.bucket_limit
    counts = histo.bucket
    histogram.add(values, counts)
    return histogram


def add_summary_logger(experiment, original, value, *args, **kwargs):
    """
    Note: auto_metric_logging controls summary metrics and histograms
    Note: assumes "simple_value" is a metric
    """
    try:
        if (
            experiment.auto_metric_logging
            and not experiment.disabled_monkey_patching
            and (LOG_METRICS or LOG_HISTOGRAMS)
        ):
            LOGGER.debug("TENSORBOARD LOGGER CALLED")
            metrics, histo, step = extract_from_add_summary(*args, **kwargs)
            if metrics and LOG_METRICS:
                experiment.log_metrics(metrics, step=step)
            if histo and LOG_HISTOGRAMS:
                for histo in histo:
                    experiment.log_histogram_3d(convert_histograms(histo), step=step)

    except Exception:
        LOGGER.error(
            "Failed to extract metrics/histograms from add_summary()", exc_info=True
        )


def summary_scalar_logger(experiment, original, value, *args, **kwargs):
    """
    Note: Assumes summary.scalars are metrics.
    """
    try:
        if (
            experiment.auto_metric_logging
            and not experiment.disabled_monkey_patching
            and LOG_METRICS
        ):
            name, data, step = get_args(*args, **kwargs)
            experiment.log_metric(name, data, step=step)
    except Exception:
        LOGGER.error(
            "Failed to extract metrics from tensorflow.summary.scalar()", exc_info=True
        )


def summary_histogram_3d_logger(experiment, original, value, *args, **kwargs):
    try:
        if (
            experiment.auto_metric_logging
            and not experiment.disabled_monkey_patching
            and LOG_HISTOGRAMS
        ):
            # FIXME:
            # name, data, step = get_args(*args, **kwargs)
            # experiment.log_histogram_3d(name, data, step=step)
            pass
    except Exception:
        LOGGER.error(
            "Failed to extract histogram 3D from tensorflow.summary.histogram()",
            exc_info=True,
        )


def get_args(name, data, step=None, **kwargs):
    """
    Wrapper to parse args
    """
    return (name, data, step)


class ContextHolder:
    def __init__(self, new_context):
        self.new_context = new_context
        self.old_context = None

    def enter(self, experiment, *args, **kwargs):
        self.old_context = experiment.context
        experiment.context = self.new_context

    def exit(self, experiment, *args, **kwargs):
        experiment.context = self.old_context
        self.old_context = None


TRAIN_HOLDER = ContextHolder("train")
EVAL_HOLDER = ContextHolder("eval")


def patch(module_finder):
    check_module("tensorflow")
    check_module("tensorboard")

    # tensorflow 1.11.0 - 1.14.0 in non-compatible mode:
    module_finder.register_after(
        "tensorflow.python.summary.writer.writer",
        "FileWriter.add_summary",
        add_summary_logger,
    )
    module_finder.register_before(
        "tensorflow.python.estimator.estimator", "Estimator.train", TRAIN_HOLDER.enter
    )
    module_finder.register_after(
        "tensorflow.python.estimator.estimator", "Estimator.train", TRAIN_HOLDER.exit
    )
    module_finder.register_before(
        "tensorflow_estimator.python.estimator.estimator",
        "Estimator.train",
        TRAIN_HOLDER.enter,
    )
    module_finder.register_after(
        "tensorflow_estimator.python.estimator.estimator",
        "Estimator.train",
        TRAIN_HOLDER.exit,
    )
    module_finder.register_before(
        "tensorflow.python.estimator.estimator", "Estimator.evaluate", EVAL_HOLDER.enter
    )
    module_finder.register_after(
        "tensorflow.python.estimator.estimator", "Estimator.evaluate", EVAL_HOLDER.exit
    )
    module_finder.register_before(
        "tensorflow_estimator.python.estimator.estimator",
        "Estimator.evaluate",
        EVAL_HOLDER.enter,
    )
    module_finder.register_after(
        "tensorflow_estimator.python.estimator.estimator",
        "Estimator.evaluate",
        EVAL_HOLDER.exit,
    )
    # tensorflow 2:
    module_finder.register_after(
        "tensorboard.plugins.scalar.summary_v2", "scalar", summary_scalar_logger
    )
    module_finder.register_after(
        "tensorboard.plugins.scalar.summary_v2",
        "histogram",
        summary_histogram_3d_logger,
    )


check_module("tensorflow")
check_module("tensorboard")
