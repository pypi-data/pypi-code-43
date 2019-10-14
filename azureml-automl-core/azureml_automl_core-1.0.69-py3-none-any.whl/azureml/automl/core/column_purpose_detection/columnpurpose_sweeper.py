# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Methods and classes used during an AutoML experiment to sweep through column purposes."""
from typing import List, Optional, Type, Union

from automl.client.core.common.constants import NumericalDtype, TextOrCategoricalDtype
from azureml.automl.core.constants import FeatureType as _FeatureType


class ColumnPurposeSweeper:
    """Methods and classes used during an AutoML experiment to sweep through column purposes."""

    # Possible safe conversions between types
    _SAFE_FEATURE_TYPE_CONVERSIONS = {_FeatureType.Hashes: _FeatureType.Text}
    _DTYPE_TO_FEATURE_TYPE_MAPPING = {
        _FeatureType.Categorical:
            {
                NumericalDtype.Integer: _FeatureType.Numeric,
                TextOrCategoricalDtype.String: _FeatureType.Text
            },
        _FeatureType.Text:
            {
                TextOrCategoricalDtype.String: _FeatureType.Categorical
            },
        _FeatureType.Numeric:
            {
                NumericalDtype.Integer: _FeatureType.Categorical
            }
    }

    @classmethod
    def safe_convert_on_feature_type(cls: Type["ColumnPurposeSweeper"],
                                     feature_type: str) -> Optional[str]:
        """
        Provide possible safe type column conversion options for feature type.

        :param feature_type: Feature type of the current column.
        :return: Possible column purposes that are compatible and safe to use.
        """
        # Safe conversion between feature types
        if feature_type in cls._SAFE_FEATURE_TYPE_CONVERSIONS:
            return cls._SAFE_FEATURE_TYPE_CONVERSIONS[feature_type]

        return None

    @classmethod
    def safe_convert_on_data_type(cls: Type["ColumnPurposeSweeper"],
                                  feature_type: str,
                                  data_type: str = '') -> Optional[str]:
        """
        Provide possible safe type column conversion options for data type.

        :param feature_type: Feature type of the current column.
        :param data_type: Data type inferred from infer_dtype().
        :return: Possible column purposes that are compatible and safe to use.
        """
        # Safe conversion based on specific data type
        # (e.g. Numeric feature type can include integer, float, and others but only integer is used as categorical.
        if feature_type in cls._DTYPE_TO_FEATURE_TYPE_MAPPING:
            if data_type in cls._DTYPE_TO_FEATURE_TYPE_MAPPING[feature_type]:
                return cls._DTYPE_TO_FEATURE_TYPE_MAPPING[feature_type][data_type]

        return None
