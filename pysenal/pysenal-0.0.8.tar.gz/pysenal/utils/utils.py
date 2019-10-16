# -*- coding: UTF-8 -*-
import os
import copy
from collections import Iterable
from decimal import Decimal


def get_chunk(l, n):
    """
    get a chunk in iterable object
    :param l: iterable object
    :param n: chunk size
    :return: a chunk in list type
    """
    if not isinstance(l, Iterable):
        raise TypeError('input value is not iterable')
    if hasattr(l, '__getitem__'):
        for i in range(0, len(l), n):
            yield l[i:i + n]
    else:
        chunk = []
        for i in l:
            chunk.append(i)
            if len(chunk) == n:
                yield chunk
                chunk = []

        if chunk:
            yield chunk


def list2dict(l, key, pop_key=False):
    """
    convert list of dict to dict
    :param l: list of dict
    :param key: key name, which value of dict in list as returned dict key
    :param pop_key: whether pop the key in list of
    :return: assembled dict
    """
    if type(l) not in {list, tuple}:
        raise TypeError('input must in list or tuple type')
    d = {}
    for item in l:
        if not isinstance(item, dict):
            raise TypeError('item {0} is not dict'.format(item))
        if key not in item:
            raise KeyError('key is not in item')
        new_item = copy.deepcopy(item)
        if pop_key:
            new_item.pop(key)
        d[item[key]] = new_item
    return d


def get_filenames_in_dir(dirname,
                         skip_dir=True,
                         skip_hidden_file=True,
                         rm_extname=False,
                         rm_dirname=False):
    """
    get file names in directory, file name in dictionary order
    :param dirname: directory path to get file names
    :param skip_dir: whether skip directory in results
    :param skip_hidden_file: whether skip hidden file in results
    :param rm_extname: whether remove suffix extname in results
    :param rm_dirname: whether remove prefix dirname in results
    :return: scanned file name list, in dictionary order
    """
    filenames = []
    if not os.path.exists(dirname):
        raise FileNotFoundError('directory is not existed.')

    for filename in os.listdir(dirname):
        is_add = True
        if skip_hidden_file and filename.startswith('.') and filename not in {'.', '..'}:
            is_add = False
        if skip_dir and os.path.isdir(os.path.join(dirname, filename)):
            is_add = False
        if is_add:
            filenames.append(filename)

    if not rm_dirname:
        filenames = [os.path.join(dirname, name) for name in filenames]

    if rm_extname:
        new_filenames = []
        for filename in filenames:
            basename = os.path.basename(filename)
            if '.' in basename:
                dot_index = basename.rindex('.')
                if dot_index:
                    filename = filename[:filename.rindex('.')]

            new_filenames.append(filename)
        filenames = new_filenames

    filenames = sorted(filenames)
    return filenames


def index(l, val, default=-1):
    """
    find the index the val in list
    :param l: index list
    :param val: value to find index
    :param default: default value to return that value not in list
    :return: value index in list
    """
    try:
        getattr(l, 'index')
    except:
        raise TypeError('ipnut data doesn\'t support index')
    if val not in l:
        return default
    else:
        return l.index(val)


def json_serialize(obj):
    """
    add serialize method used in json.dumps or json.dump
    :param obj: input obj
    :return: string representation for json.dump or json.dumps
    """
    if isinstance(obj, Decimal):
        return str(obj)
    elif isinstance(obj, bytes):
        return str(obj)
    else:
        try:
            return str(obj)
        except:
            raise TypeError(repr(obj) + ' is not JSON serializable')
