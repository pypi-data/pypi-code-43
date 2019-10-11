# coding=utf-8

import json


def dumps(obj):
    return json.dumps(obj, ensure_ascii=False).encode('utf8')


def loads(s):
    return json.loads(s)
