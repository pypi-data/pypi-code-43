# encoding: utf-8
import unittest

from hyperstools.request import External

class TestHyperstools(unittest.TestCase):
    """Tests for `hyperstools` package."""


    def test_000_something(self):
        """Test something."""
        External.get('https://baidu.com')

    def test_cache(self):
        External.get('https://baidu.com')
        External.get('https://baidu.com', cache=True)