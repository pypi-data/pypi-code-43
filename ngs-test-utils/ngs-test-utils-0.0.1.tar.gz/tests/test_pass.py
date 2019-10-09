"""Test pass."""
import unittest

import ngs_test_utils


class PassTestCase(unittest.TestCase):
    """Test pass."""

    def test_pass(self):
        """Test pass."""
        self.assertEqual(ngs_test_utils.__doc__, "NGS test utils.")
