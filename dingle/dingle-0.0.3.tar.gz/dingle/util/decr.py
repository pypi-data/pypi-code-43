# -*- coding: utf-8 -*-
import functools


def all_bytes_parameters(func):
    '''
    Convert all the sub parameters to bytes if necessary.
    '''
    @functools.wraps(func)
    def wrapper(*sub):
        new_sub = [i.encode('utf-8') if isinstance(i, str) else i\
                   for i in sub]
        return func(*new_sub)
    return wrapper
