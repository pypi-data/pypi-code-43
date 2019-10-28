import pandas as pd
from .profile import Profile
from typing import Dict, List
import pickle

class Persister():
    def __init__(self, data_path: str):
        self.__data_path: str = data_path
        self.__frames: Dict[str, Profile] = {}

    def persist(self, path: str):
        f = open(path, "wb" )
        pickle.dump(self, f)
        f.close()

    def save(self, name: str, df: pd.DataFrame):
        if name in self.__frames:
            raise KeyError(f"name {name} is already saved, cannot overwrite implicitly")

        self.__write(name, df)

    def delete(self, name: str):
        if name not in self.__frames:
            raise KeyError(f"name {name} is not already saved, cannot delete")
        
        del self.__frames[name]

    def overwrite(self, name: str, df: pd.DataFrame):
        if name not in self.__frames:
            raise KeyError(f"name {name} is not already saved, cannot overwrite.")

        self.__write(name, df)

    def load(self, name:str) -> pd.DataFrame:
        if name not in self.__frames:
            raise KeyError(f"name {name} does not match any existing saves")

        profile = self.__frames[name]    

        f = open(self.__path_for(name), "rb")
        df = pickle.load(f)
        f.close()

        return df

    def __write(self, name: str, df: pd.DataFrame):     
        f = open(self.__path_for(name), "wb" )
        pickle.dump(df, f)
        f.close()

        self.__frames[name] = Profile(name)

    def __path_for(self, name:str) ->str:
        return self.__data_path + "/" + name + ".pkl"
    
    @classmethod
    def load_from(cls, path: str):
        f = open(path, "rb")
        p = pickle.load(f)
        f.close()
        return p



