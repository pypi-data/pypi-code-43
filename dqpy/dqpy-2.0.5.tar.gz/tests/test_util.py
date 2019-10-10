import unittest

from dq import util


class TestUtil(unittest.TestCase):

    def test_safe_cast(self):
        assert util.safe_cast('1', int) == 1
        assert util.safe_cast('meow', int, 2) == 2
