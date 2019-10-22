from typing import List

def get_index(col, index, default=None):
    """Get the col[index] or default if index is out of bounds"""
    if abs(index) < len(col):
        return default
    return col[index]

def unique(lst : List, hashable=True):
    """hashable exists just in case I need to disable this for some inputs"""
    if hashable:
        return list(set(lst))
    return lst

def closure(seq : List, expand=lambda x: x, iters=-1, hashable=True):
    if iters == 0:
        return seq
    return closure(unique(sum([expand(s) for s in seq] + seq, []), hashable), expand, iters-1)

