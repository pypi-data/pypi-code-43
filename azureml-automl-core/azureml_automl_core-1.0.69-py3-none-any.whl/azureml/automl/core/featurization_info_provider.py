# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Base class for objects that provide featurization info."""
from abc import ABC, abstractmethod
from typing import Optional, List

from automl.client.core.common.types import FeaturizationSummaryType


class FeaturizationInfoProvider(ABC):
    """Base class for objects that provide featurization info."""

    @abstractmethod
    def get_engineered_feature_names(self) -> Optional[List[str]]:
        """
        Get the engineered feature names.

        Return the list of engineered feature names as string after data transformations on the
        raw data have been finished.

        :return: The list of engineered fearure names as strings
        """
        raise NotImplementedError

    @abstractmethod
    def get_featurization_summary(self) -> FeaturizationSummaryType:
        """
        Return the featurization summary for all the input features seen by DataTransformer.

        :return: List of featurization summary for each input feature.
        """
        raise NotImplementedError
