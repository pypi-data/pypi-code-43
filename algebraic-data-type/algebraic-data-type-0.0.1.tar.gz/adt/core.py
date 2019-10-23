from pampy import match, _
from dataclasses import dataclass
from typing import TypeVar, Generic
T = TypeVar('T')

class Matcher:
    def __init__(self):
        self.pattern = []
    
    def __setitem__(self, pat, method):
        self.pattern.append(pat)
        self.pattern.append(method)
        
    def __call__(self, *x):
        if len(x)==1:
            x = x[0]
        return match(x, *self.pattern)
    

class Multimethod:
    
    def __init__(self):
        pass
    
    def __enter__(self):
        return Matcher()
    
    def __exit__(self, exc_type, exc_value, exc_traceback):
        pass

class Case:
    
    def __init__(self,**kwargs):
        self.slot = kwargs
        
        
class ADTMeta(type):
       
    def __init__(cls, clsname, bases, clsdict):
        annot = clsdict["__annotations__"]
        for name in list(annot.keys()):
            try:
                d = annot[name].slot
                t = dataclass(type(name, (cls,), {"__annotations__":d}))
                setattr(cls, name, t)
            except AttributeError:
                pass
        super().__init__(clsname, bases, clsdict)