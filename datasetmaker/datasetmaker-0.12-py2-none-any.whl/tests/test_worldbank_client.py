# mypy: allow-untyped-defs, no-check-untyped-defs

import unittest
from unittest.mock import patch
import datasetmaker as dam
from .mock.mock_worldbank_data import MockResponse  # type: ignore


class TestWorldBankClient(unittest.TestCase):
    def setUp(self):
        resp_patcher = patch('datasetmaker.clients.worldbank.requests.get')
        mock_resp = resp_patcher.start()
        mock_resp.return_value = MockResponse()
        self.addCleanup(resp_patcher.stop)

        self.client = dam.create_client(source='worldbank')
        self.df = self.client.get(indicators=['worldbank_spdynimrtin'],
                                  periods=[2017])

    def test_has_correct_columns(self):
        self.assertIn('worldbank_spdynimrtin', self.df.columns)
        self.assertIn('year', self.df.columns)
        self.assertIn('country', self.df.columns)

    def test_mapped_correct_country_code(self):
        self.assertIn('arg', self.df.country.tolist())
