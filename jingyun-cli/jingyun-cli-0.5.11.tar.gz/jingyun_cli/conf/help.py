#! /usr/bin/env python
# coding: utf-8

import sys
from functools import partial
from jingyun_cli.util.help import help_value

__author__ = '鹛桑够'

conf_file_help = {"en": "the path of conf file", "cn": "配置文件的路径"}
file_not_exist_help = {"en": "file %s not exist", "cn": "文件%s不存在"}
read_error_help = {"en": "read file %s error", "cn": "读取文件%s失败"}
write_error_help = {"en": "rewrite file %s error", "cn": "重写文件%s失败"}
mode_help = {"en": "1 use str.format(os.environ),2 use str %% os.environ",
             "cn": "1代表使用str.format(os.environ)，2代表使用str %% os.environ"}
directory_help = {'en': '', 'cn': "遍历目录下所有文件，可与参数-p -e -f一起使用，筛选目录下文件"}
filter_help = {"en": "", "cn": "筛选条件，正则表达式，根据筛选条件进行match操作.-d存在时有效"}
prefix_help = {"en": "", "cn": "文件名开头，根据根据文件开头筛选目录中的文件.-d存在时有效"}
end_help = {"en": "", "cn": "文件名结尾，根据根据文件结尾筛选目录中的文件.-d存在时有效"}
section_help = {"en": "", "cn": "要查询的配置文件的哪部分"}
section_not_found_help = {"en": "", "cn": "要查询的配置文件%s部分不存在"}
option_help = {"en": "", "cn": "要查询的配置选项名"}
option_not_found_help = {"en": "", "cn": "要查询的配置选项%s不存在"}
ignore_error_help = {"end": "", "cn": "遇到错误如配置不存在，配置项不存在时，不报错仅打印信息"}


help_keys = filter(lambda x: x.endswith("_help"), locals().keys())
help_dict = dict()
for key in help_keys:
    help_dict[key[:-5]] = locals()[key]

g_help = partial(help_value, help_dict)


def error_and_exit(msg, error_code=1):
    sys.stderr.write(msg)
    sys.stderr.write("\n")
    sys.exit(error_code)
