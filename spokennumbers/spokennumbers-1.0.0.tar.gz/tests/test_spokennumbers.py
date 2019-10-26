"""Test parse_line"""

# Built-in imports
import unittest
import os

# Project
from spokennumbers import spoken


class TestSpoken(unittest.TestCase):
    """Test creating mp3 and txt"""

    def test_defaults(self):
        spoken(list(range(10))*50)
        self.assertTrue(os.path.isfile('spoken.mp3'))
        os.remove('spoken.mp3')


if __name__ == '__main__':
    unittest.main()
