# -*- coding: utf-8 -*-
'''
Manage configuration.
'''
import json
import os
import copy

CONFIG = {}


def get_config():
    '''
    Get the configuration dict object.
    '''
    return CONFIG


def load_config(config_dict=None, config_file=None):
    '''
    Load configuration with the following order:
    1) A dict object from config_dict
    2) A file specified by config_file
    3) dingtalk.json in current directory
    '''
    if config_dict is not None:
        CONFIG.update(copy.copy(config_dict))
        return CONFIG
    if not config_file:
        config_file = "dingtalk.json"
    if not os.path.exists(config_file):
        raise Exception("Config file %s is not existed." % config_file)
    CONFIG.update(json.load(open(config_file)))
    return CONFIG
