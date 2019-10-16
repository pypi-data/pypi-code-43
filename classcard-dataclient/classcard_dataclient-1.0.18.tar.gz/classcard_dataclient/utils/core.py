# -*- coding: utf-8 -*-
"""
Created By Murray(m18527) on 2019/9/9 20:24
"""
from __future__ import absolute_import, unicode_literals

import os
import sys

from .loggerutils import logging

logger = logging.getLogger(__name__)


def import_module(import_name):
    import_name = str(import_name).replace(':', '.')
    try:
        try:
            __import__(import_name)
        except ImportError:
            if '.' not in import_name:
                raise
        else:
            return sys.modules[import_name]
        module_name, obj_name = import_name.rsplit('.', 1)
        try:
            module = __import__(module_name, None, None, [obj_name])
        except ImportError:
            module = import_module(module_name)
        try:
            return getattr(module, obj_name)
        except AttributeError as e:
            raise ImportError(e)
    except ImportError as e:
        logger.error("Error, import module <{}> fail, Detail: {}".format(import_name, e))


config_module = os.getenv("DATA_CLIENT_CONFIG_MODULE", "classcard_dataclient.settings")


class Config(dict):
    def __init__(self, defaults=None):
        dict.__init__(self, defaults or {})
        self.from_obj(config_module)

    def from_obj(self, obj=None):
        obj = import_module(obj)
        for key in dir(obj):
            if key.isupper():
                self[key] = getattr(obj, key)


config = Config()
