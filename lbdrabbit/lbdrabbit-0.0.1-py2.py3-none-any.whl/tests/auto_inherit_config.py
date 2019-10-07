# -*- coding: utf-8 -*-

import attr
from lbdrabbit.lbd_func_config.base import BaseConfig, REQUIRED, NOTHING


@attr.s
class LbdFuncConfig(BaseConfig):
    memory = attr.ib(default=REQUIRED)
    timeout = attr.ib(default=REQUIRED)
    alias = attr.ib(default=NOTHING)
    description = attr.ib(default=NOTHING)

    _default = {
        "memory": 128,
        "timeout": 3,
    }
