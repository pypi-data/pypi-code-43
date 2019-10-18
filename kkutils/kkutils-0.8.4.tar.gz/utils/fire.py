#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
Author: zhangkai
Email: kai.zhang1@nio.com
Last modified: 2019-09-04 13:32:01
'''
import asyncio
import inspect
import sys
from functools import partial

from .config_utils import Config
from .log_utils import Logger


def Fire(component=None, *args, **kwargs):
    opt = Config()
    logger = Logger()
    if inspect.isclass(component):
        module = component(*args, **kwargs)
        func = getattr(module, sys.argv[1])
        params = sys.argv[2:]
    elif inspect.ismethod(component):
        func = partial(component, *args, **kwargs)
        params = sys.argv[1:]
    elif component is None:
        modules = inspect.stack()[1].frame.f_globals
        module = modules[sys.argv[1]]
        if isinstance(module, type):
            module = module()
            func = getattr(module, sys.argv[2])
            params = sys.argv[3:]
        else:
            func = getattr(module, sys.argv[1])
            params = sys.argv[2:]
    else:
        return logger.error(f'type: {type(component)} is unknown')

    ret = func(*params, **opt)
    if inspect.isawaitable(ret):
        loop = asyncio.get_event_loop()
        ret = loop.run_until_complete(ret)
    if ret is not None:
        logger.info(ret)
