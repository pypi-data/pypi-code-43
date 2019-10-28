import unittest
import os
import math
from sklearn import neighbors
from .lag import *
from .internal import *
from .globals import *
import warnings


class TestLag(unittest.TestCase):
    def setUp(self):
        pass
        self.dirname = os.path.dirname(__file__)
        self.dataset = pd.read_csv(self.dirname + "/resources/houses_train.csv")
        # self.houses = pd.read_csv(self.dirname + "/resources/houses_train.csv")
        # self.houses_test = pd.read_csv(self.dirname + "/resources/houses_t.csv")
    
    def test_grouping_check(self):
        warnings.filterwarnings("ignore")
        df = pd.DataFrame({
                "day":   [3,  3,  4,  4,  4,  5,   5, 7],
                "price": [99, 21, 77, 32, 32, 109, 7, 8],
                "dist":  [1,  2,  2,  1,  1,  1,   2, 1],
        }, )


        df["hash"] = multi_concat_feat(df, ["dist", "day"])
        self.assertTrue(already_grouped(df, "hash", "price"))

        df = pd.DataFrame({
            "day":   [3,  3,  4,  4,  4,  5,   5, 7],
            "price": [99, 21, 77, 32, 99999, 109, 7, 8],
            "dist":  [1,  2,  2,  1,  1,  1,   2, 1],
        }, )
        df["hash"] = multi_concat_feat(df, ["dist", "day"])
        self.assertFalse(already_grouped(df, "hash", "price"))

        self.dataset = self.dataset.head(800)
        self.dataset["hash"] = multi_concat_feat(self.dataset, ["YrSold", "MSSubClass"])
        self.assertFalse(already_grouped(self.dataset, "hash", "SalePrice"))

        self.dataset['MSP'] = pd.merge(
            self.dataset, 
            self.dataset.groupby(["YrSold", "MSSubClass"]).agg({'SalePrice': ['mean']}),
            on=["YrSold", "MSSubClass"],
            how="left"
        )[('SalePrice', 'mean')]
        self.assertTrue(already_grouped(self.dataset, "hash", "MSP"))

    def test_creatinglag(self):
        df = pd.DataFrame({
                "day":   [3,  3,  4,  4,  4,  5,   5, 7],
                "price": [99, 21, 77, 32, 32, 109, 7, 8],
                "dist":  [1,  2,  2,  1,  1,  1,   2, 1],
        }, )

        lag_name = create_lag(df, "price", "day", 1, ["dist"])

        for col in [hash_col, lagged_time_col, lagged_hash_col]:
            self.assertTrue(not contains(df, col))
        
        self.assertEqual(lag_name, "price-lag1day")    
        self.assertTrue(lag_name in list(df.columns))
        self.assertEqual(4, df.shape[1])
        self.assertEqual(21, df[lag_name][2])
        self.assertEqual(99, df[lag_name][3])
        self.assertEqual(99, df[lag_name][4])
        self.assertEqual(32, df[lag_name][5])
        self.assertEqual(77, df[lag_name][6])

        self.assertTrue(math.isnan(df[lag_name][7]))
        self.assertTrue(math.isnan(df[lag_name][0]))
        self.assertTrue(math.isnan(df[lag_name][1]))


    def test_creating_groupedlags(self):
        warnings.filterwarnings("ignore")
        df = pd.DataFrame({
                "day":   [3,  3, 3,  4,  4,  4,  5],
                "price": [5, 99, 15, 32, 40, 80, 55],
                "dist":  [1,  2,  1, 2,  1,  1,  1,],
        }, )

        lag_names = create_grouped_lags(df, "price", "day", 1, ["dist"])
        self.assertTrue(not contains(df, "dist-pricemean"))
        self.assertEqual(1, len(lag_names)) 
        
        lag_name = lag_names[0]
        self.assertEqual(lag_name, "distday-pricemean-lag1day") 
        self.assertTrue(lag_name in list(df.columns))
        self.assertEqual(4, df.shape[1])
        self.assertEqual(99, df[lag_name][3])
        self.assertEqual(10, df[lag_name][4])
        self.assertEqual(10, df[lag_name][5])
        self.assertEqual(60, df[lag_name][6])

        self.assertTrue(math.isnan(df[lag_name][0]))
        self.assertTrue(math.isnan(df[lag_name][1]))
        self.assertTrue(math.isnan(df[lag_name][2]))




