# mypy: allow-untyped-defs, no-check-untyped-defs

import unittest
from unittest.mock import patch
import pandas as pd
import datasetmaker as dam
from .mock.mock_wikipedia_data import (
    mock_elections_html,
    mock_visas_html)


@unittest.skip('Skip')
class TestWikipediaClient(unittest.TestCase):
    def setUp(self):
        html_patcher = patch('datasetmaker.clients.wikipedia.fetch_elections')
        html_mock = html_patcher.start()
        html_mock.return_value = mock_elections_html
        self.addCleanup(html_patcher.stop)

    def test_elections_output_is_dataframe(self):
        df = dam.clients.wikipedia.scrape_elections()
        self.assertTrue(type(df) is pd.DataFrame)

    @patch('datasetmaker.clients.wikipedia.fetch_visas')
    def test_visas_output_is_dataframe(self, mock_fetch_visas):
        mock_fetch_visas.return_value = mock_visas_html
        df = dam.clients.wikipedia.scrape_visas()
        self.assertTrue(type(df) is pd.DataFrame)

    @patch('datasetmaker.clients.wikipedia.fetch_visas')
    def test_visas_correct_columns(self, mock_fetch_visas):
        mock_fetch_visas.return_value = mock_visas_html
        df = dam.clients.wikipedia.scrape_visas()
        self.assertIn('wikipedia_visa_country_to', df.columns)
        self.assertIn('wikipedia_visa_country_from', df.columns)
        self.assertIn('wikipedia_visa_requirement', df.columns)
        self.assertIn('wikipedia_visa_allowed_stay', df.columns)
        self.assertIn('wikipedia_visa_reciprocity', df.columns)
