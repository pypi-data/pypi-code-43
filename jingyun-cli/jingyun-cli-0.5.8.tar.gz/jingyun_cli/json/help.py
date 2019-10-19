#! /usr/bin/env python
# coding: utf-8

import sys
from functools import partial
from jingyun_cli.util.help import help_value

__author__ = '鹛桑够'


output_help = {"en": "the output of file, default is stdout.", "cn": "输出文件的路径，默认输出到标准输出流"}
json_file_help = {"en": "the path of json file", "cn": "json 文件的路径"}
file_not_exist_help = {"en": "file %s not exist", "cn": "文件%s不存在"}
read_error_help = {"en": "read file %s error", "cn": "读取文件%s失败"}
content_error_help = {"en": "file %s not json content", "cn": "文件%s里的内容不是json格式"}
cover_help = {"en": "whether or not to cover the input file. default is false. the priority is higher than arg -o or "
                    "--output", "cn": "是否覆盖输入文件。默认不覆盖。优先级高于参数-o和--output"}


help_keys = filter(lambda x: x.endswith("_help"), locals().keys())
help_dict = dict()
for key in help_keys:
    help_dict[key[:-5]] = locals()[key]


g_help = partial(help_value, help_dict)


def error_and_exit(msg, error_code=1):
    sys.stderr.write(msg)
    sys.stderr.write("\n")
    sys.exit(error_code)