import unittest

from azureml.automl.core.featurizer.transformer.data import DataProviders
from azureml.automl.core.featurizer.transformer.data.automl_wordembeddings_provider import AutoMLEmbeddingsProvider


class TestDataProviders(unittest.TestCase):
    def test_wiki_news_300d_1M_subword(self):
        embeddings = DataProviders.wiki_news_300d_1M_subword()
        assert isinstance(embeddings, AutoMLEmbeddingsProvider)

    def test_glove_6B_300d_word2vec(self):
        embeddings = DataProviders.glove_6B_300d_word2vec()
        assert isinstance(embeddings, AutoMLEmbeddingsProvider)


if __name__ == '__main__':
    unittest.main()
