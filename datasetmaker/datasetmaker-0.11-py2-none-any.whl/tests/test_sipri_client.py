# mypy: allow-untyped-defs

import pathlib
import unittest
from unittest.mock import patch, PropertyMock
import datasetmaker as dam


#@unittest.skip('Skip for now')
class TestSIPRIClient(unittest.TestCase):
    def setUp(self):
        self.client = dam.create_client(source='sipri')
        tests_dir = pathlib.Path(__file__).parent
        url_patcher = patch('datasetmaker.clients.sipri.SIPRI.url',
                            new_callable=PropertyMock)
        mock_url = url_patcher.start()
        mock_url.return_value = tests_dir / 'mock' / 'sipri_test_data.xlsx'
        self.addCleanup(url_patcher.stop)

    def test_sheets_are_present(self):
        data = self.client.get()
        self.assertIn('milexp_cap', data)
        self.assertIn('milexp_gov', data)

    def test_no_missing_countries(self):
        data = self.client.get()
        for key in data:
            self.assertFalse(data[key].country.isnull().any())

    def test_no_missing_years(self):
        data = self.client.get()
        for key in data:
            self.assertFalse(data[key].year.isnull().any())
