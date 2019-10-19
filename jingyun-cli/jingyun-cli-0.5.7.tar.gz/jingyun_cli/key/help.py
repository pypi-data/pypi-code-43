#! /usr/bin/env python
# coding: utf-8

import sys
from functools import partial
from jingyun_cli.util.help import help_value

__author__ = '鹛桑够'

output_help = {"en": "the output of file, default is work dir.", "cn": "下载后的文件保存的目录，默认保存到当前工作目录"}
app_help = {"en": " what kind of application key belongs to, for example: mysql oss",
            "cn": "key属于哪类应用，例如mysql oss"}
print_key_help = {"en": "what information is included in the print key ", "cn": "打印密钥包含的哪些信息"}
only_value_help = {"en": "only print value", "cn": "只打印密钥要打印的密钥中的属性值，不打印属性"}
replace_file_help = {"en": "use key info format the file concent and rewrite",
                     "cn": "将该文件内容，使用密钥所包含的信息进行字符串格式化，再回写到该文件"}
endpoint_help = {"en": "dist key server endpoint, for example https://dms.gene.ac/dist/key/",
                 "cn": "密钥分发服务器端点,例如https://dms.gene.ac/dist/key/"}
filters_help = {"en": "other parameters used to filter keys. format is filter_key=filter_value",
                "cn": "其他用于筛选密钥的参数，格式为filter_key=filter_value"}

error_filter_help = {"en": "invalid filter string, please use filter_key=filter_value",
                     "cn": "无效的筛选字符串%s，请使用filter_key=filter_value"}
error_get_help = {"en": " unable to obtain a specified key, %s ", "cn": "无法获得指定的密钥,%s"}
file_not_exist_help = {"en": "file %s not exist", "cn": "文件%s不存在"}
key_not_exist_help = {"en": "key %s not exist", "cn": "密钥信息中不包含%s"}
read_error_help = {"en": "read file %s error", "cn": "读取文件%s失败"}
write_error_help = {"en": "rewrite file %s error", "cn": "重写文件%s失败"}

help_keys = filter(lambda x: x.endswith("_help"), locals().keys())
help_dict = dict()
for key in help_keys:
    help_dict[key[:-5]] = locals()[key]

g_help = partial(help_value, help_dict)


def error_and_exit(msg, error_code=1):
    sys.stderr.write(msg)
    sys.stderr.write("\n")
    sys.exit(error_code)
