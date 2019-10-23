# -*- coding: utf-8 -*-
'''
Manage dingtalk blackboard.
Document available at https://ding-doc.dingtalk.com/doc#/serverapi2/knmd16
'''
import time
import threading
from ..util.api import client


def list_top_ten(userid):
    '''
    获取用户可见的10条公告数据
    '''
    resp = client.call('POST', '/topapi/blackboard/listtopten',
                       data={'userid': userid})
    return resp.json()
