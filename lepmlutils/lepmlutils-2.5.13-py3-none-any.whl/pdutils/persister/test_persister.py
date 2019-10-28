from .persister import Persister
import os
import pandas as pd
import pickle
import shutil
import unittest

class TestPersister(unittest.TestCase):
    def setUp(self):
        self.save_dir = os.path.dirname(__file__) + "/data"
        self.data_dir = os.path.dirname(__file__) + "/resources/"
        os.mkdir(self.save_dir)
    
    def test_no_implicit_overrides(self):
        p = Persister(self.save_dir)
        set1 = pd.DataFrame({"apples":[2, 3,3, 4]})
        self.assertRaises(KeyError, p.load, "somename")
        self.assertRaises(KeyError, p.overwrite, "somename", set1)

        p.save("somename", set1)
        self.assertRaises(KeyError, p.save, "somename", set1)

        df = p.load("somename")
        self.assertTrue(df.equals(set1))
        self.assertRaises(KeyError, p.load, "othername")
        self.assertRaises(KeyError, p.overwrite, "othername", set1)

        set2 = pd.DataFrame({"apples":[111, 3,3, 4]})
        p.overwrite("somename", set2)
        df = p.load("somename")
        self.assertFalse(df.equals(set1))
        self.assertTrue(df.equals(set2))

    def test_delete(self):
        p = Persister(self.save_dir)
        set1 = pd.DataFrame({"apples":[2, 3,3, 4]})

        self.assertRaises(KeyError, p.delete, "somename")

        p.save("somename", set1)
        self.assertRaises(KeyError, p.save, "somename", set1)
        self.assertRaises(KeyError, p.delete, "othername")

        p.delete("somename")
        p.save("somename", set1)

    def test_date_persisting(self):
        p = Persister(self.save_dir)
        df = pd.read_csv(self.data_dir + "bets.csv")
        self.assertTrue(df["started_at"].dtype == "object")
        df["started_at"] = pd.to_datetime(df["started_at"])
        p.save("somename", df)

        self.assertTrue(df["started_at"].dtype == "datetime64[ns]")

        p.save("timed", df, ["started_at"])
        loaded = p.load("timed")
        self.assertTrue(loaded["started_at"].dtype == "datetime64[ns]")
        self.assertRaises(AssertionError, p.save, "timed2", df, ["non_existant"])
        self.assertRaises(AssertionError, p.save, "timed2", df, ["origin"])

        # overwriting without passing in time cols reverts to old
        # time cols
        p.overwrite("timed", df)
        loaded = p.load("timed")
        self.assertTrue(loaded["started_at"].dtype == "datetime64[ns]")

        p.overwrite("timed", df, [])
        loaded = p.load("timed")
        print(loaded["started_at"].dtype)
        self.assertTrue(loaded["started_at"].dtype == "datetime64[ns]")

    def test_pickling(self):
        p = Persister(self.save_dir)
        set1 = pd.DataFrame({"apples":[2, 3,3, 4]})
        p.save("somename", set1)

        save_path = self.save_dir + "/persister.pkl"
        p.persist(save_path)
        q = Persister.load_from(save_path)
        df = q.load("somename")
        self.assertTrue(df.equals(set1))

    def tearDown(self):
        shutil.rmtree(self.save_dir)
    
