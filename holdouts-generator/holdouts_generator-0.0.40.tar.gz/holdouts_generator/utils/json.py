from typing import Dict
import json

__all__ = ["load", "dump"]

def load(path:str)->Dict:
    with open(path, "r") as f:
        return json.load(f)

def dump(obj, path:str):
    with open(path, "w") as f:
        json.dump(obj, f)
