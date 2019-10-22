"""
A bunch functions that would make my life easier
"""

import os, re, soul
import json as _json

def ls_(p=".", pattern=".*", depth=0):
    # 1. If it is a file, return a list containing the file
    # 2. If it is a directory return all contents to depth 
    # 3. Filter results by pattern
    cands = []
    if os.path.isfile(p):
        cands = [p]
    elif os.path.isdir(p):
        cands = os.listdir(p)
        cands = [c for c in cands if re.match(pattern, c)]
        while depth > 0:
            depth = depth - 1
            cands = sum([ls(c, pattern, depth) for c in cands], [])
            cands = [c for c in cands if re.match(pattern, c)]
    else:
        return []
    return cands

def ls(p=".", pattern=".*", depth=0):
    return [os.path.join(p, x) for x in ls_(p, pattern, depth)]

def json(file_):
    if type(file_) is str:
        with open(file_) as f:
            return _json.load(f)
    else:
        return _json.load(file_)

def dump_json(data, file_):
    if type(file_) is str:
        file_ = open(file_, 'w')
    _json.dump(data, file_, indent=2)
    file_.close()

def jsons(string):
    return _json.loads(string)
