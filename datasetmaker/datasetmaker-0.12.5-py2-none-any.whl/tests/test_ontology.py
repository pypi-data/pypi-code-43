# mypy: allow-untyped-defs, no-check-untyped-defs

import unittest
from datasetmaker.onto.manager import read_concepts
from datasetmaker.onto.schemas import schema_registry


class TestOntology(unittest.TestCase):
    def test_every_entity_domain_has_schema(self):
        concepts = read_concepts()
        domains = concepts[concepts.concept_type == 'entity_domain']
        domains = sorted(domains.concept.to_list())
        schemas = sorted(list(schema_registry.all().keys()))
        self.assertEqual(domains, schemas)

    def test_no_duplicate_concepts(self):
        concepts = read_concepts()
        self.assertFalse(concepts.concept.duplicated().any())

    def test_all_concepts_have_required_fields(self):
        concepts = read_concepts()
        have_concept = concepts.concept.notnull().all()
        have_concept_type = concepts.concept_type.notnull().all()
        have_name = concepts.name.notnull().all()
        self.assertTrue(all([have_concept, have_concept_type, have_name]))

    def test_all_properties_are_enumerated_concepts(self):
        concepts = read_concepts().concept.to_list()
        props = []
        for name, schema in schema_registry.all().items():
            for value in list(schema.keys()):
                if '.' in value:
                    props.extend(value.split('.'))
                else:
                    props.append(value)
        self.assertTrue(all([x in concepts for x in props]))
