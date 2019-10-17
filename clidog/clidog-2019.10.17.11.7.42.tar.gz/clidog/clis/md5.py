#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Project      : tql-CLI.
# @File         : tomd5
# @Time         : 2019-08-12 19:51
# @Author       : yuanjie
# @Email        : yuanjie@xiaomi.com
# @Software     : PyCharm
# @Description  : 

import hashlib


def md5(x):
    if isinstance(x, str):
        pass
    else:
        x = str(x)

    m = hashlib.md5()
    m.update(bytes(x, encoding="utf8"))
    _ = m.hexdigest()
    return _

if __name__ == '__main__':
    print(md5(123456789))
