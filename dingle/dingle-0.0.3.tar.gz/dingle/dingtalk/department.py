# -*- coding: utf-8 -*-
'''
Manage dingtalk departments.
'''
import time
import threading
from ..util.api import client


def list_ids(parent_department_id):
    '''
    获取子部门ID列表
    https://open-doc.dingtalk.com/docs/doc.htm?spm=a219a.7629140.0.0.RpPrRv&treeId=371&articleId=106817&docType=1#s0
    '''
    resp = client.call('GET', '/department/list_ids', params={'id': parent_department_id})
    return resp.json()


def list(id=None, fetch_child=False, lang='zh_CN'):
    '''
    获取部门列表
    https://open-doc.dingtalk.com/docs/doc.htm?spm=a219a.7629140.0.0.RpPrRv&treeId=371&articleId=106817&docType=1#s1
    '''
    resp = client.call('GET', '/department/list', params={'id': id, 'fetch_child': fetch_child, 'lang': lang})
    return resp.json()


def get_all_department_list(root_department_id=1):
    '''
    获取以root_department_id为根节点的全部部门列表
    '''
    ret = list(id=root_department_id,
               fetch_child=True)
    if ret['errcode'] == 0:
        return ret['department']
    else:
        return []
