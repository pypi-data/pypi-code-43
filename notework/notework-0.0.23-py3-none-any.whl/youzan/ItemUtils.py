#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2019/05/08 18:56
# @Author  : niuliangtao
# @Site    : 
# @File    : ItemUtils.py
# @Software: PyCharm


import json
import os
import sys

import requests

from ..worker import decrypt

sys.path.append(os.path.dirname(__file__) + os.sep + '../')


def get_data_from_console(url):
    try:
        r = requests.get(url)
        return json.loads(r.text)
    except:
        print("error")
        return None


def get_item_detail(item_id, shop_id):
    url = decrypt(
        b'gAAAAABdaN0rQeQGj1C5L7tXMNUoocv_n6lv8mOA3fkxDHGxVhIL4h44nzkmhEGiSDZjGpkiN9-Bs68BBf0HUQ1YC2_QyF0GmtJwcvv2OHv-Mx5_by6Qjdm3p2HY_2aLV5MOpA3EaeX27u7rbwAP8ekcG_XimggIlSI8VKV4zSNBK2ZZPFAvcfI=').format(
        item_id, shop_id)

    res = None
    for i in range(0, 5):
        if res is None:
            res = get_data_from_console(url)
        else:
            break

    if res is not None:
        return res['data']
    return res


def test():
    res = get_item_detail(item_id="466973942", shop_id="1206788")

    print(res)
