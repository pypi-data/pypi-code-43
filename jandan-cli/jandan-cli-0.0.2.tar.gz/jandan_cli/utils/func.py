# -*- coding: utf-8 -*-

from __future__ import absolute_import
import logging
import tempfile
import json
import os

logger = logging.getLogger(__name__)

__all__ = (
    'save_log',
    'is_json',
    'make_dict',
    'get_userinfo',
    'set_userinfo',
    'get_json',
    'set_json',
    'del_json'
)


def save_log(s, dest=None):
    dest = dest or tempfile.mktemp(suffix='.log')
    with open(dest, 'w') as g:
        g.write(s)
    return dest

def make_dict(d, key, value):
    if isinstance(d, dict):
        d[key] = value
        return d
    else:
        return {key: value}

def is_json(s):
    try:
        json.loads(s)
        return True
    except:
        return False

def get_userinfo(config_file):
    if os.path.isfile(config_file):
        with open(config_file, 'r', encoding='utf-8') as f:
            user = {}
            s = f.read()
            if is_json(s):
                user = json.loads(s)
        return user
    return {}

def set_userinfo(config_file, user):
    with open(config_file, 'w', encoding='utf-8') as f:
        f.write(json.dumps(user))
    return user

def set_json(config_file, data):
    old_data = {}
    if os.path.isfile(config_file):
        with open(config_file, 'r', encoding='utf-8') as f:
            s = f.read()
            if is_json(s):
                old_data = json.loads(s)

    new_data = dict(old_data, **data)
    with open(config_file, 'w', encoding='utf-8') as f:
        f.write(json.dumps(new_data))
    return data

def get_json(config_file):
    data = {}
    if os.path.isfile(config_file):
        with open(config_file, 'r', encoding='utf-8') as f:
            s = f.read()
            if is_json(s):
                data = json.loads(s)
    return data

def del_json(config_file, key):
    data = {}
    if os.path.isfile(config_file):
        with open(config_file, 'r', encoding='utf-8') as f:
            s = f.read()
            if is_json(s):
                data = json.loads(s)
            if key in data:
                del data[key]

    with open(config_file, 'w', encoding='utf-8') as f:
        f.write(json.dumps(data))
    return key