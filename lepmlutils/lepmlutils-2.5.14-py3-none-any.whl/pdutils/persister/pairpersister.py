from .persister import Persister
from typing import List
import pandas as pd

class PairPersister(Persister):
    def __init__(self, data_path: str):
        super().__init__(data_path)

    def save_pair(
        self, 
        name:str, 
        trn: pd.DataFrame, 
        tst: pd.DataFrame,
    ):
        self.save(self.train_name(name), trn)
        self.save(self.test_name(name), tst)

    def overwrite_pair(
        self, 
        name:str, 
        trn: pd.DataFrame, 
        tst: pd.DataFrame,
    ):
        self.overwrite(self.train_name(name), trn)
        self.overwrite(self.test_name(name), tst)

    def load_pair(self, name:str) -> (pd.DataFrame, pd.DataFrame):
        return (
            self.load(self.train_name(name)),
            self.load(self.test_name(name))
        )

    def test_name(self, name:str) -> str:
        return "test-" + name 

    def train_name(self, name:str) -> str:
        return "train-" + name 