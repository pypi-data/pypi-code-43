"""Tests the status module in KomiDL"""

import os
import sys
import unittest
from unittest.mock import patch
sys.path.append(os.path.abspath('..'))

import komidl.status as status

class StatusTest(unittest.TestCase):
    """Test the status module in KomiDL"""
    #######################################################################
    # prompt()
    #######################################################################

    def test_yn_lower_y(self):
        """Lowercase 'y' entered in prompt()"""
        with patch("builtins.input", return_value='y') as _input:
            self.assertEqual(status.prompt("Test msg"), True)
    
    def test_yn_upper_y(self):
        """Uppercase 'Y' entered in prompt()"""
        with patch("builtins.input", return_value='Y') as _input:
            self.assertEqual(status.prompt("Test msg"), True)
    
    def test_yn_lower_n(self):
        """Lowercase 'n' entered in prompt()"""
        with patch("builtins.input", return_value='n') as _input:
            self.assertEqual(status.prompt("Test msg"), False)

    def test_yn_upper_n(self):
        """Uppercase 'N' entered in prompt()"""
        with patch("builtins.input", return_value='N') as _input:
            self.assertEqual(status.prompt("Test msg"), False)
    
    def test_yn_random(self):
        """A character not 'y' or 'n' entered in prompt()"""
        with patch("builtins.input", return_value='q') as _input:
            self.assertEqual(status.prompt("Test msg"), False)
    
    def test_yn_empty(self):
        """No character entered in prompt()"""
        with patch("builtins.input", return_value='') as _input:
            self.assertEqual(status.prompt("Test msg"), False)

    def test_yn_yes_arg(self):
        """Skip the prompt if args.yes is True"""
        self.assertEqual(status.prompt("Test msg", True), True)

    #######################################################################
    # Miscellaneous
    #######################################################################
    
    def test_get_bars(self):
        """Test # of bars to display"""
        test_cases = ((50, 100, 50, 25),
                      (50, 100, 33, 16),
                      (50, 100, 100, 50),
                      (50, 100, 0, 0))
        for barsize, gallery_size, current, expected_bars in test_cases:
            actual_bars = status._bar_size(barsize, current, gallery_size)
            self.assertEqual(expected_bars, actual_bars)

    def test_get_percent(self):
        """Test percentage calculations"""
        test_cases = ((100, 50, 50),
                      (100, 23, 23),
                      (100, 100, 100),
                      (100, 0, 0))
        for gallery_size, current, expected_percent in test_cases:
            actual_percent = status._percent(current, gallery_size)
            self.assertEqual(expected_percent, actual_percent)
