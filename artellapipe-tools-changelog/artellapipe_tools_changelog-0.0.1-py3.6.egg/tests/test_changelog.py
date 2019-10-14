#! /usr/bin/env python
# -*- coding: utf-8 -*-

"""
Module that contains tests for artellapipe-tools-changelog
"""

import pytest

from artellapipe.tools.changelog import __version__


def test_version():
    assert __version__.__version__
