# -*- coding: utf-8 -*-
'''
Interface for dingtalk auth api.
'''
import time
import threading
from ..util.api import client


def scopes():
    '''
    获取通讯录权限范围
    钉钉官方文档见 https://open-doc.dingtalk.com/microapp/serverapi2/vt6v7m
    '''
    resp = client.call('GET', '/auth/scopes')
    return resp.json()
