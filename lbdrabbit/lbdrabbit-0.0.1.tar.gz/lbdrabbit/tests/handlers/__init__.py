# -*- coding: utf-8 -*-

from lbdrabbit.tests.auto_inherit_config import LbdFuncConfig

__lbd_func_config__ = LbdFuncConfig(
    alias="root"
)
__lbd_func_config__.fill_na_with_default()
