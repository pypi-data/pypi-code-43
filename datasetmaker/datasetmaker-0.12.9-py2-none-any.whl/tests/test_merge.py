# mypy: allow-untyped-defs

import shutil
import unittest
import pathlib
import pandas as pd
from datasetmaker.merge import merge_packages


ddf_dir = pathlib.Path(__file__).parent / 'ddf'


class TestMerge(unittest.TestCase):
    def setUp(self):
        self.dir = pathlib.Path(__file__).parent / 'ymerge_test_dir1kvx'
        merge_packages([ddf_dir / 'worldbank', ddf_dir / 'oecd'], self.dir)

    def test_no_duplicate_entities(self):
        countries = pd.read_csv(self.dir / 'ddf--entities--country.csv')
        self.assertFalse(countries.country.duplicated().any())

    @unittest.skip('We dont care about this for now, see https://github.com/pandas-dev/pandas/issues/29026')
    def test_lowercase_booleans(self):
        countries = pd.read_csv(self.dir / 'ddf--entities--country.csv', dtype={'landlocked': str})
        countries = countries[countries.landlocked.notnull()]
        self.assertSequenceEqual(list(countries.landlocked),
                                 list(countries.landlocked.str.lower()))

    def tearDown(self):
        shutil.rmtree(self.dir)
