# -*- coding: utf-8 -*-
'''
Manage dingtalk roles.
Document available at https://ding-doc.dingtalk.com/doc#/serverapi2/dnu5l1
'''
import time
import threading
from ..util.api import client


def list(size=None, offset=0):
    '''
    获取角色列表
    '''
    if size is None:
        size = 20
    resp = client.call('POST', '/topapi/role/list',
                       json={'size': size,
                             'offset': offset})
    return resp.json()


def simplelist(role_id, size=None, offset=0):
    '''
    获取角色下员工列表
    '''
    if size is None:
        size = 20
    resp = client.call('POST', '/topapi/role/simplelist',
                       data={'role_id': role_id,
                             'size': size,
                             'offset': offset})
    return resp.json()


def getrolegroup(group_id):
    '''
    获取角色组
    '''
    resp = client.call('POST', '/topapi/role/getrolegroup',
                       data={'group_id': group_id})
    return resp.json()


def getrole(role_id):
    '''
    获取角色详情
    '''
    resp = client.call('POST', '/topapi/role/getrole',
                       data={'roleId': role_id})
    return resp.json()


def add_role(role_name, group_id):
    '''
    创建角色
    '''
    resp = client.call('POST', '/role/add_role',
                       data={'roleName': role_name,
                             'groupId': group_id})
    return resp.json()


def update_role(role_name, role_id):
    '''
    更新角色
    '''
    resp = client.call('POST', '/role/update_role',
                       data={'roleName': role_name,
                             'roleId': role_id})
    return resp.json()


def deleterole(role_id):
    '''
    删除角色
    '''
    resp = client.call('POST', '/topapi/role/deleterole',
                       data={'role_id': role_id})
    return resp.json()


def add_role_group(name):
    '''
    创建角色组
    '''
    resp = client.call('POST', '/role/add_role_group',
                       data={'name': name})
    return resp.json()


def add_roles_for_emps(role_ids, user_ids):
    '''
    批量添加角色
    '''
    if isinstance(role_ids, (list, tuple)):
        role_ids = ','.join(role_ids)
    if isinstance(user_ids, (list, tuple)):
        user_ids = ','.join(user_ids)
    resp = client.call('POST', '/topapi/role/addrolesforemps',
                       data={'roleIds': role_ids,
                             'userIds': user_ids})
    return resp.json()


def remove_roles_for_emps(role_ids, user_ids):
    '''
    批量删除角色
    '''
    if isinstance(role_ids, (list, tuple)):
        role_ids = ','.join(role_ids)
    if isinstance(user_ids, (list, tuple)):
        user_ids = ','.join(user_ids)
    resp = client.call('POST', '/topapi/role/addrolesforemps',
                       data={'roleIds': role_ids,
                             'userIds': user_ids})
    return resp.json()
