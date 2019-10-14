# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Definitions for classification metrics."""
import logging
import numpy as np
import sklearn.metrics

from abc import abstractmethod
from typing import Any, Optional

from automl.client.core.runtime.score import _scoring_utilities, constants, utilities
from automl.client.core.runtime.score._metric_base import Metric, NonScalarMetric, ScalarMetric


class ClassificationMetric(Metric):
    """Abstract class for classification metrics."""

    def __init__(self,
                 y_test: np.ndarray,
                 y_pred_proba: np.ndarray,
                 y_test_bin: np.ndarray,
                 y_pred: np.ndarray,
                 class_labels: np.ndarray,
                 sample_weight: Optional[np.ndarray] = None,
                 logger: Optional[logging.Logger] = None) -> None:
        """
        Initialize the classification metric class.

        :param y_test: True labels for the test set.
        :param y_pred_proba: Predicted probabilities for each sample and class.
        :param y_test_bin: Binarized true labels.
        :param y_pred: The model's predictions.
        :param class_labels: Class labels for the full dataset.
        :param sample_weight: Weighting of each sample in the calculation.
        :param logger: Logger for errors and warnings.
        """
        if y_test.shape[0] != y_pred_proba.shape[0]:
            raise ValueError("Mismatched input shapes: y_test={}, y_pred={}"
                             .format(y_test.shape, y_pred.shape))

        self._y_test = y_test
        self._y_pred_proba = y_pred_proba
        self._y_test_bin = y_test_bin
        self._y_pred = y_pred
        self._test_labels = np.unique(y_test)
        self._class_labels = class_labels
        self._sample_weight = sample_weight

        super().__init__(logger=logger)

    @abstractmethod
    def compute(self) -> Any:
        """Compute the metric."""
        ...


class Accuracy(ClassificationMetric, ScalarMetric):
    """Wrapper class for accuracy."""

    def compute(self):
        """Compute the score for the metric."""
        return sklearn.metrics.accuracy_score(y_true=self._y_test, y_pred=self._y_pred,
                                              sample_weight=self._sample_weight)


class WeightedAccuracy(ClassificationMetric, ScalarMetric):
    """Accuracy weighted by number of elements for each class."""

    def compute(self):
        """Compute the score for the metric."""
        updated_weights = np.ones(self._y_test.shape[0])
        for idx, i in enumerate(np.bincount(self._y_test.ravel())):
            updated_weights[self._y_test.ravel() == idx] *= (i / float(self._y_test.ravel().shape[0]))

        return sklearn.metrics.accuracy_score(y_true=self._y_test, y_pred=self._y_pred,
                                              sample_weight=updated_weights)


class BalancedAccuracy(ClassificationMetric, ScalarMetric):
    """Wrapper class for balanced accuracy."""

    def compute(self):
        """Compute the score for the metric."""
        average_modifier = 'macro'
        return sklearn.metrics.recall_score(y_true=self._y_test, y_pred=self._y_pred,
                                            average=average_modifier,
                                            sample_weight=self._sample_weight)


class NormMacroRecall(ClassificationMetric, ScalarMetric):
    """
    Normalized macro averaged recall metric.

    https://github.com/ch-imad/AutoMl_Challenge/blob/2353ec0/Starting_kit/scoring_program/libscores.py#L187
    For the AutoML challenge
    https://competitions.codalab.org/competitions/2321#learn_the_details-evaluation
    This is a normalized macro averaged recall, rather than accuracy
    https://github.com/scikit-learn/scikit-learn/issues/6747#issuecomment-217587210
    Random performance is 0.0 perfect performance is 1.0
    """

    def _norm_macro_recall_wrapper(self, y_true, y_score, test_class_labels, class_labels, logger,
                                   metric_name, average=None, **kwargs):
        return _scoring_utilities.class_averaged_score(
            self._norm_macro_recall, y_true=y_true, y_score=y_score,
            test_class_labels=test_class_labels, class_labels=class_labels,
            average=average, logger=logger, metric_name=metric_name, **kwargs)

    def _norm_macro_recall(self, y_true, y_pred, num_classes, logger=None, **kwargs):
        # need to use the actual prediction not the matrix here but need
        # the matrix passed to utilities.class_averaged_score
        # if we start doing calibration we need to change this
        BINARY_CUTOFF = .5
        R = 1 / num_classes
        if y_true.shape[1] > 1:
            y_true = np.argmax(y_true, 1)

        y_pred_proba = np.array(y_pred > BINARY_CUTOFF, dtype=int) if y_pred.ndim == 1 else np.argmax(y_pred, 1)
        cmat = sklearn.metrics.confusion_matrix(y_true=y_true, y_pred=y_pred_proba,
                                                sample_weight=kwargs.get('sample_weight'))
        if isinstance(cmat, float):
            return constants.DEFAULT_PIPELINE_SCORE
        else:
            cms = cmat.sum(axis=1)
            if cms.sum() == 0:
                return constants.DEFAULT_PIPELINE_SCORE
            else:
                return max(0.0, (np.mean(cmat.diagonal() / cmat.sum(axis=1)) - R) / (1 - R))

    def compute(self):
        """Compute the score for the metric."""
        y_pred_proba = self._y_pred_proba[:, 1] if self._class_labels.shape[0] == 2 else self._y_pred_proba
        return self._norm_macro_recall_wrapper(self._y_test_bin, y_pred_proba, self._test_labels, self._class_labels,
                                               self._logger, constants.NORM_MACRO_RECALL,
                                               sample_weight=self._sample_weight)


class LogLoss(ClassificationMetric, ScalarMetric):
    """Wrapper class for log loss."""

    def compute(self):
        """Compute the score for the metric."""
        y_pred_proba = self._y_pred_proba[:, 1] if self._class_labels.shape[0] == 2 else self._y_pred_proba
        return sklearn.metrics.log_loss(y_true=self._y_test, y_pred=y_pred_proba,
                                        labels=self._class_labels,
                                        sample_weight=self._sample_weight)


class F1(ClassificationMetric, ScalarMetric):
    """Wrapper class for recall."""

    def compute(self):
        """Compute the score for the metric."""
        return sklearn.metrics.f1_score(y_true=self._y_test, y_pred=self._y_pred,
                                        average=self._average_type, sample_weight=self._sample_weight)


class F1Macro(F1):
    """Wrapper class for macro-averaged F1 score."""

    def __init__(self, *args, **kwargs):
        """Initialize F1Macro."""
        self._average_type = 'macro'
        super().__init__(*args, **kwargs)


class F1Micro(F1):
    """Wrapper class for micro-averaged F1 score."""

    def __init__(self, *args, **kwargs):
        """Initialize F1Micro."""
        self._average_type = 'micro'
        super().__init__(*args, **kwargs)


class F1Weighted(F1):
    """Wrapper class for weighted-averaged F1 score."""

    def __init__(self, *args, **kwargs):
        """Initialize F1Weighted."""
        self._average_type = 'weighted'
        super().__init__(*args, **kwargs)


class Precision(ClassificationMetric, ScalarMetric):
    """Wrapper class for precision."""

    def compute(self):
        """Compute the score for the metric."""
        return sklearn.metrics.precision_score(y_true=self._y_test, y_pred=self._y_pred,
                                               average=self._average_type, sample_weight=self._sample_weight)


class PrecisionMacro(Precision):
    """Wrapper class for macro-averaged precision."""

    def __init__(self, *args, **kwargs):
        """Initialize PrecisionMacro."""
        self._average_type = 'macro'
        super().__init__(*args, **kwargs)


class PrecisionMicro(Precision):
    """Wrapper class for micro-averaged precision."""

    def __init__(self, *args, **kwargs):
        """Initialize PrecisionMicro."""
        self._average_type = 'micro'
        super().__init__(*args, **kwargs)


class PrecisionWeighted(Precision):
    """Wrapper class for weighted-averaged precision."""

    def __init__(self, *args, **kwargs):
        """Initialize PrecisionWeighted."""
        self._average_type = 'weighted'
        super().__init__(*args, **kwargs)


class Recall(ClassificationMetric, ScalarMetric):
    """Wrapper class for recall."""

    def compute(self):
        """Compute the score for the metric."""
        return sklearn.metrics.recall_score(y_true=self._y_test, y_pred=self._y_pred,
                                            average=self._average_type, sample_weight=self._sample_weight)


class RecallMacro(Recall):
    """Wrapper class for macro-averaged recall."""

    def __init__(self, *args, **kwargs):
        """Initialize RecallMacro."""
        self._average_type = 'macro'
        super().__init__(*args, **kwargs)


class RecallMicro(Recall):
    """Wrapper class for micro-averaged recall."""

    def __init__(self, *args, **kwargs):
        """Initialize RecallMicro."""
        self._average_type = 'micro'
        super().__init__(*args, **kwargs)


class RecallWeighted(Recall):
    """Wrapper class for weighted-averaged recall."""

    def __init__(self, *args, **kwargs):
        """Initialize RecallWeighted."""
        self._average_type = 'weighted'
        super().__init__(*args, **kwargs)


class AveragePrecision(ClassificationMetric, ScalarMetric):
    """Wrapper class for average precision."""

    def compute(self):
        """Compute the score for the metric."""
        y_pred_proba = self._y_pred_proba[:, 1] if self._class_labels.shape[0] == 2 else self._y_pred_proba
        return _scoring_utilities.class_averaged_score(
            sklearn.metrics.average_precision_score,
            y_true=self._y_test_bin, y_score=y_pred_proba,
            test_class_labels=self._test_labels, class_labels=self._class_labels,
            average=self._average_type, logger=self._logger,
            metric_name=self._name, sample_weight=self._sample_weight)


class AveragePrecisionMacro(AveragePrecision):
    """Wrapper class for macro-averaged average precision."""

    def __init__(self, *args, **kwargs):
        """Initialize AveragePrecisionMacro."""
        self._average_type = 'macro'
        self._name = constants.AVERAGE_PRECISION_MACRO
        super().__init__(*args, **kwargs)


class AveragePrecisionMicro(AveragePrecision):
    """Wrapper class for micro-averaged average precision."""

    def __init__(self, *args, **kwargs):
        """Initialize AveragePrecisionMicro."""
        self._average_type = 'micro'
        self._name = constants.AVERAGE_PRECISION_MICRO
        super().__init__(*args, **kwargs)


class AveragePrecisionWeighted(AveragePrecision):
    """Wrapper class for weighted-averaged average precision."""

    def __init__(self, *args, **kwargs):
        """Initialize AveragePrecisionWeighted."""
        self._average_type = 'weighted'
        self._name = constants.AVERAGE_PRECISION_WEIGHTED
        super().__init__(*args, **kwargs)


class AUC(ClassificationMetric, ScalarMetric):
    """Wrapper class for AUC (area under the ROC curve)."""

    def compute(self):
        """Compute the score for the metric."""
        y_pred_proba = self._y_pred_proba[:, 1] if self._class_labels.shape[0] == 2 else self._y_pred_proba
        return _scoring_utilities.class_averaged_score(
            sklearn.metrics.roc_auc_score,
            y_true=self._y_test_bin, y_score=y_pred_proba,
            test_class_labels=self._test_labels, class_labels=self._class_labels,
            average=self._average_type, logger=self._logger,
            metric_name=self._name, sample_weight=self._sample_weight)


class AUCMacro(AUC):
    """Wrapper class for macro-averaged AUC."""

    def __init__(self, *args, **kwargs):
        """Initialize AUCMacro."""
        self._average_type = 'macro'
        self._name = constants.AUC_MACRO
        super().__init__(*args, **kwargs)


class AUCMicro(AUC):
    """Wrapper class for micro-averaged AUC."""

    def __init__(self, *args, **kwargs):
        """Initialize AUCMicro."""
        self._average_type = 'micro'
        self._name = constants.AUC_MICRO
        super().__init__(*args, **kwargs)


class AUCWeighted(AUC):
    """Wrapper class for weighted-averaged AUC."""

    def __init__(self, *args, **kwargs):
        """Initialize AUCWeighted."""
        self._average_type = 'weighted'
        self._name = constants.AUC_WEIGHTED
        super().__init__(*args, **kwargs)


class AccuracyTable(ClassificationMetric, NonScalarMetric):
    """
    Accuracy Table Metric.

    The accuracy table metric is a multi-use non-scalar metric
    that can be used to produce multiple types of line charts
    that vary continuously over the space of predicted probabilities.
    Examples of these charts are receiver operating characteristic,
    precision-recall, and lift curves.

    The calculation of the accuracy table is similar to the calculation
    of a receiver operating characteristic curve. A receiver operating
    characteristic curve stores true positive rates and
    false positive rates at many different probability thresholds.
    The accuracy table stores the raw number of
    true positives, false positives, true negatives, and false negatives
    at many probability thresholds.

    Probability thresholds are evenly spaced thresholds between 0 and 1.
    If NUM_POINTS were 5 the probability thresholds would be
    [0.0, 0.25, 0.5, 0.75, 1.0].
    These thresholds are useful for computing charts where you want to
    sample evenly over the space of predicted probabilities.

    Percentile thresholds are spaced according to the distribution of
    predicted probabilities. Each threshold corresponds to the percentile
    of the data at a probability threshold.
    For example, if NUM_POINTS were 5, then the first threshold would be at
    the 0th percentile, the second at the 25th percentile, the
    third at the 50th, and so on.

    The probability tables and percentile tables are both 3D lists where
    the first dimension represents the class label*, the second dimension
    represents the sample at one threshold (scales with NUM_POINTS),
    and the third dimension always has 4 values: TP, FP, TN, FN, and
    always in that order.

    * The confusion values (TP, FP, TN, FN) are computed with the
    one vs. rest strategy. See the following link for more details:
    `https://en.wikipedia.org/wiki/Multiclass_classification`
    """

    SCHEMA_TYPE = constants.SCHEMA_TYPE_ACCURACY_TABLE
    SCHEMA_VERSION = '1.0.1'

    NUM_POINTS = 100

    PROB_TABLES = 'probability_tables'
    PERC_TABLES = 'percentile_tables'
    PROB_THOLDS = 'probability_thresholds'
    PERC_THOLDS = 'percentile_thresholds'
    CLASS_LABELS = 'class_labels'

    @staticmethod
    def _data_to_dict(data):
        schema_type = AccuracyTable.SCHEMA_TYPE
        schema_version = AccuracyTable.SCHEMA_VERSION
        return NonScalarMetric._data_to_dict(schema_type, schema_version, data)

    def _make_thresholds(self):
        probability_thresholds = np.linspace(0, 1, AccuracyTable.NUM_POINTS)
        all_predictions = self._y_pred_proba.ravel()
        percentile_thresholds = np.percentile(all_predictions, probability_thresholds * 100)
        return probability_thresholds, percentile_thresholds

    def _build_tables(self, class_labels, thresholds):
        """
        Create the accuracy table per class.

        Sweeps the thresholds to find accuracy data over the space of
        predicted probabilities.
        """
        y_test_bin = self._y_test_bin
        if y_test_bin.shape[1] == 1:
            y_test_bin = np.concatenate((1 - y_test_bin, y_test_bin), axis=1)
        data = zip(y_test_bin.T, self._y_pred_proba.T)
        tables = [self._build_table(tbin, pred, thresholds) for tbin, pred in data]
        full_tables = self._pad_tables(class_labels, tables)
        return full_tables

    def _pad_tables(self, class_labels, tables):
        """Add padding tables for missing validation classes."""
        y_labels = np.unique(self._y_test)
        full_tables = []
        table_index = 0
        for class_label in class_labels:
            if class_label in y_labels:
                full_tables.append(tables[table_index])
                table_index += 1
            else:
                full_tables.append(np.zeros((AccuracyTable.NUM_POINTS, 4), dtype=int))
        return full_tables

    def _build_table(self, class_y_test_bin, class_y_pred_proba, thresholds):
        """Calculate the confusion values at all thresholds for one class."""
        table = []
        n_positive = np.sum(class_y_test_bin)
        n_samples = class_y_test_bin.shape[0]
        for threshold in thresholds:
            under_threshold = class_y_test_bin[class_y_pred_proba < threshold]
            fn = np.sum(under_threshold)
            tn = under_threshold.shape[0] - fn
            tp, fp = n_positive - fn, n_samples - n_positive - tn
            conf_values = np.array([tp, fp, tn, fn], dtype=int)
            table.append(conf_values)
        return table

    def compute(self):
        """Compute the score for the metric."""
        probability_thresholds, percentile_thresholds = self._make_thresholds()
        probability_tables = self._build_tables(self._class_labels, probability_thresholds)
        percentile_tables = self._build_tables(self._class_labels, percentile_thresholds)

        string_labels = [str(label) for label in self._class_labels]
        self._data[AccuracyTable.CLASS_LABELS] = string_labels
        self._data[AccuracyTable.PROB_TABLES] = probability_tables
        self._data[AccuracyTable.PERC_TABLES] = percentile_tables
        self._data[AccuracyTable.PROB_THOLDS] = probability_thresholds
        self._data[AccuracyTable.PERC_THOLDS] = percentile_thresholds
        ret = AccuracyTable._data_to_dict(self._data)
        return _scoring_utilities.make_json_safe(ret)

    @staticmethod
    def aggregate(scores):
        """Fold several scores from a computed metric together.

        :param scores: a list of computed scores
        :return: the aggregated scores
        """
        if not Metric.check_aggregate_scores(scores):
            return NonScalarMetric.get_error_metric()

        score_data = [score[NonScalarMetric.DATA] for score in scores]
        prob_tables = [d[AccuracyTable.PROB_TABLES] for d in score_data]
        perc_tables = [d[AccuracyTable.PERC_TABLES] for d in score_data]
        data_agg = {
            AccuracyTable.PROB_TABLES: (
                np.sum(prob_tables, axis=0)),
            AccuracyTable.PERC_TABLES: (
                np.sum(perc_tables, axis=0)),
            AccuracyTable.PROB_THOLDS: (
                score_data[0][AccuracyTable.PROB_THOLDS]),
            AccuracyTable.PERC_THOLDS: (
                score_data[0][AccuracyTable.PERC_THOLDS]),
            AccuracyTable.CLASS_LABELS: (
                score_data[0][AccuracyTable.CLASS_LABELS])
        }
        ret = AccuracyTable._data_to_dict(data_agg)
        return _scoring_utilities.make_json_safe(ret)


class ConfusionMatrix(ClassificationMetric, NonScalarMetric):
    """
    Confusion Matrix Metric.

    This metric is a wrapper around the sklearn confusion matrix.
    The metric data contains the class labels and a 2D list
    for the matrix itself.
    See the following link for more details on how the metric is computed:
    `https://scikit-learn.org/stable/modules/generated/sklearn.metrics.confusion_matrix.html`
    """

    SCHEMA_TYPE = constants.SCHEMA_TYPE_CONFUSION_MATRIX
    SCHEMA_VERSION = '1.0.0'

    MATRIX = 'matrix'
    CLASS_LABELS = 'class_labels'

    @staticmethod
    def _data_to_dict(data):
        schema_type = ConfusionMatrix.SCHEMA_TYPE
        schema_version = ConfusionMatrix.SCHEMA_VERSION
        return NonScalarMetric._data_to_dict(schema_type, schema_version, data)

    def _compute_matrix(self, class_labels, sample_weight=None):
        """Compute the matrix from prediction data."""
        y_pred_indexes = np.argmax(self._y_pred_proba, axis=1)
        y_pred_labels = class_labels[y_pred_indexes]
        y_true = self._y_test

        if y_pred_labels.dtype.kind == 'f':
            class_labels = class_labels.astype(str)
            y_true = y_true.astype(str)
            y_pred_labels = y_pred_labels.astype(str)

        return sklearn.metrics.confusion_matrix(y_true=y_true,
                                                y_pred=y_pred_labels,
                                                sample_weight=sample_weight,
                                                labels=class_labels)

    def compute(self):
        """Compute the score for the metric."""
        string_labels = [str(label) for label in self._class_labels]
        self._data[ConfusionMatrix.CLASS_LABELS] = string_labels
        matrix = self._compute_matrix(self._class_labels,
                                      sample_weight=self._sample_weight)
        self._data[ConfusionMatrix.MATRIX] = matrix
        ret = ConfusionMatrix._data_to_dict(self._data)
        return _scoring_utilities.make_json_safe(ret)

    @staticmethod
    def aggregate(scores):
        """Folds several scores from a computed metric together.

        :param scores: a list of computed scores
        :return: the aggregated scores
        """
        if not Metric.check_aggregate_scores(scores):
            return NonScalarMetric.get_error_metric()

        score_data = [score[NonScalarMetric.DATA] for score in scores]
        matrices = [d[ConfusionMatrix.MATRIX] for d in score_data]
        matrix_sum = np.sum(matrices, axis=0)
        agg_class_labels = score_data[0][ConfusionMatrix.CLASS_LABELS]
        data_agg = {
            ConfusionMatrix.CLASS_LABELS: agg_class_labels,
            ConfusionMatrix.MATRIX: matrix_sum
        }
        ret = ConfusionMatrix._data_to_dict(data_agg)
        return _scoring_utilities.make_json_safe(ret)
