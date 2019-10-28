import unittest
import os
from sklearn import neighbors
from .internal import *
from .globals import *

class TestHelp(unittest.TestCase):
    def setUp(self):
        pass
        # self.dirname = os.path.dirname(__file__)
        # self.dataset = pd.read_csv(self.dirname + "/resources/train.csv")
        # self.houses = pd.read_csv(self.dirname + "/resources/houses_train.csv")
        # self.houses_test = pd.read_csv(self.dirname + "/resources/houses_t.csv")

    def test_assertions(self):
        df = pd.DataFrame({"a": [3, 4], "b": [5, 6]})
        self.assertFalse(contains(df, "c"))
        df['c'] = 8
        self.assertTrue(contains(df, "c"))







    
