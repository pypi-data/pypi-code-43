#!/usr/bin/env python
# -*- coding: utf-8 -*-

# It script it publish under GNU GENERAL PUBLIC LICENSE
# http://www.gnu.org/licenses/gpl-3.0.en.html
# Author: the Galaxie Viewer Team, all rights reserved

import unittest

from GLXViewer.utils import center_text
from GLXViewer.utils import resize_text
from GLXViewer.utils import bracket_text
import shutil


# Unittest
class TestUtils(unittest.TestCase):
    # Test
    def test_utils_center_text(self):

        self.assertRaises(TypeError, center_text, text='', max_width='')
        self.assertRaises(TypeError, center_text, text=None, max_width=None)

        self.assertEqual("  *  ", center_text(text="*", max_width=5))
        self.assertEqual(" TX  ", center_text(text="TX", max_width=5))
        self.assertEqual(" RX  ", center_text(text="RX", max_width=5))
        self.assertEqual(" DLA ", center_text(text="DLA", max_width=5))
        self.assertEqual("INIT ", center_text(text="INIT", max_width=5))
        self.assertEqual("DEBUG", center_text(text="DEBUG", max_width=5))
        self.assertEqual(
            shutil.get_terminal_size()[0], len(center_text(text="DEBUG", max_width=None))
        )

    def test_utils_text(self):
        """Test utils.resize_text()"""
        text = "123456789"
        width = 10
        self.assertEqual(text, resize_text(text, width, "~"))
        width = 9
        self.assertEqual(text, resize_text(text, width, "~"))
        width = 8
        self.assertEqual("123~789", resize_text(text, width, "~"))
        width = 7
        self.assertEqual("123~789", resize_text(text, width, "~"))
        width = 6
        self.assertEqual("12~89", resize_text(text, width, "~"))
        width = 5
        self.assertEqual("12~89", resize_text(text, width, "~"))
        width = 4
        self.assertEqual("1~9", resize_text(text, width, "~"))
        width = 3
        self.assertEqual("1~9", resize_text(text, width, "~"))
        width = 2
        self.assertEqual("19", resize_text(text, width, "~"))
        width = 1
        self.assertEqual("1", resize_text(text, width, "~"))
        width = 0
        self.assertEqual("", resize_text(text, width, "~"))
        width = -1
        self.assertEqual("", resize_text(text, width, "~"))

        # Test Error
        self.assertRaises(
            TypeError,
            resize_text,
            text=text,
            max_width=width,
            separator=int(42),
        )
        self.assertRaises(
            TypeError, resize_text, text=text, max_width="coucou", separator="~"
        )
        self.assertRaises(
            TypeError, resize_text, text=int(42), max_width=width, separator="~"
        )

    def test_bracket_test(self):

        self.assertRaises(TypeError, bracket_text, text=None, symbol_inner="[", symbol_outer="]")
        self.assertRaises(TypeError, bracket_text, text='Hello', symbol_inner=42, symbol_outer="]")
        self.assertRaises(TypeError, bracket_text, text='Hello', symbol_inner='42', symbol_outer=42)
        self.assertEqual(bracket_text(text="Hello"), "[Hello]")


if __name__ == "__main__":
    unittest.main()
