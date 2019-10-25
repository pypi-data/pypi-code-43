# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Utility methods for featurizers."""
from typing import Any, Callable, Dict, ItemsView, List, Optional, Tuple, TypeVar
import importlib

from automl.client.core.common import logging_utilities
from azureml.automl.core.constants import (TransformerNameMappings as _TransformerNameMappings,
                                           _FeaturizersType)
from .automltransformer import AutoMLTransformer

from sklearn.pipeline import Pipeline

ReturnFeaturizerT = TypeVar('ReturnFeaturizerT', bound=AutoMLTransformer)


def if_package_exists(feature_name: str, packages: List[str]) \
        -> 'Callable[..., Callable[..., Optional[ReturnFeaturizerT]]]':
    """
    Check if package is installed.

    If exists then make call to the function wrapped.
    Else log the error and return None.

    :param feature_name: Feature name that wil be enabled or disabled based on packages availability.
    :param packages: Packages to check
    :return: Wrapped function call.
    """
    def func_wrapper(function: 'Callable[..., ReturnFeaturizerT]') -> 'Callable[..., Optional[ReturnFeaturizerT]]':

        def f_wrapper(*args: Any, **kwargs: Any) -> Optional[ReturnFeaturizerT]:
            package = None
            try:
                for package in packages:
                    importlib.import_module(name=package)
                return function(*args, **kwargs)

            except ImportError as e:
                logger = logging_utilities.get_logger() if kwargs is None \
                    else kwargs.get("logger", logging_utilities.get_logger())
                logger.warning(
                    "'{}' package not found, '{}' will be disabled. Exception: {}".format(package, feature_name, e))
                return None

        return f_wrapper

    return func_wrapper


def get_transform_names(transforms: Any) -> List[str]:
    """
    Get transform names as list of string.

    :param: Transforms which can be Pipeline or List.
    :return: List of transform names.
    """
    transformer_list = []
    if isinstance(transforms, Pipeline):
        for tr in transforms.steps:
            transform = tr[1]
            if hasattr(transform, "steps"):
                for substep in transform.steps:
                    transformer_list.append(type(substep[1]).__name__)
            else:
                transformer_list.append(type(transform).__name__)
    else:
        transformer_list = [type(tr).__name__ for tr in transforms]

    return transformer_list


def get_transformer_params_by_column_names(transformer: str,
                                           cols: Optional[List[str]] = None,
                                           featurization_config: Any = None) -> Dict[str, Any]:
    """
    Get transformer customization parameters for columns.

    :param transformer: Transformer name.
    :type transformer: str
    :param featurization_config: featurization configuration object.
    :type featurization_config: FeaturizationConfig
    :param cols: Columns names; empty list if customize for all columns.
    :type cols: List[str]
    :return: transformer params settings
    :rtype: dict
    """
    if featurization_config is not None:
        params = featurization_config.get_transformer_params(transformer, cols) \
            if cols is not None else dict()  # type: Dict[str, Any]
        if len(params) == 0:
            # retrieve global transformer params setting
            params = featurization_config.get_transformer_params(transformer, [])
        return params
    return dict()


def get_transformers_method_mappings(transformer_list: List[str]) -> List[Tuple[str, str]]:
    factory_methods_types_mapping = []
    for transformer in transformer_list:
        factory_method_type = get_transformer_factory_method_and_type(transformer)
        if factory_method_type is not None:
            factory_methods_types_mapping.append(factory_method_type)
    return factory_methods_types_mapping


def get_transformer_factory_method_and_type(transformer: str) -> Optional[Tuple[str, str]]:
    if transformer in _TransformerNameMappings.CustomerFacingTransformerToTransformerMapCategoricalType:
        return ((
            str(_TransformerNameMappings.CustomerFacingTransformerToTransformerMapCategoricalType.get(transformer)),
            _FeaturizersType.Categorical
        ))
    elif transformer in _TransformerNameMappings.CustomerFacingTransformerToTransformerMapDateTimeType:
        return ((
            str(_TransformerNameMappings.CustomerFacingTransformerToTransformerMapDateTimeType.get(transformer)),
            _FeaturizersType.DateTime
        ))
    elif transformer in _TransformerNameMappings.CustomerFacingTransformerToTransformerMapGenericType:
        return ((
            str(_TransformerNameMappings.CustomerFacingTransformerToTransformerMapGenericType.get(transformer)),
            _FeaturizersType.Generic
        ))
    elif transformer in _TransformerNameMappings.CustomerFacingTransformerToTransformerMapNumericType:
        return ((
            str(_TransformerNameMappings.CustomerFacingTransformerToTransformerMapNumericType.get(transformer)),
            _FeaturizersType.Numeric
        ))
    elif transformer in _TransformerNameMappings.CustomerFacingTransformerToTransformerMapText:
        return ((
            str(_TransformerNameMappings.CustomerFacingTransformerToTransformerMapText.get(transformer)),
            _FeaturizersType.Text
        ))
    else:
        return None


def transformers_in_blocked_list(transformer_fncs: List[str], blocked_list: List[str]) -> bool:
    if blocked_list is None or len(blocked_list) == 0:
        return False

    for fnc in transformer_fncs:
        if fnc in blocked_list:
            return True
    return False


def transformer_fnc_to_customer_name(transformer_fnc: str, featurizer_type: str) -> str:
    if featurizer_type == _FeaturizersType.Generic:
        return _fnc_to_customer_name(_TransformerNameMappings.
                                     CustomerFacingTransformerToTransformerMapGenericType.items(),
                                     transformer_fnc)
    if featurizer_type == _FeaturizersType.Numeric:
        return _fnc_to_customer_name(_TransformerNameMappings.
                                     CustomerFacingTransformerToTransformerMapNumericType.items(),
                                     transformer_fnc)
    if featurizer_type == _FeaturizersType.Categorical:
        return _fnc_to_customer_name(_TransformerNameMappings.
                                     CustomerFacingTransformerToTransformerMapCategoricalType.items(),
                                     transformer_fnc)
    if featurizer_type == _FeaturizersType.DateTime:
        return _fnc_to_customer_name(_TransformerNameMappings.
                                     CustomerFacingTransformerToTransformerMapDateTimeType.items(),
                                     transformer_fnc)
    if featurizer_type == _FeaturizersType.Text:
        return _fnc_to_customer_name(_TransformerNameMappings.
                                     CustomerFacingTransformerToTransformerMapText.items(),
                                     transformer_fnc)
    return ""


def _fnc_to_customer_name(mappings: ItemsView[str, str], fnc_name_to_find: str) -> str:
    for customer_name, fnc_name in mappings:
        if fnc_name == fnc_name_to_find:
            return customer_name
    return ""
