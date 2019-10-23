# -*- coding: utf-8 -*-
'''
Several interface for easily code usage.
'''
from .util.conf import load_config
from .core.token import TokenManager


def get_api_client(config_file=None, config_dict=None, **kwargs):
    from .util.api import client
    config = load_config(config_file=config_file,
                         config_dict=config_dict)
    params = {}
    params.update(config)
    params.update(kwargs)
    manager = TokenManager(**params)
    client.set_manager(manager)
    return client
