from .pairpersister import PairPersister
from lepmlutils import pdutils
import os
import pandas as pd
import pickle
import shutil
import unittest

class TestPairPersister(unittest.TestCase):
    def setUp(self):
        self.save_dir = os.path.dirname(__file__) + "/data"
        self.data_dir = os.path.dirname(__file__) + "/resources/"
        os.mkdir(self.save_dir)
    
    def test_no_implicit_overrides(self):
        p = PairPersister(self.save_dir)
        trn = pd.DataFrame({"apples": [2, 3, 4, 5]})
        tst = pd.DataFrame({"apples": [2, 6, 47]})
        self.assertRaises(KeyError, p.overwrite_pair, "apples", trn, tst)
        self.assertRaises(KeyError, p.load_pair, "apples")

        p.save_pair("apples", trn, tst)
        self.assertRaises(KeyError, p.save_pair, "apples", trn, tst)

        trn2, tst2 = p.load_pair("apples")
        self.assertTrue(trn2.equals(trn))
        self.assertTrue(tst2.equals(tst))

        trn3 = pd.DataFrame({"apples": [2, 777, 4, 5]})
        tst3 = pd.DataFrame({"apples": [2, 611, 47]})

        p.overwrite_pair("apples", trn, tst)
        trn2, tst2 = p.load_pair("apples")
        self.assertFalse(trn2.equals(trn3))
        self.assertFalse(tst2.equals(tst3))

    def test_date_cols(self):
        df = pd.read_csv(self.data_dir + "bets.csv")
        self.assertTrue(df["started_at"].dtype == "object")
        
        df["started_at"] = pd.to_datetime(df["started_at"])
        trn, tst = pdutils.split_at_proportion(df, 0.5)
        p = PairPersister(self.save_dir)
        p.save_pair("somename", trn, tst)

        p.save_pair("timed", trn, tst)
        ltrn, ltst = p.load_pair("timed")
        self.assertTrue(ltrn["started_at"].dtype == "datetime64[ns]")
        self.assertTrue(ltst["started_at"].dtype == "datetime64[ns]")

        p.overwrite_pair("timed", trn, tst)
        ltrn, ltst = p.load_pair("timed")
        self.assertTrue(ltrn["started_at"].dtype == "datetime64[ns]")
        self.assertTrue(ltst["started_at"].dtype == "datetime64[ns]")

        ltrn.rename(columns={"started_at": "ts"}, inplace=True)
        ltst.rename(columns={"started_at": "ts"}, inplace=True)
        p.overwrite_pair("timed", ltrn, ltst)
        ltrn, ltst = p.load_pair("timed")
        self.assertTrue(ltrn["ts"].dtype == "datetime64[ns]")
        self.assertTrue(ltst["ts"].dtype == "datetime64[ns]")

        p.overwrite_pair("timed", ltrn, ltst)
        ltrn, ltst = p.load_pair("timed")
        self.assertTrue(ltrn["ts"].dtype == "datetime64[ns]")
        self.assertTrue(ltst["ts"].dtype == "datetime64[ns]")





        

    def tearDown(self):
        shutil.rmtree(self.save_dir)
    
