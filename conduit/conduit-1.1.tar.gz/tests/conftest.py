# tests.conftest
# Provides pytest configuration and fixtures that are global to all tests.
#
# Author:   Benjamin Bengfort <benjamin@pingthings.io>
# Created:  Tue Jun 25 16:47:59 2019 -0400
#
# Copyright (C) 2019 PingThings, Inc. and Kevin D. Jones
# For license information, see LICENSE.txt
#
# ID: conftest.py [] benjamin@bengfort.com $

"""
Provides pytest configuration and fixtures that are global to all tests.
"""

##########################################################################
## Imports
##########################################################################

import pytest

from btrdb import BTrDB
from .fixtures import FixtureEndpoint


##########################################################################
## BTrDB Database with Fixtures Endpoint
##########################################################################

@pytest.fixture(scope="session")
def db():
    """
    Provides a BTrDB connection whose endpoint is a mocked FixtureEndpoint
    that returns data from the test directory rather than via grpc.
    """
    return BTrDB(FixtureEndpoint())