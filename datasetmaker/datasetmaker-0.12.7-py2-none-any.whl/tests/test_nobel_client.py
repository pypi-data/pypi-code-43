# mypy: allow-untyped-defs

import unittest
from unittest.mock import patch
import datasetmaker as dam
import pandas as pd
from .mock.mock_nobel_data import MockResponse


class TestNobelClient(unittest.TestCase):
    def setUp(self):
        resp_patcher = patch('datasetmaker.clients.nobel.requests.get')
        mock_resp = resp_patcher.start()
        mock_resp.return_value = MockResponse()
        self.addCleanup(resp_patcher.stop)

        self.client = dam.create_client(source='nobel')
        self.df = self.client.get()

    def test_has_correct_columns(self):
        self.assertIn('birth.city', self.df.columns)

    def test_mapped_correct_country_code(self):
        self.assertIn('prus', self.df['birth.country'].tolist())

    def test_mapped_non_existing_country_is_none(self):
        self.assertTrue(self.df['birth.country'].isnull().any())

    def test_clean_country_col(self):
        data = pd.DataFrame({
            'born': ['Prussia', 'Scotland'],
            'died': ['Russia', 'Britain']
        })
        born_country = self.client._clean_country_col(data.born)
        self.assertFalse(born_country.str.contains('Scotland').any())
