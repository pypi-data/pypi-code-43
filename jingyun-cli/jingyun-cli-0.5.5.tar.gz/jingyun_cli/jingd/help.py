#! /usr/bin/env python
# coding: utf-8

import sys
from functools import partial
from jingyun_cli import logger
from jingyun_cli.util.help import help_value, error_and_exit, jy_input

__author__ = '鹛桑够'

user_help = {"en": "", "cn": "晶读平台账户名"}
new_password_help = {"en": "", "cn": "要设置的密码，默认为123456"}
action_help = {"en": "", "cn": "reset重置晶读平台密码；lock锁定账户；unlock解除锁定账户；genetic授予访问晶读的权限"}
defect_env_help = {"en": "", "cn": "缺少环境变量%s"}
sample_no_help = {"en": "", "cn": "样本编号必须时数字"}

help_keys = filter(lambda x: x.endswith("_help"), locals().keys())
help_dict = dict()
for key in help_keys:
    help_dict[key[:-5]] = locals()[key]

g_help = partial(help_value, help_dict)

