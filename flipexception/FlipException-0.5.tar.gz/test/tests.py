#!/usr/bin/env python
# -*- coding: utf-8 -*-

import unittest
from flipexception import FlipException


class FlipAllTheThings(unittest.TestCase):
    def setUp(self):
        pass

    def test_exception_base(self):
        """
        Testing Exception Base
        """

        with self.assertRaises(Exception):
            raise FlipException()

    def test_exception_flip(self):
        """
        Testing Exception Base
        """

        with self.assertRaises(FlipException):
            raise FlipException()

    def test_fliptext(self):
        """
        Flipped text
        """
        flipped = FlipException.flip_text("lala")
        expected = str('(╯°□°）╯︵ ɐꞁɐꞁ')

        self.assertEqual(flipped, expected)
