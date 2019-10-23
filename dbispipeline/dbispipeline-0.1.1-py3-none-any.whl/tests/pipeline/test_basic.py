import unittest

from dbispipeline.pipeline.basic import DictFieldTransformer
from dbispipeline.pipeline.basic import CallbackTransformer


class TestStrings(unittest.TestCase):

    def test_dict_field(self):
        transformer = DictFieldTransformer('field_b')
        documents = [
            {
                'field_a': 'a',
                'field_b': 123
            },
        ]
        expected = [123]
        actual = transformer.transform(documents)
        self.assertEqual(actual, expected)

    def test_callback(self):
        transformer = CallbackTransformer(lambda x: x.lower())
        documents = [
            'THIS is A string',
        ]
        expected = ['this is a string']
        actual = transformer.transform(documents)
        self.assertEqual(actual, expected)
