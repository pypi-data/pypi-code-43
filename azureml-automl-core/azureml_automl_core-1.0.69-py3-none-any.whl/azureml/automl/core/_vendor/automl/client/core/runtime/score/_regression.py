# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Definitions for regression metrics."""
import logging
import numpy as np
import scipy.stats
import sklearn.metrics

from abc import abstractmethod
from typing import Any, Dict, Optional

from automl.client.core.runtime.score import _scoring_utilities, constants, utilities
from automl.client.core.runtime.score._metric_base import Metric, NonScalarMetric, ScalarMetric


class RegressionMetric(Metric):
    """Abstract class for regression metrics."""

    def __init__(self,
                 y_test: np.ndarray,
                 y_pred: np.ndarray,
                 y_min: Optional[float] = None,
                 y_max: Optional[float] = None,
                 y_std: Optional[float] = None,
                 bin_info: Optional[Dict[str, float]] = None,
                 sample_weight: Optional[np.ndarray] = None,
                 logger: Optional[logging.Logger] = None) -> None:
        """
        Initialize the regression metric class.

        :param y_test: True labels for the test set.
        :param y_pred: Predictions for each sample.
        :param y_min: Minimum target value.
        :param y_max: Maximum target value.
        :param y_std: Standard deviation of the targets.
        :param bin_info: Metadata about the dataset (required for nonscalar metrics).
        :param sample_weight: Weighting of each sample in the calculation.
        :param logger: Logger for errors and warnings.
        """
        if y_test.shape[0] != y_pred.shape[0]:
            raise ValueError("Mismatched input shapes: y_test={}, y_pred={}"
                             .format(y_test.shape, y_pred.shape))
        self._y_test = y_test
        self._y_pred = y_pred
        self._y_min = y_min
        self._y_max = y_max
        self._y_std = y_std
        self._bin_info = bin_info
        self._sample_weight = sample_weight

        # Compute if there are negative values for logarithmic metrics
        self._has_negatives = (y_test < 0).any() or (y_pred < 0).any()

        super().__init__(logger=logger)

    @abstractmethod
    def compute(self) -> Any:
        """Compute the score for the metric."""
        ...


class ExplainedVariance(RegressionMetric, ScalarMetric):
    """Wrapper class for explained variance."""

    def compute(self):
        """Compute the score for the metric."""
        return sklearn.metrics.explained_variance_score(self._y_test, self._y_pred,
                                                        sample_weight=self._sample_weight,
                                                        multioutput='uniform_average')


class R2(RegressionMetric, ScalarMetric):
    """Wrapper class for R^2."""

    def compute(self):
        """Compute the score for the metric."""
        ret = sklearn.metrics.r2_score(self._y_test, self._y_pred,
                                       sample_weight=self._sample_weight,
                                       multioutput='uniform_average')
        return np.clip(ret, constants.CLIPS_NEGATIVE[constants.R2_SCORE], 1.0)


class Spearman(RegressionMetric, ScalarMetric):
    """Wrapper class for spearman correlation."""

    def compute(self):
        """Compute the score for the metric."""
        worst_spearman = utilities.get_worst_values(constants.REGRESSION)[constants.SPEARMAN]
        if np.unique(self._y_test).shape[0] == 1:
            self._logger.warning("Failed to compute spearman correlation because all targets were equal.")
            return worst_spearman

        if np.unique(self._y_pred).shape[0] == 1:
            self._logger.warning("Failed to compute spearman correlation because all predictions were equal.")
            return worst_spearman

        return scipy.stats.spearmanr(self._y_test, self._y_pred)[0]


class MAPE(RegressionMetric, ScalarMetric):
    """Wrapper class for MAPE."""

    def compute(self):
        """Compute the score for the metric."""
        return _mape(y_true=self._y_test, y_pred=self._y_pred, logger=self._logger)


class MeanAbsoluteError(RegressionMetric, ScalarMetric):
    """Wrapper class for mean absolute error."""

    def compute(self):
        """Compute the score for the metric."""
        return sklearn.metrics.mean_absolute_error(self._y_test, self._y_pred,
                                                   sample_weight=self._sample_weight,
                                                   multioutput='uniform_average')


class NormMeanAbsoluteError(RegressionMetric, ScalarMetric):
    """Wrapper class for normalized mean absolute error."""

    def compute(self):
        """Compute the score for the metric."""
        ret = sklearn.metrics.mean_absolute_error(
            self._y_test, self._y_pred,
            sample_weight=self._sample_weight, multioutput='uniform_average')
        return ret / np.abs(self._y_max - self._y_min)


class MedianAbsoluteError(RegressionMetric, ScalarMetric):
    """Wrapper class for median absolute error."""

    def compute(self):
        """Compute the score for the metric."""
        return sklearn.metrics.median_absolute_error(self._y_test, self._y_pred)


class NormMedianAbsoluteError(RegressionMetric, ScalarMetric):
    """Wrapper class for normalized median absolute error."""

    def compute(self):
        """Compute the score for the metric."""
        ret = sklearn.metrics.median_absolute_error(self._y_test, self._y_pred)
        return ret / np.abs(self._y_max - self._y_min)


class RMSE(RegressionMetric, ScalarMetric):
    """Wrapper class for root mean squared error."""

    def compute(self):
        """Compute the score for the metric."""
        return np.sqrt(sklearn.metrics.mean_squared_error(
            self._y_test, self._y_pred, sample_weight=self._sample_weight,
            multioutput='uniform_average'))


class NormRMSE(RegressionMetric, ScalarMetric):
    """Wrapper class for normalized root mean squared error."""

    def compute(self):
        """Compute the score for the metric."""
        ret = np.sqrt(sklearn.metrics.mean_squared_error(
            self._y_test, self._y_pred, sample_weight=self._sample_weight,
            multioutput='uniform_average'))
        ret = ret / np.abs(self._y_max - self._y_min)
        return np.clip(ret, 0, constants.CLIPS_POSITIVE.get(constants.NORM_RMSE, 100))


class RMSLE(RegressionMetric, ScalarMetric):
    """Wrapper class for root mean squared log error."""

    def compute(self):
        """Compute the score for the metric."""
        if self._has_negatives:
            self._logger.warning('Skipping NormRMSLE calculation since y_test/y_pred contains negative values.')
            return np.nan

        ret = np.sqrt(sklearn.metrics.mean_squared_log_error(
            self._y_test, self._y_pred, sample_weight=self._sample_weight,
            multioutput='uniform_average'))
        return np.clip(ret, 0, constants.CLIPS_POSITIVE.get(constants.RMSLE, 100))


class NormRMSLE(RegressionMetric, ScalarMetric):
    """Wrapper class for normalized root mean squared log error."""

    def compute(self):
        """Compute the score for the metric."""
        if self._has_negatives:
            self._logger.warning('Skipping NormRMSLE calculation since y_test/y_pred contains negative values.')
            return np.nan

        ret = np.sqrt(sklearn.metrics.mean_squared_log_error(
            self._y_test, self._y_pred, sample_weight=self._sample_weight,
            multioutput='uniform_average'))
        ret = ret / np.abs(np.log1p(self._y_max) - np.log1p(self._y_min))
        return np.clip(ret, 0, constants.CLIPS_POSITIVE.get(constants.NORM_RMSLE, 100))


class Residuals(RegressionMetric, NonScalarMetric):
    """
    Residuals Metric.

    This metric contains the data needed to display a histogram of
    residuals for a regression task.
    The residuals are predicted - actual.

    The bounds of this histogram are determined by the standard
    deviation of the targets for the full dataset. This value is
    passed to the metrics module as y_std. This is why y_std is
    required to compute this metric.
    The first and last bins are not necessarily the same width as
    the other bins. The first bin is [y_min, -2 * y_std].
    The last bin is [2 * y_std, y_max].
    If the regressor performs fairly well most of the residuals will
    be around zero and less than the standard deviation of the original
    data.

    The internal edges are evenly spaced.
    """

    SCHEMA_TYPE = constants.SCHEMA_TYPE_RESIDUALS
    SCHEMA_VERSION = '1.0.0'

    EDGES = 'bin_edges'
    COUNTS = 'bin_counts'
    MEAN = 'mean'
    STDDEV = 'stddev'
    RES_COUNT = 'res_count'

    @staticmethod
    def _data_to_dict(data):
        schema_type = Residuals.SCHEMA_TYPE
        schema_version = Residuals.SCHEMA_VERSION
        return NonScalarMetric._data_to_dict(schema_type, schema_version, data)

    def compute(self):
        """Compute the metric score."""
        if self._y_std is None:
            raise ValueError("y_std required to compute Residuals")

        num_bins = 10
        # If full dataset targets are all zero we still need a bin
        y_std = self._y_std if self._y_std != 0 else 1
        residuals = self._y_pred - self._y_test

        mean = np.mean(residuals)
        stddev = np.std(residuals)
        res_count = len(residuals)

        counts, edges = Residuals._hist_by_bound(residuals, 2 * y_std, num_bins)
        Residuals._simplify_edges(residuals, edges)

        self._data[Residuals.EDGES] = edges
        self._data[Residuals.COUNTS] = counts
        self._data[Residuals.MEAN] = mean
        self._data[Residuals.STDDEV] = stddev
        self._data[Residuals.RES_COUNT] = res_count
        ret = Residuals._data_to_dict(self._data)
        return _scoring_utilities.make_json_safe(ret)

    @staticmethod
    def _hist_by_bound(values, bound, num_bins):
        # Need to subtract one because num_bins needs (num_bins + 1) edges, but we also have inf/-inf.
        num_edges = num_bins - 1
        min_decimal_places = 2

        bound = abs(bound)
        num_bound_decimal_places = int(max(min_decimal_places, -1 * np.log10(bound) + (min_decimal_places + 1)))
        bound = np.ceil(bound * (10 ** num_bound_decimal_places)) / (10 ** num_bound_decimal_places)

        bin_size = bound / num_edges
        bin_edges = np.linspace(-bound, bound, num_edges)
        num_decimal_places = int(max(min_decimal_places, -1 * np.log10(bin_size) + (min_decimal_places + 1)))
        for i, edge in enumerate(bin_edges):
            bin_edges[i] = np.around(edge, decimals=num_decimal_places)
        bins = np.r_[-np.inf, bin_edges, np.inf]
        return np.histogram(values, bins=bins)

    @staticmethod
    def _simplify_edges(residuals, edges):
        """Set the first and last edges of the histogram to be real numbers.

        If the minimum residual is in the outlier bin then the left
        edge is set to that residual value. Otherwise, the left edge
        is set to be evenly spaced with the rest of the bins
        This is repeated on the right side of the histogram.
        """
        assert(len(edges) >= 4)
        min_residual = np.min(residuals)

        # Keep left edge greater than negative infinity
        if min_residual < edges[1]:
            edges[0] = min_residual
        else:
            edges[0] = edges[1] - np.abs(edges[2] - edges[1])

        # Keep right edge less than infinity
        max_residual = np.max(residuals)
        if max_residual >= edges[-2]:
            edges[-1] = max_residual
        else:
            edges[-1] = edges[-2] + np.abs(edges[-2] - edges[-3])

    @staticmethod
    def aggregate(scores):
        """Fold several scores from a computed metric together.

        :param scores: a list of computed scores
        :return: the aggregated scores
        """
        if not Metric.check_aggregate_scores(scores):
            return NonScalarMetric.get_error_metric()

        score_data = [score[NonScalarMetric.DATA] for score in scores]
        edges = [d[Residuals.EDGES] for d in score_data]
        counts = [d[Residuals.COUNTS] for d in score_data]
        agg_edges = Residuals._aggregate_edges(edges)
        agg_counts = np.sum(counts, axis=0)

        means = np.array([d[Residuals.MEAN] for d in score_data])
        res_counts = np.array([d[Residuals.RES_COUNT] for d in score_data])
        stddevs = np.array([d[Residuals.STDDEV] for d in score_data])
        variances = stddevs ** 2

        agg_res_count = np.sum(res_counts)
        agg_mean = np.sum(means * res_counts) / agg_res_count
        agg_stddev = np.sqrt(_scoring_utilities.total_variance(res_counts, means, variances))
        data_agg = {
            Residuals.EDGES: agg_edges,
            Residuals.COUNTS: agg_counts,
            Residuals.MEAN: agg_mean,
            Residuals.STDDEV: agg_stddev,
            Residuals.RES_COUNT: agg_res_count,
        }
        ret = Residuals._data_to_dict(data_agg)
        return _scoring_utilities.make_json_safe(ret)

    @staticmethod
    def _aggregate_edges(all_edges):
        all_edges_arr = np.array(all_edges)
        ret = np.copy(all_edges_arr[0])
        ret[0] = np.min(all_edges_arr[:, 0])
        ret[-1] = np.max(all_edges_arr[:, -1])
        return ret.tolist()


class PredictedTrue(RegressionMetric, NonScalarMetric):
    """
    Predicted vs True Metric.

    This metric can be used to compare the distributions of true
    target values to the distribution of predicted values.

    The predictions are binned and standard deviations are calculated
    for error bars on a line chart.
    """

    SCHEMA_TYPE = constants.SCHEMA_TYPE_PREDICTIONS
    SCHEMA_VERSION = '1.0.0'

    EDGES = 'bin_edges'
    COUNTS = 'bin_counts'
    MEANS = 'bin_averages'
    STDEVS = 'bin_errors'

    @staticmethod
    def _data_to_dict(data):
        schema_type = PredictedTrue.SCHEMA_TYPE
        schema_version = PredictedTrue.SCHEMA_VERSION
        return NonScalarMetric._data_to_dict(schema_type, schema_version, data)

    def compute(self):
        """Compute the metric score."""
        if self._bin_info is None:
            raise ValueError("bin_info is required to \
                             compute PredictedTrue")

        n_bins = self._bin_info['number_of_bins']
        bin_starts = self._bin_info['bin_starts']
        bin_ends = self._bin_info['bin_ends']
        bin_edges = np.r_[bin_starts, bin_ends[-1]]
        # As long as we guarantee all points fit in the edges of bin_info
        # we can use np.digitize only on the ends.
        bin_indices = np.digitize(self._y_test, bin_ends, right=True)

        bin_counts = []
        bin_means = []
        bin_stdevs = []
        for bin_index in range(n_bins):
            y_pred_in_bin = self._y_pred[np.where(bin_indices == bin_index)]
            bin_count = y_pred_in_bin.shape[0]
            bin_counts.append(bin_count)
            if bin_count == 0:
                bin_means.append(0)
                bin_stdevs.append(0)
            else:
                bin_means.append(y_pred_in_bin.mean())
                bin_stdevs.append(y_pred_in_bin.std())

        self._data[PredictedTrue.EDGES] = bin_edges
        self._data[PredictedTrue.COUNTS] = np.array(bin_counts, dtype=int)
        self._data[PredictedTrue.MEANS] = np.array(bin_means)
        self._data[PredictedTrue.STDEVS] = np.array(bin_stdevs)

        ret = PredictedTrue._data_to_dict(self._data)
        return _scoring_utilities.make_json_safe(ret)

    @staticmethod
    def aggregate(scores):
        """Fold several scores from a computed metric together.

        :param scores: a list of computed scores
        :return: the aggregated scores
        """
        if not Metric.check_aggregate_scores(scores):
            return NonScalarMetric.get_error_metric()

        EDGES = PredictedTrue.EDGES
        COUNTS = PredictedTrue.COUNTS
        MEANS = PredictedTrue.MEANS
        STDEVS = PredictedTrue.STDEVS

        score_data = [score[NonScalarMetric.DATA] for score in scores]

        n_bins = len(score_data[0][COUNTS])

        bin_counts = []
        bin_means = []
        bin_stdevs = []
        for bin_index in range(n_bins):
            split_counts = np.array([d[COUNTS][bin_index] for d in score_data])
            split_means = np.array([d[MEANS][bin_index] for d in score_data])
            split_stdevs = np.array([d[STDEVS][bin_index] for d in score_data])

            bin_count = np.sum(split_counts)
            bin_counts.append(bin_count)
            if bin_count == 0:
                bin_means.append(0)
                bin_stdevs.append(0)
            else:
                bin_mean = np.sum(split_counts * split_means) / bin_count
                bin_means.append(bin_mean)
                split_vars = split_stdevs ** 2
                bin_var = _scoring_utilities.total_variance(
                    split_counts, split_means, split_vars)
                bin_stdevs.append(bin_var ** 0.5)

        data_agg = {
            EDGES: score_data[0][EDGES],
            COUNTS: np.array(bin_counts, dtype=int),
            MEANS: np.array(bin_means),
            STDEVS: np.array(bin_stdevs)
        }

        ret = PredictedTrue._data_to_dict(data_agg)
        return _scoring_utilities.make_json_safe(ret)


def _mape(y_true: np.ndarray,
          y_pred: np.ndarray,
          logger: logging.Logger) -> np.float64:
    """
    Calcualte the mean absolute precentage error.

    We remove NA and values where actual is close to zero to keep score from approaching inf.
    """
    not_na = ~(np.isnan(y_true))
    not_zero = ~np.isclose(y_true, 0.0)
    safe = not_na & not_zero

    y_true_safe = y_true[safe]
    y_pred_safe = y_pred[safe]

    if len(y_true_safe) < 1:
        logger.warning('Skipping MAPE calculation since there not enough non-zero, non-nan values.')
        return np.nan
    ape = 100 * np.abs((y_true_safe - y_pred_safe) / y_true_safe)

    return np.mean(ape)
