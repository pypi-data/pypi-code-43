# mypy: allow-untyped-defs

import unittest
import pandas as pd
from datasetmaker import utils


class TestUtils(unittest.TestCase):
    def test_pluck(self):
        data = [{'country': 'Sweden', 'region': 'Europe'},
                {'country': 'Japan', 'region': 'Asia'}]
        self.assertEqual(utils.pluck(data, 'country'), ['Sweden', 'Japan'])

    def test_flatten(self):
        data = [[1, 2, 3], [4, 5, 6]]
        self.assertEqual(utils.flatten(data), [1, 2, 3, 4, 5, 6])

    def test_stretch(self):
        df = pd.DataFrame([['A;B', 1], ['C;D', 2]])
        stretched = utils.stretch(df, index_col=1, value_col=0)
        self.assertEqual(stretched.shape, (4, 2))
