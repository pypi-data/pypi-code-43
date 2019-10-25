# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Container for generic featurizers."""
from typing import Any

from nimbusml.preprocessing.missing_values import Handler as NimbusMLMissingValuesHandler
from nimbusml.preprocessing.schema import ColumnSelector as NimbusMLColumnSelector
from sklearn.cluster import MiniBatchKMeans
from sklearn.preprocessing import Imputer, MaxAbsScaler

from automl.client.core.common import constants
from .imputation_marker import ImputationMarker
from .lambda_transformer import LambdaTransformer


class GenericFeaturizers:
    """Container for generic featurizers."""

    @classmethod
    def imputation_marker(cls, *args: Any, **kwargs: Any) -> ImputationMarker:
        """Create imputation marker."""
        return ImputationMarker(*args, **kwargs)

    @classmethod
    def lambda_featurizer(cls, *args: Any, **kwargs: Any) -> LambdaTransformer:
        """Create lambda featurizer."""
        return LambdaTransformer(*args, **kwargs)

    @classmethod
    def imputer(cls, *args: Any, **kwargs: Any) -> Imputer:
        """Create Imputer."""
        # remove logger key as we don't own this featurizer
        if constants.FeatureSweeping.LOGGER_KEY in kwargs:
            kwargs.pop(constants.FeatureSweeping.LOGGER_KEY)
        return Imputer(*args, **kwargs)

    @classmethod
    def minibatchkmeans_featurizer(cls, *args: Any, **kwargs: Any) -> MiniBatchKMeans:
        """Create mini batch k means featurizer."""
        # remove logger key as we don't own this featurizer
        if constants.FeatureSweeping.LOGGER_KEY in kwargs:
            kwargs.pop(constants.FeatureSweeping.LOGGER_KEY)
        return MiniBatchKMeans(*args, **kwargs)

    @classmethod
    def maxabsscaler(cls, *args: Any, **kwargs: Any) -> MaxAbsScaler:
        """Create maxabsscaler featurizer."""
        # remove logger key as we don't own this featurizer
        if constants.FeatureSweeping.LOGGER_KEY in kwargs:
            kwargs.pop(constants.FeatureSweeping.LOGGER_KEY)
        return MaxAbsScaler(*args, **kwargs)

    @classmethod
    def nimbus_missing_values_handler(cls, *args: Any, **kwargs: Any) -> NimbusMLMissingValuesHandler:
        """Create Imputer."""
        return NimbusMLMissingValuesHandler(*args, **kwargs)

    @classmethod
    def nimbus_column_selector(cls, *args: Any, **kwargs: Any) -> NimbusMLColumnSelector:
        """Create Column Selector transform."""
        return NimbusMLColumnSelector(*args, **kwargs)
