# mypy: allow-untyped-defs

import pathlib
import unittest
from unittest.mock import patch, PropertyMock
import datasetmaker as dam


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
        self.assertIn('sipri_milexp_cap', data[0]['data'])
        self.assertIn('sipri_milexp_gov', data[1]['data'])

    def test_no_missing_countries(self):
        data = self.client.get()
        for dataset in data:
            self.assertFalse(dataset['data'].country.isnull().any())

    def test_no_missing_years(self):
        data = self.client.get()
        for dataset in data:
            self.assertFalse(dataset['data'].year.isnull().any())
