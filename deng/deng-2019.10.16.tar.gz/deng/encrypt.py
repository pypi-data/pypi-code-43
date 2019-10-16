#!/usr/bin/env python
# coding:utf-8
"""加密模块
"""
import json
import base64
import hashlib


class EncryptTools(object):
    """加密类，目前仅支持md5，base64"""

    @staticmethod
    def getmd5(paramstr):
        """计算MD5值"""
        if isinstance(paramstr, int):
            paramstr = str(paramstr)
        try:
            _hash = hashlib.md5()
            _hash.update(paramstr.encode('UTF-8'))
        except ImportError:
            # for Python << 2.5
            import md5
            _hash = md5.new()
            _hash.update(paramstr)
        return _hash.hexdigest()

    @staticmethod
    def join_array(param_dict):
        """将字典参数按升序排序并及拼接成字符串"""
        str_data = ''
        sorted_x = sorted(iter(param_dict.items()), key=lambda param_dict : param_dict[0])
        for mytuple in sorted_x:
            str_data += str(mytuple[0])+str(mytuple[1])
        return str_data

    @staticmethod
    def base64_encode(connect: dict) -> str:
        return str(base64.b64encode(bytes(json.dumps(connect, ensure_ascii=False), encoding='utf8')), encoding='utf8')

    @staticmethod
    def base64_decode(connect: str) -> dict:
        return json.loads(str(base64.b64decode(bytes(connect, encoding='utf8')), encoding='utf8'))
