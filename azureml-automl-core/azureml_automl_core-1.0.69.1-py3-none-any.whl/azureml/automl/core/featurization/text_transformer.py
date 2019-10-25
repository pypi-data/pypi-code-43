# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Class for top level text transformation logic."""
import logging
from typing import Optional, List

from automl.client.core.common import constants
from automl.client.core.runtime.types import TransformerType
from azureml.automl.core.constants import FeatureType as _FeatureType
from azureml.automl.core.constants import \
    SupportedTransformersInternal as _SupportedTransformersInternal
from azureml.automl.core.featurization.featurizationconfig import FeaturizationConfig
from .._engineered_feature_names import _FeatureTransformers, _GenerateEngineeredFeatureNames, \
    _Transformer, _OperatorNames, _TransformerParamsHelper
from ..featurizer.transformer import featurization_utilities
from ..featurizer.transformer.automltransformer import AutoMLTransformer
from ..featurizer.transformer.text.constants import TFIDF_VECTORIZER_CONFIG
from ..featurizer.transformer.text.text_featurizers import TextFeaturizers
from ..featurizer.transformer.text.utilities import max_ngram_len


class TextTransformer(AutoMLTransformer):
    """Class for top level text transformation logic."""

    def __init__(self,
                 task_type: Optional[str] = constants.Tasks.CLASSIFICATION,
                 logger: Optional[logging.Logger] = None,
                 is_onnx_compatible: bool = False,
                 featurization_config: Optional[FeaturizationConfig] = None):
        """
        Preprocessing class for Text.

        :param task_type: 'classification' or 'regression' depending on what kind of ML problem to solve.
        :param logger: The logger to use.
        :param is_onnx_compatible: if works in onnx compatible mode.
        """
        super().__init__()
        self._task_type = task_type
        self.logger = logger
        self.is_onnx_compatible = is_onnx_compatible
        self.featurization_config = featurization_config

    def get_transforms(self,
                       column: str,
                       column_name: str,
                       ngram_len: int,
                       engineered_feature_names: _GenerateEngineeredFeatureNames,
                       blocked_list: List[str] = []) -> \
            List[TransformerType]:
        """
        Create a list of transforms for text data.

        :param column: Column name in the data frame.
        :param column_name: Name of the column for engineered feature names.
        :param ngram_len: Continous length of characters or number of words.
        :param engineered_feature_names: Existing engineered feature names.
        :param blocked_list: List of transformers to exclude.
        :return: Text transformations to use in a list.
        """
        tr = []  # type: List[TransformerType]
        transformer_fncs = [_SupportedTransformersInternal.StringCast,
                            _SupportedTransformersInternal.TfIdf]
        transformer_in_blocked_list = featurization_utilities.transformers_in_blocked_list(transformer_fncs,
                                                                                           blocked_list)
        if transformer_in_blocked_list:
            return tr

        ngram_len = min(max_ngram_len, ngram_len)

        if not self.is_onnx_compatible:
            # The trichar transform is currently not ONNX compatible.
            # Add the transformations to be done and get the alias name
            # for the trichar transform.
            text_trichar_string_cast = TextFeaturizers.string_cast(logger=self.logger)
            text_trichar_tfidf = TextFeaturizers.tfidf_vectorizer(
                **{
                    'use_idf': False,
                    'norm': TFIDF_VECTORIZER_CONFIG.NORM,
                    'max_df': TFIDF_VECTORIZER_CONFIG.MAX_DF,
                    'analyzer': TFIDF_VECTORIZER_CONFIG.CHAR_ANALYZER,
                    'ngram_range': TFIDF_VECTORIZER_CONFIG.CHAR_NGRAM_RANGE,
                    **featurization_utilities.get_transformer_params_by_column_names(
                        _SupportedTransformersInternal.TfIdf, [column], self.featurization_config)
                })

            text_trichar_string_cast_transformer = _Transformer(
                parent_feature_list=[str(column_name)],
                transformation_fnc=transformer_fncs[0],
                operator=None,
                feature_type=_FeatureType.Text,
                should_output=False)
            # This transformation depends on the previous transformation
            # remove dtype since np.type is not serializable
            text_trichar_tfidf_transformer = _Transformer(
                parent_feature_list=[1],
                transformation_fnc=transformer_fncs[1],
                operator=_OperatorNames.CharGram, feature_type=None,
                should_output=True,
                transformer_params=_TransformerParamsHelper.to_dict(text_trichar_tfidf))
            # Create an object to convert transformations into JSON object
            feature_transformers = _FeatureTransformers([
                text_trichar_string_cast_transformer,
                text_trichar_tfidf_transformer])
            # Create the JSON object
            json_obj = feature_transformers.encode_transformations_from_list()
            # Persist the JSON object for later use and obtain an alias name
            tfidf_trichar_column_name = engineered_feature_names.get_raw_feature_alias_name(json_obj)

        # Add the transformations to be done and get the alias name
        # for the bigram word transform.
        text_biword_string_cast = TextFeaturizers.string_cast(logger=self.logger)
        text_biword_tfidf = TextFeaturizers.tfidf_vectorizer(
            **{
                'use_idf': False,
                'norm': TFIDF_VECTORIZER_CONFIG.NORM,
                'analyzer': TFIDF_VECTORIZER_CONFIG.WORD_ANALYZER,
                'ngram_range': TFIDF_VECTORIZER_CONFIG.WORD_NGRAM_RANGE,
                **featurization_utilities.get_transformer_params_by_column_names(
                    _SupportedTransformersInternal.TfIdf, [column], self.featurization_config)
            })
        text_biword_string_cast_transformer = _Transformer(
            parent_feature_list=[str(column_name)],
            transformation_fnc=transformer_fncs[0],
            operator=None,
            feature_type=_FeatureType.Text,
            should_output=False)
        # This transformation depends on the previous transformation
        text_biword_tfidf_transformer = _Transformer(
            parent_feature_list=[1],
            transformation_fnc=transformer_fncs[1],
            operator=_OperatorNames.WordGram,
            feature_type=None,
            should_output=True,
            transformer_params=_TransformerParamsHelper.to_dict(text_biword_tfidf))
        # Create an object to convert transformations into JSON object
        feature_transformers = _FeatureTransformers([
            text_biword_string_cast_transformer,
            text_biword_tfidf_transformer])
        # Create the JSON object
        json_obj = feature_transformers.encode_transformations_from_list()
        # Persist the JSON object for later use and obtain an alias name
        tfidf_biword_column_name = engineered_feature_names.get_raw_feature_alias_name(json_obj)

        if not self.is_onnx_compatible:
            # The trichar transform is currently not ONNX compatible.
            fea_tup_char = (column,
                            [text_trichar_string_cast, text_trichar_tfidf],
                            {'alias': str(tfidf_trichar_column_name)}
                            )
            tr.append(fea_tup_char)

        fea_tup_word = (column,
                        [text_biword_string_cast, text_biword_tfidf],
                        {'alias': str(tfidf_biword_column_name)}
                        )
        tr.append(fea_tup_word)

        return tr
