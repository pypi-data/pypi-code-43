# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Featurizer factory."""
from typing import Any, Optional

from automl.client.core.common.exceptions import ConfigException
from azureml.automl.core.constants import _FeaturizersType
from azureml.automl.core.featurization import FeaturizationConfig
from azureml.automl.core.featurizer.transformer.featurization_utilities import transformer_fnc_to_customer_name
from ..featurizer.transformer.text import TextFeaturizers
from ..featurizer.transformer.numeric import NumericFeaturizers
from ..featurizer.transformer.generic import GenericFeaturizers
from ..featurizer.transformer.categorical import CategoricalFeaturizers
from ..configuration.feature_config import FeatureConfig
from ..featurizer.transformer.datetime import DateTimeFeaturizers


class Featurizers:
    """Featurizer factory."""

    FEATURE_NAME_TO_FACTORY = {
        _FeaturizersType.Text: TextFeaturizers,
        _FeaturizersType.Numeric: NumericFeaturizers,
        _FeaturizersType.Categorical: CategoricalFeaturizers,
        _FeaturizersType.Generic: GenericFeaturizers,
        _FeaturizersType.DateTime: DateTimeFeaturizers
    }

    @classmethod
    def get(cls, config: FeatureConfig, featurization_config: Optional[FeaturizationConfig] = None) -> Any:
        """Get featurizer given an id and type. Initialize with params defined in the config.

        :param config: Configuration containing required feature details.
        :param featurization_config: customized featurization config provided by user.
        :return: Featurizer instance or None.
        """
        assert config is not None and isinstance(config, FeatureConfig)
        assert isinstance(config, FeatureConfig) and isinstance(config.id, str)
        assert isinstance(config.featurizer_type, str)
        feature_id = config.id
        if featurization_config and featurization_config.blocked_transformers:
            mapped_name = transformer_fnc_to_customer_name(feature_id, config.featurizer_type)
            if mapped_name in featurization_config.blocked_transformers:
                return

        return cls.get_transformer(
            featurizer_type=config.featurizer_type,
            factory_method_name=feature_id,
            args=config.featurizer_args,
            kwargs=config.featurizer_kwargs)

    @classmethod
    def get_transformer(cls, featurizer_type: str, factory_method_name: str, args: Any = [],
                        kwargs: Any = {}) -> Any:
        """Get featurizer given an factory method, featurizer type, args and kwargs.

        :param featurizer_type: featurizer type.
        :param factory_method_name: Transformer factory method name.
        :param args: Arguments to be send to the featurizer.
        :param kwargs: Keyword arguments to be send to the featurizer.
        :return: Featurizer instance or None.
        """
        if featurizer_type not in cls.FEATURE_NAME_TO_FACTORY:
            raise ConfigException("{featurizer_type} is not a valid featurizer type."
                                  .format(featurizer_type=featurizer_type))

        factory = cls.FEATURE_NAME_TO_FACTORY[featurizer_type]

        if not hasattr(factory, factory_method_name):
            raise ConfigException(
                "{feature_id} is not a valid featurizer in the featurizer type {featurizer_type}.".format(
                    feature_id=factory_method_name, featurizer_type=featurizer_type))

        factory_method = getattr(factory, factory_method_name)

        if not callable(factory_method):
            raise ConfigException(
                "{feature_id} is not a callable featurizer in the featurizer type {featurizer_type}.".format(
                    feature_id=factory_method_name, featurizer_type=featurizer_type))
        return factory_method(*args, **kwargs)
