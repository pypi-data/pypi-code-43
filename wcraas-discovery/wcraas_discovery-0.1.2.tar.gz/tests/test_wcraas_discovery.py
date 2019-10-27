#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Tests for `wcraas_discovery` package."""

import pytest

from bs4 import BeautifulSoup, Tag
from click.testing import CliRunner
from yarl import URL

from wcraas_discovery import DiscoveryWorker, Config
from wcraas_discovery import cli


def test_command_line_interface():
    """Test the CLI."""
    runner = CliRunner()
    help_result = runner.invoke(cli.main, ['--help'])
    assert help_result.exit_code == 0
    assert '--help  Show this message and exit.' in help_result.output


def test_extract():
    soup = BeautifulSoup(features="html.parser")
    html = soup.new_tag(name="html")
    a_same_origin = soup.new_tag("a", href="https://foo.com/")
    a_no_href = soup.new_tag("a")
    a_other_origin = soup.new_tag("a", href="https://bar.com/")
    a_relative_href = soup.new_tag("a", href="/foo")
    a_other_scheme = soup.new_tag("a", href="tel:+00123412345")
    soup.append(html)
    html.append(a_same_origin)
    html.append(a_no_href)
    html.append(a_other_origin)
    html.append(a_relative_href)
    html.append(a_other_scheme)
    worker = DiscoveryWorker(*Config.fromenv())
    links = worker.extract(soup.prettify(), "https://foo.com/")
    assert "inbound" in links
    assert "outbound" in links
    assert "https://foo.com/" in links["inbound"]
    assert "https://foo.com/foo" in links["inbound"]
    assert "https://bar.com/" in links["outbound"]
    assert "tel:+00123412345" in links["outbound"]
