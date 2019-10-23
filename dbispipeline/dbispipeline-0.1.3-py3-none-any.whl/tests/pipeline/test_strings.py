import string
import unittest

from dbispipeline.pipeline.strings import FlatteningTransformer
from dbispipeline.pipeline.strings import NgramTransformer
from dbispipeline.pipeline.strings import TextCleaner


class TestStrings(unittest.TestCase):

    def test_flattener(self):
        transformer = FlatteningTransformer()
        documents = [
            [[['This', 'is'], ['a', 'very']], [['Deep']], [['and'], 'weird'],
             'list'],
        ]
        expected = [
            'This is a very Deep and weird list',
        ]
        actual = transformer.transform(documents)
        self.assertEqual(expected, actual)

    def test_cleaner(self):
        transformer = TextCleaner()
        documents = [
            '!clean' + string.punctuation,
        ]
        expected = ['clean']
        actual = transformer.transform(documents)
        self.assertEqual(expected, actual)

    def test_ngram_word(self):
        transformer = NgramTransformer(analyzer='word', ngram_range=(1, 3))
        documents = ['This is a sentence.']
        expected = [[
            'This', 'is', 'a', 'sentence.', 'This is', 'is a', 'a sentence.',
            'This is a', 'is a sentence.'
        ]]
        actual = transformer.transform(documents)
        self.assertEqual(expected, actual)

    def test_ngram_char(self):
        transformer = NgramTransformer(analyzer='word', ngram_range=(1, 3))
        documents = ['This is a sentence.']
        expected = [[
            'This', 'is', 'a', 'sentence.', 'This is', 'is a', 'a sentence.',
            'This is a', 'is a sentence.'
        ]]
        actual = transformer.transform(documents)
        self.assertEqual(expected, actual)
