import unittest
import os
from crawling_gocd.portal import Portal
from crawling_gocd.outputs import OutputCsv

class PortalTest(unittest.TestCase):
    def setUp(self):
        os.environ["GOCD_SITE"] = "test.com"
        os.environ["GOCD_USER"] = "test_user"
        os.environ["GOCD_PASSWORD"] = "123456"

    def test_new_crawler_correctly(self):
        self.assertIsNotNone(Portal().crawler)

    def test_new_crawler_failed(self):
        os.environ.pop("GOCD_SITE", None)
        os.environ.pop("GOCD_USER", None)
        os.environ.pop("GOCD_PASSWORD", None)
        self.assertRaises(KeyError, Portal)

    def test_new_calculator_correctly(self):
        calculator = Portal().calculator
        self.assertEqual(len(calculator.strategyHandlers), 4)

    def test_new_output_instance_correctly(self):
        self.assertTrue(type(Portal().output) == OutputCsv)

    def test_get_global_time_range_correctly(self):
        self.assertIsNotNone(Portal().getGlobalTimeRange())

    