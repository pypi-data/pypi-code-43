# mypy: allow-untyped-defs

import io
import unittest
from unittest.mock import patch, PropertyMock
import pandas as pd
from pandas.api.types import is_numeric_dtype
import datasetmaker as dam
from .mock.mock_data import (
    mock_skv_schema,
    mock_skv_xml,
    mock_frame)


class TestSKVClient(unittest.TestCase):
    def setUp(self):
        """Patch all IO functions."""

        p = 'datasetmaker.clients.skolverket.client.SkolverketClient.schema'
        schema_patcher = patch(p, new_callable=PropertyMock)
        schema = schema_patcher.start()
        schema.return_value = mock_skv_schema
        self.addCleanup(schema_patcher.stop)

        p = 'datasetmaker.clients.skolverket.Table.Table._fetch_xml'
        fetch_patcher = patch(p)
        fetch = fetch_patcher.start()
        fetch.return_value = mock_skv_xml
        self.addCleanup(fetch_patcher.stop)

        p = 'datasetmaker.clients.skolverket.Table.Table._write_table'
        write_patcher = patch(p)
        write_patcher.start()
        self.addCleanup(write_patcher.stop)

        self.client = dam.create_client(source='skolverket')

    def test_list_indicators(self):
        indicators = self.client.indicators
        self.assertIn('skolverket_and_beh_yrk_exklok_tcv139', indicators)

    def test_get_indicators(self):
        data = self.client.get(indicators=['skolverket_sva_andel_hojt_tcv83'], years=[2017])
        self.assertIn('skolverket_sva_andel_hojt_tcv83', data)

    def test_fails_if_wrong_indicator(self):
        with self.assertRaises(ValueError):
            self.client.get(indicators=['does_not_exist'], years=[2015])

    def test_year_not_available(self):
        with self.assertRaises(ValueError):
            self.client.get(indicators=['skolverket_sva_andel_hojt_tcv83'], years=[1576])

    def test_type_conversion(self):
        data = self.client.get(indicators=['skolverket_en_antal_m_betyg_tcv83'],
                               years=[2018])
        self.assertTrue(is_numeric_dtype(data['skolverket_en_antal_m_betyg_tcv83']))

    def test_column_name_standardization(self):
        """Check that `skol_kod` was properly translated to school"""
        data = self.client.get(indicators=['skolverket_en_antal_m_betyg_tcv83'],
                               years=[2017])
        self.assertIn('school_unit', data.reset_index().columns)
