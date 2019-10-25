from __future__ import annotations
from typing import List, Optional
from abc import ABC, abstractmethod
import random
import string
from collections import OrderedDict


class Getter(ABC):
    def __init__(self):
        self.name: str = "_"
        
    @abstractmethod
    def get(self, name: str, make: bool = False) -> Optional[Getter]:
        pass
    

class Col(Getter):
    
    def __init__(self):
        super().__init__()
        self.docs: List[Doc] = []

    def get(self, name: str, make: bool = False) -> Optional[Getter]:
        for i in self.docs:
            if i.name == name:
                return i
        if make is False:
            return None
        else:
            d = Doc()
            d.name = name
            self.docs.append(d)
            return d


class Doc(Getter):
    
    def __init__(self):
        super().__init__()
        self.data: Optional[OrderedDict] = None
        self.cols: List[Col] = []
    
    def __getitem__(self, key):
        if self.data is not None:
            # TODO: **implement** field_path firestore language
            return self.data.get(key)
    
    def get(self, name: str, make: bool = False) -> Optional[Getter]:
        for i in self.cols:
            if i.name == name:
                return i
        if make is False:
            return None
        else:
            c = Col()
            c.name = name
            self.cols.append(c)
            return c


class _DatabaseRaw:
    def __init__(self):
        
        self.__database__: List[Col] = []
    
    @property
    def database(self):
        return self.__database__
    
    def get_or_create_correct_col(self, name: str) -> Col:
        for col in self.__database__:
            if col.name == name:
                return col
        
        c = Col()
        c.name = name
        self.__database__.append(c)
        return c
    
    def search_path(self, path: List[str], make: bool = False) -> Getter:
        _path = path.copy()
        global_col = _path.pop(0)
        col: Getter = self.get_or_create_correct_col(global_col)
        
        for i in _path:
            col = col.get(i, make)
            if col is None:
                break
        
        return col
    
    @staticmethod
    def random_id(n=20):
        return ''.join(random.choice(string.ascii_lowercase) for _ in range(n))
