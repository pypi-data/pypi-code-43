# -*- coding: utf-8 -*-

from lbdrabbit.tests.auto_inherit_config import LbdFuncConfig

__lbd_func_config__ = LbdFuncConfig(
    timeout=30,
    alias="users"
)


def get(event, context): pass


get.__lbd_func_config__ = LbdFuncConfig(
    alias="rest.users.get"
)


def post(event, context): pass


post.__lbd_func_config__ = LbdFuncConfig(
    timeout=60,
    alias="rest.users.post"
)


def any_(event, context): pass
