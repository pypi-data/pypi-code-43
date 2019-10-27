#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Tests for `wcraas_storage` package."""

import pytest

from click.testing import CliRunner

from wcraas_storage import wcraas_storage
from wcraas_storage import cli


def test_command_line_interface():
    """Test the CLI."""
    runner = CliRunner()
    help_result = runner.invoke(cli.main, ['--help'])
    assert help_result.exit_code == 0
    assert '--help  Show this message and exit.' in help_result.output
