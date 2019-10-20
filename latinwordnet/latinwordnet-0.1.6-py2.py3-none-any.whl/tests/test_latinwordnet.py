#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Tests for `latinwordnet` package."""


import unittest
from latinwordnet import LatinWordNet


class TestQueryTypes(unittest.TestCase):
    """Tests for `latinwordnet` package."""

    def setUp(self):
        """Set up test fixtures, if any."""

    def tearDown(self):
        """Tear down test fixtures, if any."""

    def test_latinwordnet(self):
        """Test the Latin WordNet API."""

        LWN = LatinWordNet()
        assert next(LWN.index())
