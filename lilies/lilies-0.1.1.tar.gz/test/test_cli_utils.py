#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import unittest
import os
from lilies import grow, wilt, bordered


class TestCliUtils(unittest.TestCase):
    def setUp(self):
        self.string = "hey"
        self.lilystring = grow("hey", "red")
        self.lilyblock = grow(["quick", "brown", "fox"], "blue")

    def test_bordered_python_string(self):
        control = os.linesep.join(["┌───┐", "│hey│", "└───┘"])
        test = bordered(self.string)
        self.assertEqual(control, wilt(test))

    def test_bordered_lilystring(self):
        control = os.linesep.join(["┌───┐", "│hey│", "└───┘"])
        test = bordered(self.lilystring)
        self.assertEqual(control, wilt(test))

    def test_bordered_lilyblock(self):
        control = os.linesep.join(
            ["┌─────┐", "│quick│", "│brown│", "│fox  │", "└─────┘"]
        )
        test = bordered(self.lilyblock)
        self.assertEqual(control, wilt(test))
