# mypy: allow-untyped-defs

import unittest
import pathlib
import collections
import pandas as pd
import datasetmaker as dam


ddf_dir = pathlib.Path(__file__).parent / 'ddf'


@unittest.skip('Skip')
class TestMerge(unittest.TestCase):
    def setUp(self):
        self.worldbank = dam.merge.DDFPackage(ddf_dir / 'worldbank')
        self.oecd = dam.merge.DDFPackage(ddf_dir / 'oecd')
        self.collection = dam.merge.DDFPackageCollection([self.worldbank.path,
                                                          self.oecd.path])

    def test_package_read_entity(self):
        entity_frame = self.worldbank.read_entity('country')
        self.assertEqual(entity_frame.shape, (195, 1))
        self.assertEqual(list(entity_frame.columns), ['country'])

    def test_package_list_datafiles(self):
        exp = ['ddf--datapoints--worldbank_sp.dyn.imrt.in--by--country--year',
               'ddf--datapoints--worldbank_sp.dyn.le00.in--by--country--year']
        self.assertEqual(self.worldbank.list_datafiles(), exp)

    def test_package_list_entities(self):
        exp = ['country']
        self.assertEqual(self.worldbank.list_entities(), exp)

    def test_package_has_meta(self):
        self.assertIsInstance(self.worldbank.meta, collections.OrderedDict)

    def test_package_read_concepts(self):
        concepts = self.worldbank.read_concepts()
        self.assertIsInstance(concepts, pd.DataFrame)
        self.assertEqual(concepts.shape, (4, 3))
        self.assertEqual(list(concepts.columns),
                         ['concept', 'concept_type', 'name'])

    def test_packages_list_datafiles(self):
        exp = ['ddf--datapoints--worldbank_sp.dyn.imrt.in--by--country--year',
               'ddf--datapoints--worldbank_sp.dyn.le00.in--by--country--year',
               'ddf--datapoints--oecd_lifeexpy_g1--by--country--year']
        self.assertEqual(self.collection.list_datafiles(), exp)

    def test_packages_list_distinct_entities(self):
        exp = set()  # type: ignore
        self.assertEqual(self.collection.list_distinct_entities(), exp)

    def test_packages_list_shared_entities(self):
        exp = {'country'}
        self.assertEqual(self.collection.list_shared_entities(), exp)

    def test_packages_create_common_concepts(self):
        concepts = self.collection.create_common_concepts_frame()
        self.assertIsInstance(concepts, pd.DataFrame)
        self.assertEqual(concepts.shape, (5, 3))
        self.assertEqual(list(concepts.columns),
                         ['concept', 'concept_type', 'name'])

    def test_packages_create_datapoint_frame(self):
        fname = 'ddf--datapoints--worldbank_sp.dyn.imrt.in--by--country--year'
        frame = self.collection.create_datapoint_frame(fname)
        self.assertEqual(frame.shape, (1096, 3))
        self.assertIn('worldbank_sp.dyn.imrt.in', frame.columns)

    def test_create_entity_frame(self):
        frame = self.collection.create_entity_frame('country')
        self.assertIn('country', frame.columns)
        self.assertIn('name', frame.columns)
        self.assertIn('un_state', frame.columns)
        self.assertFalse(frame.name.isnull().any())
        self.assertFalse(frame.country.duplicated().any())
