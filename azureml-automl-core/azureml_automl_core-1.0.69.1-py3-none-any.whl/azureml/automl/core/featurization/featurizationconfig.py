# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Configuration for AutoML customization."""
from typing import Any, Dict, List, Optional, Tuple, Union
import json
import logging

from automl.client.core.common.exceptions import ConfigException
from automl.client.core.runtime.types import ColumnTransformerParamType
from azureml.automl.core.constants import (SupportedTransformers as _SupportedTransformers,
                                           FeatureType as _FeatureType)
from ..featurizer.transformer import featurization_utilities


class FeaturizationConfig:
    """
    Featurization customization configuration for an Automated Machine Learning experiment in
    Azure Machine Learning service.
    """
    def __init__(
            self,
            blocked_transformers: Optional[List[str]] = None,
            column_purposes: Optional[Dict[str, str]] = None,
            transformer_params: Optional[Dict[str, List[ColumnTransformerParamType]]] = None,
            drop_columns: Optional[List[str]] = None
    ) -> None:
        """
        Create a FeaturizationConfig.

        :param blocked_transformers: List of transformer names to be blocked during featurization.
        :param column_purposes: Dictionary of column names and feature types used to update column purpose.
        :param transformer_params: Dictionary of transformer and corresponding customization parameters.
        :param drop_columns: List of columns to be ignored from featurization process.
        """
        self._blocked_transformers = blocked_transformers
        self._column_purposes = column_purposes
        self._transformer_params = transformer_params
        self._drop_columns = drop_columns

        self._validate_featurization_config_input()

    def add_column_purpose(self, column_name: str, feature_type: str) -> None:
        """
        Add feature type for the specified column.

        :param column_name: column name to update.
        :param feature_type: feature type to use for the column.
        """
        self._validate_feature_type(feature_type=feature_type)

        if self._column_purposes is None:
            self._column_purposes = {column_name: feature_type}
        else:
            self._column_purposes[column_name] = feature_type

    def remove_column_purpose(self, column_name: str) -> None:
        """
        Remove feature type for the specified column. It will use detected default if not specified.

        :param column_name: column name
        :type column_name: str
        """
        if self._column_purposes is not None:
            self._column_purposes.pop(column_name, None)

    def add_blocked_transformers(self, transformers: Union[str, List[str]]) -> None:
        """
        Add transformers to be blocked.

        :param transformers: Transformer name or list of transformer names.
        :type transformers: str or List[str]
        """
        # validation
        self._validate_blocked_transformer_names(transformers)
        self._blocked_transformers = self._append_to_list(transformers, self._blocked_transformers)

    def add_drop_columns(self, drop_columns: Union[str, List[str]]) -> None:
        """
        Add column name or list of column names to ignore columns list.

        :param drop_columns: Column name or list of column names.
        :type drop_columns: str or List[str]
        """
        self._drop_columns = self._append_to_list(drop_columns, self._drop_columns)

    def add_transformer_params(self, transformer: str, cols: List[str], params: Dict[str, Any]) -> None:
        """
        Add customized transformer parameters to the list of custom transformer parameters.
        Apply to all columns if column list is empty.

        :param transformer: Transformer name.
        :param cols: Input columns for specified transformer.
            Some transformers can take multiple column as input, hence accepting list.
        :param params: Dictionary of keywords and arguments.
        """
        self._validate_transformer_names(transformer=transformer)
        self._validate_transformer_kwargs(transformer=transformer, kwargs=params)

        if self._transformer_params is None:
            self._transformer_params = {transformer: [(cols, params)]}
        else:
            self.remove_transformer_params(transformer, cols)
            if transformer in self._transformer_params:
                self._transformer_params[transformer].append((cols, params))
            else:
                self._transformer_params[transformer] = [(cols, params)]

    def get_transformer_params(self, transformer: str, cols: List[str]) -> Dict[str, Any]:
        """
        Retrieve transformer customization parameters for columns.

        :param transformer: Transformer name.
        :type transformer: str
        :param cols: Columns names; empty list if customize for all columns.
        :type cols: List[str]
        :return: transformer params settings
        :rtype: Dict
        """
        if self._transformer_params is not None and transformer in self._transformer_params:

            separator = '#'
            column_transformer_params = list(
                filter(lambda item: separator.join(item[0]) == separator.join(cols),
                       self._transformer_params[transformer]))
            if len(column_transformer_params) == 1:
                return column_transformer_params[0][1]
        return {}

    def remove_transformer_params(
            self,
            transformer: str,
            cols: Optional[List[str]] = None
    ) -> None:
        """
        Remove transformer customization parameters for specific column or all columns.

        :param transformer: Transformer name.
        :type transformer: str
        :param cols: Columns names; None if remove all customize params for specific transformers.
        :type cols: List[str] or None
        """
        self._validate_transformer_names(transformer)

        if self._transformer_params is not None and transformer in self._transformer_params:
            if cols is None:
                self._transformer_params.pop(transformer, None)
            else:
                # columns = cols  # type: List[str]
                separator = '#'
                column_transformer_params = [item for item in self._transformer_params[transformer]
                                             if separator.join(item[0]) != separator.join(cols)]
                if len(column_transformer_params) == 0:
                    self._transformer_params.pop(transformer, None)
                else:
                    self._transformer_params[transformer] = column_transformer_params

    def _validate_featurization_config_input(self):
        if self._blocked_transformers is not None:
            self._validate_transformer_names(self._blocked_transformers)
        if self._column_purposes is not None:
            for feature_type in self._column_purposes.values():
                self._validate_feature_type(feature_type)
        if self._transformer_params is not None:
            for transformer_name, column_transformer_params in self._transformer_params.items():
                self._validate_transformer_names(transformer_name)
                for (column_selector, transformer_kwargs) in column_transformer_params:
                    self._validate_transformer_kwargs(transformer=transformer_name, kwargs=transformer_kwargs)

    def _validate_transformer_names(self, transformer: Union[str, List[str]]) -> None:
        if isinstance(transformer, str):
            self._validate_transformer_fullset(transformer)
        else:
            for t in transformer:
                self._validate_transformer_fullset(t)

    def _validate_blocked_transformer_names(self, transformer: Union[str, List[str]]) -> None:
        if isinstance(transformer, str):
            self._validate_transformer_fullset(transformer)
            self._validate_transformer_blockedlist(transformer)
        else:
            for t in transformer:
                self._validate_transformer_fullset(t)
                self._validate_transformer_blockedlist(t)

    @staticmethod
    def _append_to_list(items: Union[str, List[str]], origin_list: Optional[List[str]]) -> List[str]:
        extend_list = [items] if isinstance(items, str) else items
        new_list = [] if origin_list is None else origin_list
        new_list.extend(extend_list)
        return new_list

    @staticmethod
    def _validate_feature_type(feature_type: str) -> None:
        if feature_type not in _FeatureType.FULL_SET:
            raise ConfigException("Invalid feature_type ({0})".format(feature_type))

    @staticmethod
    def _validate_transformer_kwargs(transformer: str, kwargs: Dict[str, Any]) -> None:
        factory_method_and_type = featurization_utilities.get_transformer_factory_method_and_type(
            transformer)
        if factory_method_and_type is None:
            raise ConfigException(
                "Invalid transformer ({0}), please check the transformer name.".format(transformer))
        # TODO: Implement to validate transformer parameters.
        '''
        else:
            try:
                Featurizers.get_transformer(featurizer_type=factory_method_and_type[1],
                                            factory_method_name=factory_method_and_type[0],
                                            kwargs=kwargs)
            except Exception as e:
                raise ConfigException(
                    "Invalid transformer ({0}), can't construct object with exception: {1}".format(
                        transformer, e))
        '''

    @staticmethod
    def _validate_transformer_fullset(transformer: str) -> None:
        if transformer not in _SupportedTransformers.FULL_SET:
            raise ConfigException("Invalid transformer ({0})".format(transformer))

    @staticmethod
    def _validate_transformer_blockedlist(transformer: str) -> None:
        if transformer not in _SupportedTransformers.BLOCK_TRANSFORMERS:
            raise ConfigException("Transformer ({0}) cannot be blocked.".format(transformer))

    @property
    def blocked_transformers(self):
        return self._blocked_transformers

    @blocked_transformers.setter
    def blocked_transformers(self, blocked_transformers: List[str]) -> None:
        if blocked_transformers is not None:
            self._validate_blocked_transformer_names(blocked_transformers)
        self._blocked_transformers = blocked_transformers

    @property
    def column_purposes(self):
        return self._column_purposes

    @column_purposes.setter
    def column_purposes(self, column_purposes: Dict[str, str]) -> None:
        if column_purposes is not None:
            for column_name, feature_type in column_purposes.items():
                self._validate_feature_type(feature_type=feature_type)
        self._column_purposes = column_purposes

    @property
    def drop_columns(self):
        return self._drop_columns

    @drop_columns.setter
    def drop_columns(self, drop_columns: List[str]) -> None:
        self._drop_columns = drop_columns

    @property
    def transformer_params(self):
        return self._transformer_params

    @transformer_params.setter
    def transformer_params(self, transformer_params: Dict[str, List[ColumnTransformerParamType]]) -> None:
        if transformer_params is not None:
            for transformer, list_of_tuples in transformer_params.items():
                self._validate_transformer_names(transformer=transformer)
                for cols, params in list_of_tuples:
                    self._validate_transformer_kwargs(transformer=transformer, kwargs=params)
        self._transformer_params = transformer_params

    def _from_dict(self, dict):
        for key, value in dict.items():
            if key not in self.__dict__.keys():
                logging.warning(
                    "Received unrecognized parameter for FeaturizationConfig: {0} {1}".format(key, value))
            else:
                setattr(self, key, value)

    def __str__(self):
        return json.dumps(self.__dict__)
