#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Tests for `deploy_py` package."""


import unittest
from click.testing import CliRunner

from deploy_py import deploy_py
from deploy_py import cli


class TestDeployPy(unittest.TestCase):
    """Tests for `deploy_py` package."""

    def setUp(self):
        """Set up test fixtures, if any."""

    def tearDown(self):
        """Tear down test fixtures, if any."""

    def test_000_something(self):
        """Test something."""

    def test_command_line_interface(self):
        """Test the CLI."""
        runner = CliRunner()
        result = runner.invoke(cli.deploy)
        assert result.exit_code == 0
        assert 'deploy_py.cli.main' in result.output
        help_result = runner.invoke(cli.deploy, ['--help'])
        assert help_result.exit_code == 0
        assert '--help  Show this message and exit.' in help_result.output
