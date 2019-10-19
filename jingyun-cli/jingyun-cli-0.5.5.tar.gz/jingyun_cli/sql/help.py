#! /usr/bin/env python
# coding: utf-8

import sys
from functools import partial
from jingyun_cli.util.help import help_value, error_and_exit

__author__ = '鹛桑够'

conf_path_help = {"en": "", "cn": "配置文件所在的路径，默认会读取DB_CONF_PATH这个环境变量"}
dir_help = {"en": "", "cn": "会读取该目录下相应的文件。表结构.json，存储过程.procedure，视图.view，触发器.trigger，函数.function"}
file_help = {"en": "", "cn": "结构描述文件，文件后缀必须满足表结构.json，存储过程.procedure，视图.view，触发器.trigger，函数.function结尾"}
file_prefix_help = {"en": "", "cn": "文件路径前缀，和参数-f一起使用。该参数设置后，-f跟的文件路径全部前面加上该参数后使用"}
create_help = {"en": "", "cn": "根据描述，批量新建表或者存储过程，视图，或者触发器，函数"}
handle_file_help = {"en": "", "cn": "正在处理文件%s"}
skip_file_help = {"en": "", "cn": "跳过文件%s，后缀名不符合要求或者文件名中包含\w以外的字符"}
readonly_help = {"en": "", "cn": "使用只读账户"}

help_keys = filter(lambda x: x.endswith("_help"), locals().keys())
help_dict = dict()
for key in help_keys:
    help_dict[key[:-5]] = locals()[key]


g_help = partial(help_value, help_dict)

