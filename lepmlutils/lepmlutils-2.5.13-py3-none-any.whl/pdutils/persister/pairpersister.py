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
        time_cols: List[str]=None,
    ):
        self.save(self.train_name(name), trn, time_cols)
        self.save(self.test_name(name), tst, time_cols)

    def overwrite_pair(
        self, 
        name:str, 
        trn: pd.DataFrame, 
        tst: pd.DataFrame,
        time_cols: List[str]=None,
    ):
        self.overwrite(self.train_name(name), trn, time_cols)
        self.overwrite(self.test_name(name), tst, time_cols)

    def load_pair(self, name:str) -> (pd.DataFrame, pd.DataFrame):
        return (
            self.load(self.train_name(name)),
            self.load(self.test_name(name))
        )

    def test_name(self, name:str) -> str:
        return "test-" + name 

    def train_name(self, name:str) -> str:
        return "train-" + name 