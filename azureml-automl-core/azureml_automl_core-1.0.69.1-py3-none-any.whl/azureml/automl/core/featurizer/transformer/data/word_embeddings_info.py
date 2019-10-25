# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Holder for embedding information."""
from typing import Dict, Optional


class EmbeddingInfo:
    """Class to hold information of embeddings."""

    ENGLISH_FASTTEXT_WIKI_NEWS_SUBWORDS_300 = "wiki_news_300d_1M_subword"
    BERT_BASE_UNCASED = "bert-base-uncased"
    XLNET_BASE_CASED = "xlnet-base-cased"
    GLOVE_WIKIPEDIA_GIGAWORD_6B_300 = "glove_6B_300d_word2vec"

    _all_ = [ENGLISH_FASTTEXT_WIKI_NEWS_SUBWORDS_300,
             GLOVE_WIKIPEDIA_GIGAWORD_6B_300,
             BERT_BASE_UNCASED,
             XLNET_BASE_CASED]

    def __init__(self, user_friendly_name: str, embedding_name: str,
                 download_prefix: str, file_name: str,
                 lower_case: bool, license: str, credits: str,
                 md5hash: str) -> None:
        """
        Create embedding info object.

        :param embedding_name: Name of the embedding.
        :param download_prefix: Prefix of the url to download from.
        :param file_name: Name of the file to be appended to the prefix.
        :param lower_case: True if the embeddings were generated on strings
         after lower casing.
        """
        self._user_friendly_name = user_friendly_name
        self._embedding_name = embedding_name
        self._download_prefix = download_prefix
        self._file_name = file_name
        self._lower_case = lower_case
        self._license = license
        self._credits = credits
        self._md5hash = md5hash


# TODO Make this a full fledged class and move to config
class WordEmbeddingsInfo:
    """Word embeddings information holder."""
    BERT_EMB_INFO = EmbeddingInfo.BERT_BASE_UNCASED
    XLNET_EMB_INFO = EmbeddingInfo.XLNET_BASE_CASED
    WORD_VEC_LINK = "https://aka.ms/automl-resources/data/wordvectors/"
    embeddings = {
        EmbeddingInfo.ENGLISH_FASTTEXT_WIKI_NEWS_SUBWORDS_300:
            EmbeddingInfo(
                user_friendly_name="English word embeddings trained on wikipedia and web",
                embedding_name=EmbeddingInfo.ENGLISH_FASTTEXT_WIKI_NEWS_SUBWORDS_300,
                download_prefix="https://aka.ms/automl-resources/data/wordvectors/",
                file_name="{base}.pkl".format(base=EmbeddingInfo.ENGLISH_FASTTEXT_WIKI_NEWS_SUBWORDS_300),
                lower_case=False,
                license="Creative Commons Attribution-Share-Alike License (3.0). More information can be found at: "
                        "https://creativecommons.org/licenses/by-sa/3.0/",
                credits="Advances in Pre-Training Distributed Word Representations by "
                        "P. Bojanowski, E. Grave, A. Joulin, "
                        "T. Mikolov, Proceedings of the International Conference on Language Resources "
                        "and Evaluation (LREC 2018). More information can be found at: https://fasttext.cc and "
                        "http://https://arxiv.org/abs/1712.09405",
                md5hash="4fd6dce9765e619aca3d26481076763b"),
        EmbeddingInfo.BERT_BASE_UNCASED:
            EmbeddingInfo(
                user_friendly_name="BERT pretrained model",
                embedding_name=EmbeddingInfo.BERT_BASE_UNCASED,
                download_prefix=WORD_VEC_LINK,
                file_name="{base}.zip".format(base=BERT_EMB_INFO),
                lower_case=True,
                license="Apache License Version 2.0, More information can\
                be found at: "
                "http://www.apache.org/licenses/",
                credits="BERT: Pre-training of Deep Bidirectional Transformers\
                for Language Understanding by Devlin, Jacob and Chang, "
                "Ming-Wei and Lee, Kenton and Toutanova, Kristina,\
                arXiv preprint arXiv:1810.04805",
                md5hash="be74ba203bd19bd3d9e7ab17b6d9c9f6"),
        EmbeddingInfo.XLNET_BASE_CASED:
            EmbeddingInfo(
                user_friendly_name="XLNET pretrained model",
                embedding_name=EmbeddingInfo.XLNET_BASE_CASED,
                download_prefix=WORD_VEC_LINK,
                file_name="{base}.zip".format(base=XLNET_EMB_INFO),
                lower_case=False,
                license="Apache License Version 2.0, More information can\
                be found at: "
                "http://www.apache.org/licenses/",
                credits=" XLNet: Generalized Autoregressive Pretraining for\
                Language Understanding by Zhilin Yang*, Zihang Dai*, "
                "Yiming Yang, Jaime Carbonell, Ruslan Salakhutdinov, Quoc V. Le,\
                arXiv preprint arXiv:1906.08237",
                md5hash="7ec3cc8d7a2fecffbf68a572cb38240f"),
        EmbeddingInfo.GLOVE_WIKIPEDIA_GIGAWORD_6B_300:
            EmbeddingInfo(
                user_friendly_name="Glove word embeddings trained on wikipedia and gigawords",
                embedding_name=EmbeddingInfo.GLOVE_WIKIPEDIA_GIGAWORD_6B_300,
                download_prefix="https://aka.ms/automl-resources/data/wordvectors/",
                file_name="{base}.pkl".format(base=EmbeddingInfo.GLOVE_WIKIPEDIA_GIGAWORD_6B_300),
                lower_case=False,
                license="ODC Public Domain Dedication and Licence (PDDL). More information can be found at: "
                        "https://www.opendatacommons.org/licenses/pddl/1.0/",
                credits="GloVe: Global Vectors for Word Representation, "
                        "Empirical Methods in Natural Language Processing (EMNLP) 2014 "
                        "Jeffrey Pennington and Richard Socher and Christopher D. Manning "
                        "http://www.aclweb.org/anthology/D14-1162",
                md5hash="764913044de83d404ab095421291bda2")
    }                                                               # type: Dict[str, EmbeddingInfo]

    @classmethod
    def get(cls, embeddings_name: str) -> Optional[EmbeddingInfo]:
        """
        Get embedding information given the name.

        :param embeddings_name: Name of the requested embeddings.
        :return: Information on the embeddings.
        """
        return cls.embeddings[embeddings_name]\
            if embeddings_name in cls.embeddings else None
