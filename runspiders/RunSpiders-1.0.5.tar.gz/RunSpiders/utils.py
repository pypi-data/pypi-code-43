# -*- coding: utf-8 -*-
# @Time     : 2019/8/19 17:56
# @Author   : Run 
# @File     : utils.py
# @Software : PyCharm

"""
1. 官方文档：
    会话对象让你能够跨请求保持某些参数。
    它也会在同一个Session实例发出的所有请求之间保持cookie，期间使用urllib3的connection pooling功能。
    所以如果你向同一主机发送多个请求，底层的 TCP 连接将会被重用，从而带来显著的性能提升。
2. 以下给出的两种方式request_url和get_http_session，都能实现对失败的请求再进行retry次尝试，但整体感觉session的方式速度更快一些。
"""

import requests
import requests.adapters
import time
import os
import stat
import shutil


def request_url(url, timeout=10, retry=3, retry_interval=0.1, **kwargs):
    """

    :param url:
    :param timeout:
    :param retry:
    :param retry_interval:
    :return:
        success: True, req
        fail: False, None
    """
    params = {'url': url, 'timeout': timeout}
    params.update(kwargs)
    while retry:
        try:
            req = requests.get(**params)
        except:
            retry -= 1
        else:
            if req.status_code == 200:
                return True, req
            else:
                retry -= 1
        time.sleep(retry_interval)

    return False, None


def get_http_session(pool_connections, pool_maxsize, max_retries):
    session = requests.Session()
    adapter = requests.adapters.HTTPAdapter(pool_connections=pool_connections,
                                            pool_maxsize=pool_maxsize, max_retries=max_retries)
    session.mount('http://', adapter)
    session.mount('https://', adapter)
    return session


def delete_path(file_path: str) -> None:
    """
    Force delete file or dir(contains all subdirs and files).
    Ignore file's attributes like 'read-only'.
    """
    if os.path.exists(file_path):
        if os.path.isfile(file_path):  # file
            os.chmod(file_path, stat.S_IWRITE)
            os.remove(file_path)
        else:  # dir
            for path, sub_folders, sub_files in os.walk(file_path):
                for file in sub_files:
                    os.chmod(os.path.join(path, file), stat.S_IWRITE)
                    os.remove(os.path.join(path, file))
            shutil.rmtree(file_path)
        print("{} deleted".format(file_path))
    else:
        print("{} doesn't exist".format(file_path))


