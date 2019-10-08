#!/usr/bin/env python
# -*- coding=utf-8 -*-

from result import Result
import re


def boolValue(arg):
    value = False
    if arg in ("false", "FALSE", "False", "0"):
        value = False
    else:
        value = True
    return value

def matchList(pattern, string, byLine=False):
    """正则匹配

    Arguments:
        pattern {str} -- 正则表达式
        string {str} -- 要匹配的全量字符串

    Keyword Arguments:
        byLine {bool} -- 是不是一行一样匹配 (default: {False})

    Returns:
        [list] -- 匹配成功的列表
    """
    if string == "未知消息类型":
        Result.instance().returnError("没有匹配到相应的内容")
    if byLine:
        pattern = re.compile(pattern)
    else:
        pattern = re.compile(pattern, re.S)
    matchList = pattern.findall(string)
    if isinstance(matchList, list):
        return matchList
    else:
        Result.instance().returnError("没有匹配到相应的内容")


def byteify(input):
    # unicode 编码问题
    if isinstance(input, dict):
        return {byteify(key): byteify(value) for key, value in input.iteritems()}
    elif isinstance(input, list):
        return [byteify(element) for element in input]
    elif isinstance(input, unicode):
        return input.encode('utf-8')
    else:
        return input
