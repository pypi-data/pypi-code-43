# encoding=utf-8
""" This module contains tests for mwklient.util.
The class TestUtil defines unit test cases.
"""
import unittest
import time
from mwklient.util import parse_timestamp


class TestUtil(unittest.TestCase):
    """
    A class whose instances are single test cases for mwklient.util
    """

    def test_parse_missing_timestamp(self):
        assert time.struct_time(
            (0, 0, 0, 0, 0, 0, 0, 0, 0)) == parse_timestamp(None)

    def test_parse_empty_timestamp(self):
        empty_ts = time.struct_time((0, 0, 0, 0, 0, 0, 0, 0, 0))
        self.assertEqual(empty_ts, parse_timestamp('0000-00-00T00:00:00Z'))

    def test_parse_none_timestamp(self):
        empty_ts = time.struct_time((0, 0, 0, 0, 0, 0, 0, 0, 0))
        self.assertEqual(empty_ts, parse_timestamp(None))

    def test_parse_nonempty_timestamp(self):
        nice_ts = time.struct_time((2015, 1, 2, 20, 18, 36, 4, 2, -1))
        self.assertEqual(nice_ts, parse_timestamp('2015-01-02T20:18:36Z'))


if __name__ == '__main__':
    unittest.main()
