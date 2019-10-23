# -*- coding: utf-8 -*-
'''
Interface for dingtalk chat message api.
'''
import time
import threading
from ..util.api import check_none_params, client
from .message import *


def send(chat_id=None, msg=None):
    '''
    发送群消息
    '''
    check_none_params(chat_id=chat_id,
                      msg=msg)
    data = {'chatid': chat_id}
    if isinstance(msg, Message):
        data['msg'] = msg.as_msg()
    else:
        data['msg'] = msg
    resp = client.call('POST', '/chat/send', json=data)
    return resp.json()


def get_read_list(message_id=None,
                  cursor=0,
                  size=100):
    check_none_params(message_id=message_id)
    params = {
        "messageId": message_id,
        "cursor": cursor,
        "size": size
    }
    resp = client.call('GET', '/chat/getReadList', params=params)
    return resp.json()


def create(name=None,
           owner=None,
           useridlist=None,
           show_history_type=0,
           searchable=0,
           validation_type=0,
           mention_all_authority=0,
           chat_banned_type=0,
           management_type=0):
    '''
    创建群
    '''
    check_none_params(name=name,
                      owner=owner,
                      useridlist=useridlist)
    if owner not in useridlist:
        raise Exception("owner must be in useridlist")
    data = {
        "name": name,
        "owner": owner,
        "useridlist": useridlist,
        "showHistoryType": show_history_type,
        "searchable": searchable,
        "validationType": validation_type,
        "mentionAllAuthority": mention_all_authority,
        "chatBannedType": chat_banned_type,
        "managementType": management_type
    }
    resp = client.call('POST', '/chat/create', json=data)
    return resp.json()


def update(chat_id=None,
           name=None,
           owner=None,
           add_useridlist=None,
           del_useridlist=None,
           icon=None,
           show_history_type=None,
           searchable=None,
           validation_type=None,
           mention_all_authority=None,
           chat_banned_type=None,
           management_type=None):
    check_none_params(chat_id=chat_id)
    data = {
        "chatid": chat_id,
        "name": name,
        "owner": owner,
        "add_useridlist": add_useridlist,
        "del_useridlist": del_useridlist,
        "icon": icon,
        "showHistoryType": show_history_type,
        "searchable": searchable,
        "validationType": validation_type,
        "mentionAllAuthority": mention_all_authority,
        "chatBannedType": chat_banned_type,
        "managementType": management_type
    }
    resp = client.call('POST', '/chat/update', json=data)
    return resp.json()


def get(chat_id):
    resp = client.call('GET', '/chat/get', params={'chatid': chat_id})
    return resp.json()
