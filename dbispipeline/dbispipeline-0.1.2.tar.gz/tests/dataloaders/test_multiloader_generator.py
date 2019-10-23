import unittest
from dbispipeline.base import MultiLoaderGenerator, Loader


class TestLoader(Loader):

    def __init__(self, parameter1, parameter2):
        self.parameter1 = parameter1
        self.parameter2 = parameter2

    @property
    def configuration(self):
        return {
            'parameter1': self.parameter1,
            'parameter2': self.parameter2,
        }

    def load(self):
        return self.parameter1, self.parameter2


class TestMultiLoaderGenerator(unittest.TestCase):

    def test_explicit_tuples(self):
        parameters = [
            (1, 'a'),
            (1, 'b'),
            (2, 'a'),
            (3, 'b'),
        ]
        dataloader = MultiLoaderGenerator(TestLoader, parameters)
        self.assertEqual(dataloader.run_count, 4)
        configs = list(dataloader.configuration)
        self.assertEqual(len(configs), 4)
        self.assertTrue({
            'parameter1': 2,
            'parameter2': 'a',
            'run_number': 2,
            'class': 'TestLoader'
        } in configs)
        data = list(dataloader.load())
        self.assertEqual(len(data), 4),
        self.assertTrue((1, 'b') in data)
        self.assertTrue((2, 'a') in data)
        self.assertTrue((3, 'b') in data)
        self.assertFalse((5, 'b') in data)

    def test_explicit_dicts(self):
        """
        tests the generation of a multiloader by using explicit parameters
        """

        parameters = [
            {
                'parameter1': 1,
                'parameter2': 'a'
            },
            {
                'parameter1': 1,
                'parameter2': 'b'
            },
            {
                'parameter1': 2,
                'parameter2': 'a'
            },
            {
                'parameter1': 2,
                'parameter2': 'b'
            },
            {
                'parameter1': 3,
                'parameter2': 'a'
            },
            {
                'parameter1': 3,
                'parameter2': 'b'
            },
        ]

        dataloader = MultiLoaderGenerator(TestLoader, parameters)

        self.assertEqual(dataloader.run_count, 6)
        configs = list(dataloader.configuration)
        self.assertEqual(len(configs), 6)
        self.assertTrue({
            'parameter1': 2,
            'parameter2': 'b',
            'class': 'TestLoader',
            'run_number': 3
        } in configs)
        data = list(dataloader.load())
        self.assertEqual(len(data), 6),
        self.assertTrue((1, 'b') in data)
        self.assertTrue((2, 'b') in data)
        self.assertTrue((3, 'b') in data)
        self.assertFalse((5, 'b') in data)

    def test_generated_dictionary(self):
        """
        tests the generation of a multiloader by using a parameter dict
        """

        parameters = {
            'parameter1': [1, 2, 3],
            'parameter2': ['a', 'b'],
        }

        dataloader = MultiLoaderGenerator(TestLoader, parameters)

        self.assertEqual(dataloader.run_count, 6)
        configs = list(dataloader.configuration)
        self.assertEqual(len(configs), 6)
        # the run_number of the parameter setting can not be predicted
        found = list(
            filter(lambda x: (x['parameter1'] == 2 and x['parameter2'] == 'b'),
                   configs))
        self.assertEqual(len(found), 1)
        data = list(dataloader.load())
        self.assertEqual(len(data), 6),
        self.assertTrue((1, 'b') in data)
        self.assertTrue((2, 'b') in data)
        self.assertTrue((3, 'b') in data)
        self.assertFalse((5, 'b') in data)
