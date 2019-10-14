# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Container for Text featurizers."""
from pydoc import locate
from typing import Any, List, Tuple, cast, Union

from nimbusml.feature_extraction.text import NGramFeaturizer as NimbusMLNGramFeaturizer
from nimbusml.feature_extraction.text.extractor import Ngram

from sklearn.feature_extraction.text import CountVectorizer, TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
import numpy as np

from automl.client.core.common import constants, logging_utilities
from .bagofwords_transformer import BagOfWordsTransformer
from .nimbus_ml_text_target_encoder import NimbusMLTextTargetEncoder
from .stats_transformer import StatsTransformer
from .stringcast_transformer import StringCastTransformer
from .string_concat_transformer import StringConcatTransformer
from .wordembedding_transformer import WordEmbeddingTransformer
from .pretrained_text_dnn_transformer import PretrainedTextDNNTransformer
from ..data import DataProviders
from ..data.word_embeddings_info import EmbeddingInfo
from ..generic.modelbased_target_encoder import ModelBasedTargetEncoder
from ..featurization_utilities import if_package_exists
from .bilstm_attention_transformer import BiLSTMAttentionTransformer

from .constants import NIMBUS_ML_PARAMS


class TextFeaturizers:
    """Container for Text featurizers."""

    @classmethod
    def bow_transformer(cls, *args: Any, **kwargs: Any) ->\
            BagOfWordsTransformer:
        """Create bag of words transformer."""
        if 'wordgram_range' in kwargs and isinstance(kwargs['wordgram_range'], List):
            kwargs['wordgram_range'] = tuple(kwargs['wordgram_range'])
        if 'chargram_range' in kwargs and isinstance(kwargs['chargram_range'], List):
            kwargs['chargram_range'] = tuple(kwargs['chargram_range'])
        return BagOfWordsTransformer(*args, **kwargs)

    @classmethod
    def count_vectorizer(cls, *args: Any, **kwargs: Any) -> CountVectorizer:
        """Create count vectorizer featurizer."""
        if constants.FeatureSweeping.LOGGER_KEY in kwargs:
            kwargs.pop(constants.FeatureSweeping.LOGGER_KEY)
        if 'dtype' not in kwargs:
            kwargs['dtype'] = np.uint8
        return CountVectorizer(*args, **kwargs)

    @classmethod
    def naive_bayes(cls, *args: Any, **kwargs: Any) -> ModelBasedTargetEncoder:
        """Create naive bayes featurizer."""
        if not kwargs:
            kwargs = {}

        kwargs["model_class"] = MultinomialNB
        return ModelBasedTargetEncoder(*args, **kwargs)

    @classmethod
    def string_cast(cls, *args: Any, **kwargs: Any) -> StringCastTransformer:
        """Create string cast featurizer."""
        return StringCastTransformer(*args, **kwargs)

    @classmethod
    def string_concat(cls, *args: Any, **kwargs: Any) -> StringConcatTransformer:
        """Create string concat transformer."""
        return StringConcatTransformer(*args, **kwargs)

    @classmethod
    def text_stats(cls, *args: Any, **kwargs: Any) -> StatsTransformer:
        """Create text stats transformer."""
        return StatsTransformer(*args, **kwargs)

    @classmethod
    def text_target_encoder(cls, *args: Any, **kwargs: Any) -> ModelBasedTargetEncoder:
        """Create text target encoder."""
        if "model_class" in kwargs and isinstance(kwargs["model_class"], str):
            kwargs["model_class"] = locate(kwargs["model_class"])
        return ModelBasedTargetEncoder(*args, **kwargs)

    @classmethod
    @if_package_exists("AveragePerceptronTextTargetEncoder", ["nimbusml"])
    def averaged_perceptron_text_target_encoder(cls, *args: Any,
                                                **kwargs: Any) ->\
            NimbusMLTextTargetEncoder:
        """Create text target encoder using NimbusML AveragedPerceptron classifier."""
        from nimbusml.feature_extraction.text import NGramFeaturizer
        from nimbusml.feature_extraction.text.extractor import Ngram
        from nimbusml.linear_model import AveragedPerceptronBinaryClassifier
        featurizer = NGramFeaturizer(
            char_feature_extractor=Ngram(
                weighting=NIMBUS_ML_PARAMS.NGRAM_CHAR_WEIGHTING,
                ngram_length=NIMBUS_ML_PARAMS.NGRAM_CHAR_LENGTH,
                all_lengths=NIMBUS_ML_PARAMS.NGRAM_CHAR_ALL_LENGTHS),
            word_feature_extractor=Ngram(
                weighting=NIMBUS_ML_PARAMS.NGRAM_WORD_WEIGHTING,
                ngram_length=NIMBUS_ML_PARAMS.NGRAM_WORD_LENGTH,
                all_lengths=NIMBUS_ML_PARAMS.NGRAM_WORD_ALL_LENGTHS),
            vector_normalizer="L2")
        avg_perceptron = AveragedPerceptronBinaryClassifier(
            number_of_iterations=NIMBUS_ML_PARAMS.AVG_PERCEPTRON_ITERATIONS)
        return NimbusMLTextTargetEncoder(featurizer=featurizer, learner=avg_perceptron)

    @classmethod
    def tfidf_vectorizer(cls, *args: Any, **kwargs: Any) -> TfidfVectorizer:
        """Create tfidf featurizer."""
        if constants.FeatureSweeping.LOGGER_KEY in kwargs:
            kwargs.pop(constants.FeatureSweeping.LOGGER_KEY)
        if 'dtype' not in kwargs:
            kwargs['dtype'] = np.float32
        return TfidfVectorizer(*args, **kwargs)

    @classmethod
    def word_embeddings(cls, embeddings_name: str = EmbeddingInfo.ENGLISH_FASTTEXT_WIKI_NEWS_SUBWORDS_300,
                        only_run_on_cpu: bool = True, *args: Any, **kwargs: Any) ->\
            Union[WordEmbeddingTransformer, None]:
        """
        Create word embedding based transformer.

        :param embeddings_name: Name of the embeddings of interest.
        """
        # Disable work embeddings when sweeping over BERT on gpu boxes
        # TODO: refactor this logic into a more explicit BERT/LSTM/word_embeddings logical structure.
        try:
            import torch
            is_gpu = torch.cuda.is_available()
            if is_gpu and only_run_on_cpu:
                return None
        except ImportError:
            pass
        logger_key = "logger"
        kwargs[logger_key] = kwargs.get(logger_key,
                                        logging_utilities.get_logger())
        assert embeddings_name is not None and\
            embeddings_name in EmbeddingInfo._all_

        if WordEmbeddingTransformer.EMBEDDING_PROVIDER_KEY not in kwargs:
            kwargs[WordEmbeddingTransformer.EMBEDDING_PROVIDER_KEY] =\
                DataProviders.get(embeddings_name)

        return WordEmbeddingTransformer(*args, **kwargs)

    @classmethod
    @if_package_exists("PretrainedTextDNNTransformer", ["torch", "pytorch_transformers"])
    def pretrained_text_dnn(cls, embeddings_name: str = EmbeddingInfo.BERT_BASE_UNCASED,
                            can_run_on_cpu: bool = False, *args: Any, **kwargs: Any) ->\
            Union[PretrainedTextDNNTransformer, None]:
        """
        Create pretrained BERT/Transformer transformer that does fine-tuning when fit() is called.

        :param embeddings_name: Name of the pretrained model (e.g. 'bert-base-uncased', 'xlnet-base-cased').
        :param can_run_on_cpu: If set to False, then this method will return None if pytorch cannot detect a gpu.
        """
        import torch
        logger_key = "logger"
        logger = kwargs.get(logger_key, logging_utilities.get_logger())
        kwargs[logger_key] = logger
        assert embeddings_name is not None and embeddings_name in EmbeddingInfo._all_
        kwargs["provider"] = DataProviders.get("pretrained_text_dnn", model_name=embeddings_name)
        is_gpu = torch.cuda.is_available()
        logger.info("Cuda availability for pretrained_text_dnn={}".format(is_gpu))
        if not can_run_on_cpu and not is_gpu:
            return None

        # TODO: ensure that task is being passed in here since this
        # transformer needs to know if it's doing classification or regression
        return PretrainedTextDNNTransformer(*args, **kwargs)

    @classmethod
    @if_package_exists("BiLSTMAttentionTransformer", ["torch", "spacy", "en_core_web_sm"])
    def bilstm_text_dnn(cls,
                        embeddings_name: str = EmbeddingInfo.GLOVE_WIKIPEDIA_GIGAWORD_6B_300,
                        can_run_on_gpu: bool = False,
                        *args: Any,
                        **kwargs: Any) -> \
            Union[BiLSTMAttentionTransformer, None]:
        """
        Create and return a BiDirectional LSTM transformer.
        The transformer trains the BiLSTM with given pretrained embeddings when fit() is called.
        :param embeddings_name: Name of the word vector embeddings (e.g. Glove, fastText)
        """
        logger_key = "logger"
        kwargs[logger_key] = kwargs.get(logger_key, logging_utilities.get_logger())
        assert embeddings_name is not None and embeddings_name in EmbeddingInfo._all_
        kwargs["embeddings_name"] = embeddings_name

        import torch
        if not can_run_on_gpu and torch.cuda.is_available():
            return None

        return BiLSTMAttentionTransformer(*args, **kwargs)

    @classmethod
    def get(cls, sweeper_name: str, *args: Any, **kwargs: Any) -> Any:
        """
        Create and return the request sweeper.

        :param sweeper_name: Name of the requested sweeper.
        """
        if hasattr(cls, sweeper_name):
            member = getattr(cls, sweeper_name)
            # Check that the member is a callable
            if callable(member):
                return member(*args, **kwargs)
        return None

    @classmethod
    def nimbus_ngram_featurizer(cls, *args: Any, **kwargs: Any) -> NimbusMLNGramFeaturizer:
        """Create NimbusML NGram featurizer."""
        # set the word feature extractor params for NimbusML NGram Featurizer, default to NimbusML defaults
        if kwargs.get(NIMBUS_ML_PARAMS.NGRAM_WORD_LENGTH_KEY) is not None:
            kwargs[NIMBUS_ML_PARAMS.NGRAM_WORD_KEY] = \
                Ngram(ngram_length=kwargs.get(NIMBUS_ML_PARAMS.NGRAM_WORD_LENGTH_KEY),
                      max_num_terms=[200000])
            del kwargs[NIMBUS_ML_PARAMS.NGRAM_WORD_LENGTH_KEY]

        # set the char feature extractor params for NimbusML NGram Featurizer, default to None
        # This behavior can/should be changed based on experimentation
        if kwargs.get(NIMBUS_ML_PARAMS.NGRAM_CHAR_LENGTH_KEY) is not None:
            kwargs[NIMBUS_ML_PARAMS.NGRAM_CHAR_KEY] = \
                Ngram(ngram_length=kwargs.get(NIMBUS_ML_PARAMS.NGRAM_CHAR_LENGTH_KEY),
                      max_num_terms=[200000])
            del kwargs[NIMBUS_ML_PARAMS.NGRAM_CHAR_LENGTH_KEY]
        else:
            kwargs[NIMBUS_ML_PARAMS.NGRAM_CHAR_KEY] = None
        return NimbusMLNGramFeaturizer(*args, **kwargs)
