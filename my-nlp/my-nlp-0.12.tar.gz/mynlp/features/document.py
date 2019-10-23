from sklearn.feature_extraction.text import TfidfVectorizer
from gensim.sklearn_api import W2VTransformer
from gensim import models
from mynlp.preprocess import sentence
from collections import defaultdict, Counter
from gensim import corpora

class Document:
    def __init__(self, text, word2vec_size=10, word2vec_mint_count=1, word2vec_seed=1):
        self._document = sentence(text)
        self.word2vec_size = word2vec_size
        self.word2vec_mint_count = word2vec_mint_count
        self.word2vec_seed = word2vec_seed

    def _gen_corpus(self, min_count=1):
        words = self._document.words
        frequency = Counter([word for sentence in words for word in sentence])
        texts = [
            [token for token in text if frequency[token] > min_count]
            for text in words
        ]
        self._dictionary = corpora.Dictionary(texts)
        self._corpus = [self._dictionary.doc2bow(text) for text in texts]

    def _tfidf(self):
        self._tfidf_vectorizer = TfidfVectorizer()
        self._tfidf_feature = self._tfidf_vectorizer.fit_transform(self.corpus)
        return self._tfidf_feature

    def _word2vec(self):
        self._w2vmodel = W2VTransformer(size=self.word2vec_size, min_count=self.word2vec_mint_count, seed=self.word2vec_seed)
        self._w2vmodel.fit(self._document.words)

    @property
    def tfidf_feature(self):
        """ tfidf 特征
        """
        try:
            if not self._tfidf_feature:
                self._tfidf()
        except AttributeError:
            self._tfidf()
        return self._tfidf_feature

    @property
    def tfidf_vectorizer(self):
        """ tfidf 模型
        """
        try:
            if not self._tfidf_vectorizer:
                self._tfidf()
        except AttributeError:
            self._tfidf()
        return self._tfidf_vectorizer

    @property
    def word2vec_model(self):
        """ word2vec model
        """
        try: 
            if not self._w2vmodel:
                self._word2vec()
        except AttributeError:
            self._word2vec()
        return self._w2vmodel

    @property
    def corpus(self):
        try:
            if not self._corpus:
                self._gen_corpus()
        except AttributeError:
            self._gen_corpus()
        return self._corpus

    @property
    def dictionary(self):
        try:
            if not self._dictionary:
                self._gen_corpus()
        except AttributeError:
            self._gen_corpus()
        return self._dictionary

    def word2vec(self, words):
        """ word2vec 转换函数
        """
        try:
            if not self._w2vmodel:
                self._word2vec()
        except AttributeError:
            self._word2vec()
        return self._w2vmodel.transform(words)