#!/usr/bin/env python
# -*- coding: utf-8 -*-

# It script it publish under GNU GENERAL PUBLIC LICENSE
# http://www.gnu.org/licenses/gpl-3.0.en.html
# Author: the Galaxie Viewer Team, all rights reserved

from io import StringIO
import unittest
from unittest.mock import patch

from GLXViewer.viewer import flush_infos
from GLXViewer.viewer import flush_a_new_line


class TestView(unittest.TestCase):
    # Test
    def test_flush_infos(self):
        color_list = [
            "ORANGE",
            "RED",
            "RED2",
            "YELLOW",
            "YELLOW2",
            "WHITE",
            "WHITE2",
            "CYAN",
            "GREEN",
            "GREEN2",
            "WORNG"
        ]
        for color in color_list:
            flush_infos(
                with_date=True,
                status_text="TEST",
                status_text_color=color,
                column_1="test with {0} color".format(color),
            )
        for color in color_list:
            flush_infos(
                with_date=False,
                status_text="TEST",
                status_text_color=color,
                column_1="test with {0} color".format(color),
            )
        for color in color_list:
            flush_infos(
                with_date=True,
                status_text="TEST",
                status_text_color=color,
                column_1="test with {0} color".format(color),
                prompt=-1,
                status_symbol='<'
            )
            flush_infos(
                with_date=False,
                status_text="TEST",
                status_text_color=color,
                column_1="test with {0} color".format(color),
                prompt=-1,
                status_symbol='<'
            )
        for color in color_list:
            flush_infos(
                with_date=True,
                status_text="TEST",
                status_text_color=color,
                column_1="test with {0} color".format(color),
                prompt=None,
                status_symbol='>'
            )
        for color in color_list:
            flush_infos(
                with_date=True,
                status_text="TEST",
                status_text_color=color,
                column_1="test with {0} color".format(color),
                prompt=1
            )
    def test_flush_new_line(self):
        with patch("sys.stdout", new=StringIO()) as fake_out:
            flush_a_new_line()
            self.assertEqual(fake_out.getvalue(), "\n")


if __name__ == "__main__":
    unittest.main()
