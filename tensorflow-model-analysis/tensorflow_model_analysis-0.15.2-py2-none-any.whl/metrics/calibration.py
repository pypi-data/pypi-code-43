# Copyright 2019 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""Calibration related metrics."""

from __future__ import absolute_import
from __future__ import division
# Standard __future__ imports
from __future__ import print_function

import apache_beam as beam
import numpy as np
from tensorflow_model_analysis import config
from tensorflow_model_analysis.metrics import metric_types
from tensorflow_model_analysis.metrics import metric_util
from tensorflow_model_analysis.types_compat import Any, Dict, List, Optional, Text

CALIBRATION_NAME = 'calibration'
MEAN_LABEL_NAME = 'mean_label'
MEAN_PREDICTION_NAME = 'mean_prediction'
_WEIGHTED_LABELS_PREDICTIONS_EXAMPLES_NAME = (
    '_weighted_labels_predictions_examples')


class MeanLabel(metric_types.Metric):
  """Mean label."""

  def __init__(self, name = MEAN_LABEL_NAME):
    """Initializes mean label.

    Args:
      name: Metric name.
    """
    super(MeanLabel, self).__init__(
        metric_util.merge_per_key_computations(_mean_label), name=name)


metric_types.register_metric(MeanLabel)


def _mean_label(
    name = MEAN_LABEL_NAME,
    eval_config = None,
    model_name = '',
    output_name = '',
    sub_key = None
):
  """Returns metric computations for mean label."""

  key = metric_types.MetricKey(
      name=name,
      model_name=model_name,
      output_name=output_name,
      sub_key=sub_key)

  # Make sure weighted_labels_predictions_examples are calculated.
  computations = _weighted_labels_predictions_examples(
      eval_config=eval_config,
      model_name=model_name,
      output_name=output_name,
      sub_key=sub_key)
  weighted_labels_predictions_key = computations[-1].keys[-1]

  def result(
      metrics
  ):
    """Returns mean label."""
    metric = metrics[weighted_labels_predictions_key]
    if np.isclose(metric.total_weighted_examples, 0.0):
      value = float('nan')
    else:
      value = metric.total_weighted_labels / metric.total_weighted_examples
    return {key: value}

  derived_computation = metric_types.DerivedMetricComputation(
      keys=[key], result=result)
  computations.append(derived_computation)
  return computations


class MeanPrediction(metric_types.Metric):
  """Mean prediction."""

  def __init__(self, name = MEAN_PREDICTION_NAME):
    """Initializes mean prediction.

    Args:
      name: Metric name.
    """
    super(MeanPrediction, self).__init__(
        metric_util.merge_per_key_computations(_mean_prediction), name=name)


metric_types.register_metric(MeanPrediction)


def _mean_prediction(
    name = MEAN_PREDICTION_NAME,
    eval_config = None,
    model_name = '',
    output_name = '',
    sub_key = None
):
  """Returns metric computations for mean prediction."""
  key = metric_types.MetricKey(
      name=name,
      model_name=model_name,
      output_name=output_name,
      sub_key=sub_key)

  # Make sure weighted_labels_predictions_examples are calculated.
  computations = _weighted_labels_predictions_examples(
      eval_config=eval_config,
      model_name=model_name,
      output_name=output_name,
      sub_key=sub_key)
  weighted_labels_predictions_key = computations[-1].keys[-1]

  def result(
      metrics
  ):
    """Returns mean prediction."""
    metric = metrics[weighted_labels_predictions_key]
    if np.isclose(metric.total_weighted_examples, 0.0):
      value = float('nan')
    else:
      value = metric.total_weighted_predictions / metric.total_weighted_examples
    return {key: value}

  derived_computation = metric_types.DerivedMetricComputation(
      keys=[key], result=result)
  computations.append(derived_computation)
  return computations


class Calibration(metric_types.Metric):
  """Calibration.

  Calibration in this context is defined as the total weighted predictions /
  total weighted labels.
  """

  def __init__(self, name = CALIBRATION_NAME):
    """Initializes calibration.

    Args:
      name: Metric name.
    """
    super(Calibration, self).__init__(
        metric_util.merge_per_key_computations(_calibration), name=name)


metric_types.register_metric(Calibration)


def _calibration(
    name = CALIBRATION_NAME,
    eval_config = None,
    model_name = '',
    output_name = '',
    sub_key = None
):
  """Returns metric computations for calibration."""
  key = metric_types.MetricKey(
      name=name,
      model_name=model_name,
      output_name=output_name,
      sub_key=sub_key)

  # Make sure weighted_labels_predictions_examples are calculated.
  computations = _weighted_labels_predictions_examples(
      eval_config=eval_config,
      model_name=model_name,
      output_name=output_name,
      sub_key=sub_key)
  weighted_labels_predictions_key = computations[-1].keys[-1]

  def result(
      metrics
  ):
    """Returns calibration."""
    metric = metrics[weighted_labels_predictions_key]
    if np.isclose(metric.total_weighted_labels, 0.0):
      value = float('nan')
    else:
      value = metric.total_weighted_predictions / metric.total_weighted_labels

    return {key: value}

  derived_computation = metric_types.DerivedMetricComputation(
      keys=[key], result=result)
  computations.append(derived_computation)
  return computations


def _weighted_labels_predictions_examples(
    name = _WEIGHTED_LABELS_PREDICTIONS_EXAMPLES_NAME,
    eval_config = None,
    model_name = '',
    output_name = '',
    sub_key = None
):
  """Returns metric computations for weighted labels, predictions, and examples.

  Args:
    name: Metric name.
    eval_config: Eval config.
    model_name: Optional model name (if multi-model evaluation).
    output_name: Optional output name (if multi-output model type).
    sub_key: Optional sub key.
  """
  key = metric_types.MetricKey(
      name=name,
      model_name=model_name,
      output_name=output_name,
      sub_key=sub_key)
  return [
      metric_types.MetricComputation(
          keys=[key],
          preprocessor=None,  # Use default
          combiner=_WeightedLabelsPredictionsExamplesCombiner(
              key, eval_config=eval_config))
  ]


class _WeightedLabelsPredictionsExamples(object):
  """Total weighted labels, predictions, and examples."""
  __slots__ = [
      'total_weighted_labels', 'total_weighted_predictions',
      'total_weighted_examples'
  ]

  def __init__(self):
    """Initializes accumulator."""
    self.total_weighted_labels = 0.0
    self.total_weighted_predictions = 0.0
    self.total_weighted_examples = 0.0


class _WeightedLabelsPredictionsExamplesCombiner(beam.CombineFn):
  """Computes weighted labels, predictions, and examples."""

  def __init__(self, key,
               eval_config):
    self._key = key
    self._eval_config = eval_config

  def create_accumulator(self):
    return _WeightedLabelsPredictionsExamples()

  def add_input(
      self, accumulator,
      element
  ):
    label, prediction, example_weight = (
        metric_util.to_label_prediction_example_weight(
            element,
            eval_config=self._eval_config,
            output_name=self._key.output_name,
            sub_key=self._key.sub_key,
            allow_none=True,
            array_size=1))
    if example_weight is None:
      example_weight = 0.0
    else:
      example_weight = float(example_weight)
    accumulator.total_weighted_examples += example_weight
    if label is not None:
      if self._key.sub_key and self._key.sub_key.top_k is not None:
        for i in range(self._key.sub_key.top_k):
          weighted_label = label[i] * example_weight
      else:
        weighted_label = float(label) * example_weight
      accumulator.total_weighted_labels += weighted_label
    if prediction is not None:
      if self._key.sub_key and self._key.sub_key.top_k is not None:
        for i in range(self._key.sub_key.top_k):
          weighted_prediction = prediction[i] * example_weight
      else:
        weighted_prediction = float(prediction) * example_weight
      accumulator.total_weighted_predictions += weighted_prediction
    return accumulator

  def merge_accumulators(
      self, accumulators
  ):
    result = self.create_accumulator()
    for accumulator in accumulators:
      result.total_weighted_labels += accumulator.total_weighted_labels
      result.total_weighted_predictions += (
          accumulator.total_weighted_predictions)
      result.total_weighted_examples += accumulator.total_weighted_examples
    return result

  def extract_output(
      self, accumulator
  ):
    return {self._key: accumulator}
