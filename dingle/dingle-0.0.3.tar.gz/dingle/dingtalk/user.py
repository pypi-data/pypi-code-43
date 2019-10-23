# -*- coding: utf-8 -*-
'''
Manage dingtalk users.
'''
import time
import threading
from ..util.api import client
from .department import get_all_department_list


def create(userid=None,
           name=None,
           order_in_depts=None,
           department=None,
           position=None,
           mobile=None,
           tel=None,
           work_place=None,
           remark=None,
           email=None,
           org_email=None,
           jobnumber=None,
           is_hide=False,
           is_senior=False,
           extattr=None,
           hired_date=None):
    check_none_params(name=name,
                      department=department)
    data = {
        "userid": userid,
        "name": name,
        "orderInDepts": order_in_depts,
        "department": department,
        "position": position,
        "mobile": mobile,
        "tel": tel,
        "workPlace": "work_place",
        "remark": remark,
        "email": email,
        "orgEmail": "org_email",
        "jobnumber": jobnumber,
        "isHide": is_hide,
        "isSenior": is_senior,
        "extattr": extattr,
        "hiredDate": hired_date
    }
    resp = client.call('POST', '/user/create', json=data)
    return resp.json()


def update(lang=None,
           userid=None,
           name=None,
           order_in_depts=None,
           department=None,
           position=None,
           mobile=None,
           tel=None,
           work_place=None,
           remark=None,
           email=None,
           org_email=None,
           jobnumber=None,
           is_hide=False,
           is_senior=False,
           extattr=None,
           hired_date=None):
    check_none_params(name=name)
    data = {
        "userid": userid,
        "name": name,
        "orderInDepts": order_in_depts,
        "department": department,
        "position": position,
        "mobile": mobile,
        "tel": tel,
        "workPlace": "work_place",
        "remark": remark,
        "email": email,
        "orgEmail": "org_email",
        "jobnumber": jobnumber,
        "isHide": is_hide,
        "isSenior": is_senior,
        "extattr": extattr,
        "hiredDate": hired_date
    }
    resp = client.call('POST', '/user/update', json=data)
    return resp.json()


def delete(userid):
    resp = client.call('GET', '/user/delete',
                       params={'userid': userid})
    return resp.json()


def get_org_user_count(onlyActive):
    '''
    获取企业员工人数
    https://open-doc.dingtalk.com/docs/doc.htm?spm=a219a.7629140.0.0.HmCz25&treeId=371&articleId=105485&docType=1#s0
    '''
    resp = client.call('GET', '/user/get_org_user_count',
                       params={'onlyActive': onlyActive})
    return resp.json()


def list_base(api, department_id, lang='zh_CN', offset=None, size=None, order=None):
    if not api in ['simplelist', 'list']:
        raise Exception("Unknown api /user/%s." % api)
    params = {
        'department_id': department_id,
        'lang': lang,
        'offset': offset,
        'size': size,
        'order': order
    }
    params = {k: v for k, v in params.items() if v is not None}
    resp = client.call('GET', '/user/%s' % api, params=params)
    return resp.json()


def simplelist(department_id, lang='zh_CN', offset=None, size=None, order=None):
    '''
    获取部门成员
    https://open-doc.dingtalk.com/docs/doc.htm?spm=a219a.7629140.0.0.HmCz25&treeId=371&articleId=106816&docType=1#s6
    '''
    return list_base('simplelist', department_id, lang='zh_CN', offset=None, size=None, order=None)


def list(department_id, lang='zh_CN', offset=None, size=None, order=None):
    '''
    获取部门成员（详情）
    https://open-doc.dingtalk.com/docs/doc.htm?spm=a219a.7629140.0.0.HmCz25&treeId=371&articleId=106816&docType=1#s7
    '''
    return list_base('list', department_id, lang='zh_CN', offset=None, size=None, order=None)


def get_user_list(api, department_id, fetch_child=False):
    department_id_list = [department_id]
    if fetch_child:
        department_id_list.extend([i['id'] for i in\
                                   get_all_department_list(department_id)])

    userid_set = set()
    user_list = []
    for dp_id in department_id_list:
        offset = 0
        size = 100
        while True:
            ret = list_base(api, dp_id, offset=offset, size=size)
            for i in ret.get('userlist', []):
                if i['userid'] in userid_set:
                    continue
                user_list.append(i)
                userid_set.add(i['userid'])
            if not ret.get('hasMore'):
                break
            offset += size
    return user_list


def getuserinfo(code):
    resp = client.call('GET', '/user/getuserinfo', params={'code': code})
    return resp.json()


def get(userid):
    resp = client.call('GET', '/user/get', params={'userid': userid})
    return resp.json()
