#! /usr/bin/env python
# -*- coding: utf-8 -*-

"""
Module that contains tests for artellapipe-launcher-plugins-dccselector
"""

import pytest

from artellapipe.launcher.plugins.dccselector import __version__


def test_version():
    assert __version__.__version__
