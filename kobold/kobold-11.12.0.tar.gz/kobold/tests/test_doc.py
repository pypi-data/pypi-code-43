import unittest

from kobold import assertions

class SUT(object):
    def get_dictionary(self):
        return {'a': 1, 'c': 10, 'b': 2, 'd': [4, 5, 7]}

class TestExample(unittest.TestCase):
    def test_comparison_example(self):
        sut = SUT()
        self.assertEqual(
           {'a': 1, 'b': 2, 'c': 3, 'd': [4, 5, 6]},
           sut.get_dictionary())

    def test_kobold_example(self):
        sut = SUT()
        assertions.assert_match(
           {'a': 1, 'b': 2, 'c': 3, 'd': [4, 5, 6]},
           sut.get_dictionary())

 

