# mypy: allow-untyped-defs

import unittest
from datetime import date
from datasetmaker.datapackage import DataPackage
import pandas as pd


class TestDatapackage(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        c_frame = pd.DataFrame({
            'country': ['swe', 'ita', None, None],
            'esv_allocation': [None, None, '123', '456'],
            'name': [None, None, 'One', 'Two'],
            'sipri_milexp_cap': [10, 20, None, None],
            'esv_budget': [None, None, 50, 60]
        })
        c_frame.ddf.register_entity('country')
        c_frame.ddf.register_entity('esv_allocation')
        c_frame.ddf.register_datapoints(['esv_budget'], ['esv_allocation'])
        cls.c_package = DataPackage(c_frame)

        n_frame = pd.DataFrame({
            'nobel_laureate': ['pocahontas', 'simba', 'ariel'],
            'nobel_laureate__last_name': ['one', 'two', 'three'],
            'birth.city': ['vien', 'amst', 'rome'],
            'birth.city__name': ['Vienna', 'Amsterdam', 'Rome'],
            'birth.date': [date(2010, 1, 1), date(2011, 2, 2), date(2012, 3, 3)],
            'birth.country': ['aus', 'nld', 'ita'],
            'death.country': ['hun', 'dnk', None],
        })
        n_frame.ddf.register_entity('nobel_laureate')
        n_frame.ddf.register_entity('country')
        n_frame.ddf.register_entity('city')
        cls.n_package = DataPackage(n_frame)

        r_frame = pd.DataFrame({
            'country_flow.country_from': ['swe', 'ita'],
            'country_flow.country_to': ['swe', 'ita'],
            'refugees': [1, 2]
        })
        r_frame.ddf.register_entity('country', roles=['country_from', 'country_to'])
        r_frame.ddf.register_datapoints(
            'refugees', ['country_flow.country_from', 'country_flow.country_to'])
        cls.r_package = DataPackage(r_frame)

    def test_c_package_has_concepts(self):
        self.assertTrue(hasattr(self.c_package, 'concepts'))

    def test_n_package_has_concepts(self):
        self.assertTrue(hasattr(self.n_package, 'concepts'))

    def test_c_package_recursively_added_concepts(self):
        self.assertIn('landlocked', self.c_package.concepts.concept.to_list())

    def test_n_package_added_city_concept_from_composite_birth(self):
        self.assertIn('city', self.n_package.concepts.concept.to_list())

    def test_n_package_added_country_concept(self):
        self.assertIn('country', self.n_package.concepts.concept.to_list())

    def test_n_package_added_country_values_from_both_birth_and_death_composites(self):
        self.assertEqual(sorted(self.n_package.entities['country'].country.to_list()),
                         sorted(['aus', 'dnk', 'hun', 'ita', 'nld']))

    def test_n_package_added_composite_birth_concept(self):
        self.assertIn('birth', self.n_package.concepts.concept.to_list())

    def test_n_package_added_composite_death_concept(self):
        self.assertIn('death', self.n_package.concepts.concept.to_list())

    def test_n_package_has_exact_entities(self):
        actual = sorted(list(self.n_package.entities.keys()))
        expected = sorted(
            ['country', 'city', 'nobel_laureate', 'region4', 'region6'])
        self.assertEqual(actual, expected)

    def test_n_package_city_entity_has_name_column(self):
        self.assertIn('name', self.n_package.entities['city'])

    def test_n_package_laureate_entity_has_Last_name_column(self):
        self.assertIn('last_name', self.n_package.entities['nobel_laureate'])

    def test_all_concepts_headers_are_enumerated_in_c_package(self):
        concepts = self.c_package.concepts.concept.to_list()
        columns = self.c_package.concepts.columns.to_list()
        columns.remove('concept')
        columns.remove('concept_type')
        for column in columns:
            self.assertIn(column, concepts)

    def test_c_package_data_has_correct_shape(self):
        self.assertEqual(self.c_package.data.shape, (4, 5))

    def test_c_package_has_country_entity(self):
        self.assertIn('country', self.c_package.entities)

    def test_c_package_has_region4_entity(self):
        self.assertIn('region4', self.c_package.entities)

    def test_c_package_has_region6_entity(self):
        self.assertIn('region6', self.c_package.entities)

    def test_c_package_has_esv_allocation_entity(self):
        self.assertIn('esv_allocation', self.c_package.entities)

    def test_c_package_has_exact_entities(self):
        self.assertEqual(sorted(list(self.c_package.entities.keys())),
                         ['country', 'esv_allocation', 'region4', 'region6'])

    def test_c_package_has_correct_region4_entity_data(self):
        self.assertEqual(self.c_package.entities['region4'].columns.to_list(),
                         ['region4', 'name', 'slug'])

    def test_c_package_has_correct_region4_entity_shape(self):
        self.assertEqual(self.c_package.entities['region4'].shape, (4, 3))

    def test_c_package_has_datapoints(self):
        self.assertIn('ddf--datapoints--esv_budget--by--esv_allocation.csv',
                      self.c_package.datapoints)

    def test_r_package_creates_country_from_roles(self):
        self.assertFalse(self.r_package.entities['country'].empty)
