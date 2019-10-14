# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Transformer that featurizes a dataset in the streaming scenario."""
from typing import List

from nimbusml import Pipeline
from nimbusml.internal.core.base_pipeline_item import BasePipelineItem

from automl.client.core.common.types import FeaturizationSummaryType
from azureml.automl.core._engineered_feature_names import _GenerateEngineeredFeatureNames
from azureml.automl.core.featurization_info_provider import FeaturizationInfoProvider
from azureml.automl.core.featurization.streaming import NimbusMLStreamingEstimator


class StreamingFeaturizationTransformer(BasePipelineItem, FeaturizationInfoProvider):
    """Transformer that featurizes a dataset in the streaming scenario."""
    def __init__(
            self,
            transformer: NimbusMLStreamingEstimator,
            features_metadata_helper: _GenerateEngineeredFeatureNames):
        self._transformer = transformer
        self._features_metadata_helper = features_metadata_helper

        # set type to satisfy BasePipelineItem requirement
        self.type = 'transform'

    @property
    def pipeline(self) -> Pipeline:
        return self._transformer.pipeline

    def fit(self, training_data, **kwargs):
        self.pipeline.fit(training_data, None, **kwargs)
        return self

    def fit_transform(self, training_data):
        self.pipeline.fit(training_data, None)
        return self.pipeline.transform(training_data)

    def get_engineered_feature_names(self) -> List[str]:
        return self._features_metadata_helper._engineered_feature_names

    def get_featurization_summary(self, is_user_friendly: bool = True) -> FeaturizationSummaryType:
        """
        Return the featurization summary for all the input features seen by DataTransformer.
        :param is_user_friendly: If True, return user friendly summary, otherwise, return detailed
        featurization summary.
        :return: List of featurization summary for each input feature.
        """
        return self._features_metadata_helper.get_raw_features_featurization_summary(is_user_friendly)

    def get_params(self):
        """Scikit-learn API with same params, returns all parameters."""
        return self._transformer.pipeline.get_params()

    def transform(self, X, **kwargs):
        return self.pipeline.transform(X, **kwargs)

    def _get_node(self, **all_args):
        pass

    def __str__(self) -> str:
        return "{}(steps={})".format(
            self.__class__.__name__,
            str(self.pipeline.steps)
        )

    __repr__ = __str__
