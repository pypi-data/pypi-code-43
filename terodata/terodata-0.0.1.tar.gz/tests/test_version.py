# pylint: disable=C0111 # (no docstrings)
# pylint: disable=C0413 # (allow importing local modules below sys path config)

import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from terodata import __version__


def test_version():
    assert __version__ is not None
