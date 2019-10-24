# mypy: allow-untyped-defs

import unittest
import pandas as pd
import datasetmaker  # noqa, needed to register accessor


class TestDDFAccessor(unittest.TestCase):
    def test_entity_is_registered(self):
        df = pd.DataFrame([{'population': 1, 'country': 'swe'},
                           {'population': 2, 'country': 'nor'}])
        df.ddf.register_entity('country')
        self.assertIn('country', df.ddf.entities)

    def test_property_is_registered_with_parameter(self):
        df = pd.DataFrame([{'population': 1, 'country': 'swe', 'capital': 'stockholm'},
                           {'population': 2, 'country': 'nor', 'capital': 'oslo'}])
        df.ddf.register_entity('country', props=['capital'])
        self.assertIn('capital', df.ddf.properties['country'])

    def test_property_is_registered_with_function(self):
        df = pd.DataFrame([{'population': 1, 'country': 'swe', 'capital': 'stockholm'},
                           {'population': 2, 'country': 'nor', 'capital': 'oslo'}])
        df.ddf.register_entity('country')
        df.ddf.register_property('capital', 'country')
        self.assertIn('capital', df.ddf.properties['country'])

    def test_entity_frame_is_created(self):
        df = pd.DataFrame([{'population': 1, 'country': 'swe', 'capital': 'stockholm'},
                           {'population': 2, 'country': 'nor', 'capital': 'oslo'}])
        df.ddf.register_entity('country', props=['capital'])
        self.assertIsInstance(df.ddf.create_entity_frame('country'), pd.DataFrame)

    def test_datapoints_are_registered(self):
        df = pd.DataFrame([{'population': 1, 'country': 'swe', 'capital': 'stockholm'},
                           {'population': 2, 'country': 'nor', 'capital': 'oslo'}])
        df.ddf.register_entity('country', props=['capital'])
        df.ddf.register_datapoints('population', 'country')
        self.assertIn((['population'], ['country']), df.ddf.datapoints)
