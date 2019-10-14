# tests
# conduit package tests
#
# Author:   Benjamin Bengfort <benjamin@pingthings.io>
# Created:  Tue Apr 23 18:04:26 2019 -0400
#
# Copyright (C) 2019 PingThings, Inc. and Kevin D. Jones
# For license information, see LICENSE.txt
#
# ID: __init__.py [] benjamin@bengfort.com $

"""
Conduit package tests.
"""

##########################################################################
## Imports
##########################################################################

import pytest

##########################################################################
## Test Constants
##########################################################################

EXPECTED_VERSION = "1.0"


##########################################################################
## Initialization Tests
##########################################################################

class TestInitialization(object):

    def test_sanity(self):
        """
        Test that tests work by confirming 2**3 = 8
        """
        assert 2**3==8, "The world went wrong!!"

    def test_import(self):
        """
        Assert that the conduit package can be imported.
        """
        try:
            import conduit
        except ImportError:
            pytest.fail("Could not import the conduit library!")

    def test_version(self):
        """
        Assert that the test version matches the library version.
        """
        try:
            import conduit
            assert conduit.__version__ == EXPECTED_VERSION
        except ImportError:
            pytest.fail("Could not import the conduit library!")
