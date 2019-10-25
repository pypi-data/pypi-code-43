# mypy: allow-untyped-defs

import unittest
from unittest.mock import patch, PropertyMock
import datasetmaker as dam
from datasetmaker.path import ROOT_DIR
import pandas as pd


class TestValforskClient(unittest.TestCase):
    def setUp(self):
        url_patcher = patch('datasetmaker.clients.valforsk.ValforskClient.url',
                            new_callable=PropertyMock)
        mock_url = url_patcher.start()
        mock_url.return_value = ROOT_DIR.parent / 'tests/mock/valforskdata.zip'
        self.addCleanup(url_patcher.stop)

        raw_patcher = patch('datasetmaker.clients.valforsk.ValforskClient._fetch_issues')
        mock_raw = raw_patcher.start()
        mock_raw.return_value = pd.DataFrame({
            'valforsk_source': ['snes', 'snes'],
            'valforsk_issue': ['snes_frihet_for_enskilda', 'snes_homosexuella_adoptera'],
            'valforsk_issue__name': ['Mer frihet för enskilda', 'Låta homosexuella adoptera'],
            'year': [1991, 1991],
            'party': ['v', 's'],
            'valforsk_issue_position': [59.0, 58.0]
        })
        self.addCleanup(raw_patcher.stop)

        self.client = dam.create_client(source='valforsk')
        self.data = self.client.get()

    def test_unzips_and_loads_data(self):
        self.assertEqual(type(self.data), list)
        self.assertEqual(type(self.data[0]), pd.core.frame.DataFrame)
        self.assertEqual(type(self.data[1]), pd.core.frame.DataFrame)
