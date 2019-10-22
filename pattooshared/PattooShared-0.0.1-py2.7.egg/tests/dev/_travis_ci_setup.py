#!/usr/bin/env python3
"""Class used to set test configuration used by unittests."""

# Standard imports
from __future__ import print_function
import sys
import os

# Try to create a working PYTHONPATH
DEV_DIR = os.path.dirname(os.path.realpath(__file__))
ROOT_DIR = os.path.abspath(os.path.join(
    os.path.abspath(os.path.join(DEV_DIR, os.pardir)), os.pardir))
if DEV_DIR.endswith('/pattoo-shared/tests/dev') is True:
    sys.path.append(ROOT_DIR)
else:
    print('''\
This script is not installed in the "pattoo-shared/tests/dev" directory. \
Please fix.''')
    sys.exit(2)


# pattoo libraries
from tests.dev import unittest_setup


def main():
    """Create test configurations."""
    # Check environment
    config = unittest_setup.TestConfig()
    config.create()


if __name__ == '__main__':
    # Do the unit test
    main()
