#! /usr/bin/env python
# coding: utf-8

import sys
import six

__author__ = '鹛桑够'


lang = "cn"
encoding = "utf-8"
second_encoding = "gb18030"


def decode(s):
    if isinstance(s, six.binary_type):
        try:
            return s.decode(encoding)
        except UnicodeError:
            return s.decode(second_encoding, "replace")
    if isinstance(s, (int, six.integer_types)):
        return "%s" % s
    return s


def encode(s):
    if isinstance(s, six.text_type):
        return s.encode(encoding)
    return s


def is_string(s):
    if isinstance(s, (six.binary_type, six.text_type)) is False:
        return False
    return True


def error_and_exit(msg, error_code=1):
    sys.stderr.write(encode(msg))
    sys.stderr.write("\n")
    sys.exit(error_code)

default_help_dict = dict(
    file_lost=dict(
        en="file [%s] not exist or can not readable",
        cn="文件[%s]不存在或者无权限读取"
    ),
    dir_lost=dict(
        en="directory [%s] not exist or can not readable",
        cn="目录[%s]不存在或者无权限读取"
    ),
    env_lost=dict(
        en="",
        cn=""
    ),
    debug=dict(
        en=" Enter the debug mode,  print out as much information as possible.",
        cn="进入debug模式尽可能多的打印出信息"
    )
)


def help_value(help_dict, key, *args):
    if key in help_dict:
        msg = help_dict[key][lang]
    elif key in default_help_dict:
        msg = default_help_dict[key][lang]
    else:
        raise KeyError("Not find help for %s" % key)
    msg = decode(msg)
    if len(args) > 0:
        args = map(decode, args)
        msg = msg % tuple(args)
    return msg


def jy_input(prompt, prompt_prefix=None):
    if prompt_prefix is not None and prompt is not None:
        prompt = "".join([prompt_prefix, prompt])
    if not prompt.endswith("\n"):
        prompt += "\n"
    if sys.version_info[0] == 2:
        return raw_input(prompt)
    else:
        return input(prompt)