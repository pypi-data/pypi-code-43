# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Base for all metrics."""
import logging
import numpy as np

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Type, Union

from automl.client.core.common import logging_utilities


class Metric(ABC):
    """Abstract class for all metrics."""

    def __init__(self,
                 logger: Optional[logging.Logger] = None) -> None:
        """Initialize the metric class.

        :logger: Logger to log errors and warnings.
        """
        self._data = {}  # type: Dict[Union[str, int], Any]
        self._logger = logger if logger is not None else logging_utilities.NULL_LOGGER

    @staticmethod
    @abstractmethod
    def aggregate(scores: List[Any]) -> Any:
        """Fold several scores from a computed metric together.

        :param scores: a list of computed scores
        :return: the aggregated scores
        """
        ...

    @staticmethod
    def check_aggregate_scores(scores: List[Any]) -> bool:
        """
        Check that the scores to be aggregated are reasonable.

        :param scores: scores computed by a metric
        :return: an aggregated score of the same shape as each of the inputs
        """
        if len(scores) == 0:
            raise ValueError("Scores must not be empty to aggregate")
        if np.nan in scores:
            return False
        for score in scores:
            if isinstance(score, dict) and NonScalarMetric.is_error_metric(score):
                return False
        return True


class NonScalarMetric(Metric):
    """Abstract class for non-scalar metrics."""

    SCHEMA_TYPE = 'schema_type'
    SCHEMA_VERSION = 'schema_version'
    DATA = 'data'

    ERRORS = 'errors'

    """Abstract class for a metric which produces a nonscalar score."""
    @staticmethod
    def is_error_metric(score: Dict[str, Any]) -> bool:
        """
        Get whether the given score is an error metric.

        :param score: the score to test
        :return: True if the metric errored on computation, otherwise False
        """
        return NonScalarMetric.ERRORS in score

    @staticmethod
    def get_error_metric(message: Optional[str] = None) -> Dict[str, List[str]]:
        """
        Get a dictionary representation of a failed nonscalar metric.

        :param message: the error message that was thrown
        :return: dictionary with the error message
        """
        if message is None:
            message = "Unexpected error occurred while calculating metric"
        return {
            NonScalarMetric.ERRORS: [str(message)]
        }

    @staticmethod
    def _data_to_dict(schema_type, schema_version, data):
        return {
            NonScalarMetric.SCHEMA_TYPE: schema_type,
            NonScalarMetric.SCHEMA_VERSION: schema_version,
            NonScalarMetric.DATA: data
        }


class ScalarMetric(Metric):
    """Abstract class for a metric which produces a scalar score."""

    @staticmethod
    def aggregate(scores: List[Any]) -> float:
        """Fold several scores from a computed metric together."""
        if np.isnan(scores).sum() == len(scores):
            return float(np.nan)
        return float(np.nanmean(scores))
