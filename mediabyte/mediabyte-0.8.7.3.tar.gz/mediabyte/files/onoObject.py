import json
from . import cnf

class MediabyteHashObj(dict):
    
    def __init__(self):
        filename = cnf.hash_dict_path
        with open(filename, 'r') as f:
            hash_dict = json.load(f)
        for key, value in hash_dict.items():
            self[key] = value


    def __getattribute__(self, key):
        try:
            return self[key]
        except KeyError:
            raise AttributeError(key)


    def __setattr__(self, key, value):
        self[key] = value
    
    
    