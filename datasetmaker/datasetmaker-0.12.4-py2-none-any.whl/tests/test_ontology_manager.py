# mypy: allow-untyped-defs

import unittest
import pandas as pd
from datasetmaker.onto import manager
from datasetmaker.exceptions import EntityNotFoundException


class TestOntologyManager(unittest.TestCase):
    def test_read_concepts_returns_frame(self):
        concepts = manager.read_concepts()
        self.assertIs(type(concepts), pd.core.frame.DataFrame)

    def test_read_concepts_can_filter(self):
        concepts = manager.read_concepts(*['year', 'party'])
        self.assertTrue(concepts.shape[0] == 2)

    def test_read_entity_returns_frame(self):
        frame = manager.read_entity('country')
        self.assertIs(type(frame), pd.core.frame.DataFrame)

    def test_entity_exists(self):
        self.assertFalse(manager.entity_exists('zuwbing11'))
        self.assertTrue(manager.entity_exists('country'))

    def test_sid_to_id(self):
        mapping = manager.sid_to_id(source='nobel')
        self.assertIs(type(mapping), dict)
        self.assertEqual(mapping['motivation'], 'nobel_motivation')

    def test_id_to_sid(self):
        mapping = manager.id_to_sid(source='nobel')
        self.assertIs(type(mapping), dict)
        self.assertEqual(mapping['nobel_motivation'], 'motivation')

    def test_id_to_name(self):
        mapping = manager.id_to_name(source='nobel')
        self.assertIs(type(mapping), dict)
        self.assertEqual(mapping['nobel_motivation'], 'Nobel prize motivation')

    def test_map(self):
        country_to_iso3 = manager._map('country', 'iso3', 'name', include_synonyms=False)
        self.assertEqual(country_to_iso3['aus'], 'Australia')

    def test_entity_dict_raises(self):
        ent_dict = manager.EntityDict('country', {'afg': 'Afghanistan'})
        with self.assertRaises(EntityNotFoundException):
            ent_dict['swe']
