#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
Auxiliary functions
author: Valentyn Stadnytskyi
created: Sept 9 2019

"""
__vesrion__ = '0.0.0'

def save_to_file(filename,object,):
    """
    save a python object to a file

    Parameters
    ----------
    Args:
        filename (string)
            the full path and filename
        object (python object)
            a python object

    Returns
    -------

    Examples
    --------
    the example of usage

    >>> save_to_file('test.pkl',[1,2,3])
    """
    from pickle import dump
    with open(filename,"wb") as f:
        dump(object,f)

def load_from_file(filename):
    """
    read object from a file

    Parameters
    ----------
    filename : string
        the full path and filename

    Returns
    -------
    object : object
        input object to save.

    Examples
    --------
    the example of usage

    >>> list_out = load_from_file('list.extension')

    """
    from pickle import load
    with open(filename,'rb') as f:
        data = load(f, encoding='bytes')
    return data
