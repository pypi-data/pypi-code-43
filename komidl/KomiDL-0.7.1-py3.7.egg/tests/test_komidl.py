"""Tests the Scraper class in KomiDL"""

import os
import sys
import argparse
import unittest
from unittest import mock

sys.path.append(os.path.abspath('..'))

from komidl.komidl import KomiDL


class KomiDLTest(unittest.TestCase):
    """Tests the KomiDL class in KomiDL"""
    def setUp(self):
        """Create the KomiDL object for usage"""
        self.komidl = KomiDL(None)

    def test_get_extractor_valid(self):
        """Check if the appropriate extractors are returned for valid URLs

        This test re-uses URLs from the extractors to ensure that URLs are
        valid and the expected extractor is correct.
        """
        for extractor in self.komidl._extractors:
            with self.subTest(msg=f"For {extractor.name}EX URLS"):
                tests = extractor.get_tests()

                # Skip if no tests
                if not tests:
                    continue

                for test in tests:
                    actual_extr = self.komidl._get_extractor(test['url'])
                    expected_extr = extractor
                    with self.subTest(msg=f"URL={test['url']}"):
                        self.assertEqual(actual_extr.name, expected_extr.name)
