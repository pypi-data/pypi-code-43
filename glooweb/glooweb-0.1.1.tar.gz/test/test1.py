# -*- coding: utf-8 -*-
# @Author  : Gloo
# @time    : 2019/9/14 20:39
# @File    : test1.py
# @Software: PyCharm
import re


TYPE_PATTERNS = {
    "str": r"[^/]+",
    "word": r"\w+",
    "int": r"[+-]?\d+",
    "float": r"[+-]?\d+.\d+",
    "any": r".+"
}

TYPE_CASE = {
    "str": str,
    "word": str,
    "int": int,
    "float": float,
    "any": str
}
regex = re.compile('/{([^{}:]+):?([^{}:]*)}')


def transform(kv: str):
    name, _, type = kv.strip("/{}").partition(":")
    return "/(?P<{}>{})".format(name, TYPE_PATTERNS.get(type, r'\w+')), name, TYPE_CASE.get(type, str)


def parse(src: str):
    start = 0
    res = ''
    translator = {}
    while True:
        matcher = regex.search(src, start)
        if matcher:
            res += matcher.string[start: matcher.start()]
            print(matcher.string[start: matcher.start()])
            print(matcher.group())
            print(matcher.string[matcher.start(): matcher.end()])
            tmp = transform(matcher.group())
            res += tmp[0]
            translator[tmp[1]] = tmp[2]
            start = matcher.end()
        else:
            break

    if res:
        return res, translator
    else:
        return src, translator


print(parse("/admin/{name:str}/asdf/{id:int}"))
