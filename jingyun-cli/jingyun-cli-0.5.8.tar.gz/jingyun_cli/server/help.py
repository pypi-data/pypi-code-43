#! /usr/bin/env python
# coding: utf-8

import sys
from functools import partial
from jingyun_cli import logger
from jingyun_cli.util.help import help_value, error_and_exit

__author__ = '鹛桑够'

server_help = {"en": "", "cn": "使用服务预定义端口号列表"}
port_help = {"en": "", "cn": "要检测的端口号"}

help_keys = filter(lambda x: x.endswith("_help"), locals().keys())
help_dict = dict()
for key in help_keys:
    help_dict[key[:-5]] = locals()[key]

g_help = partial(help_value, help_dict)

