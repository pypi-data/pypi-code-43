#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Tests for `fx_lib` package."""


import unittest

from fx_lib.zoho_email import Email


class TestZohoEmail(unittest.TestCase):
    """Tests for `fx_lib.zoho_email` package."""

    def setUp(self):
        """Set up test fixtures, if any."""

    def tearDown(self):
        """Tear down test fixtures, if any."""

    def test_000_something(self):
        """Test something."""
        with Email.read_config() as e:
            e.send("Test Title", "Test content")
