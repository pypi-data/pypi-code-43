# -*- coding: utf-8 -*-
'''
Interface for dingtalk callback message api.
'''
import time
import threading
from ..util.api import check_none_params, client


def register_call_back(call_back_tag=None,
                       token=None,
                       aes_key=None,
                       url=None):
    check_none_params(call_back_tag=call_back_tag,
                      token=token,
                      aes_key=aes_key,
                      url=url)
    data = {
        "call_back_tag": call_back_tag,
        "token": token,
        "aes_key": aes_key,
        "url": url
    }
    resp = client.call('POST', '/call_back/register_call_back',
                       json=data)
    return resp.json()


def get_call_back():
    resp = client.call('GET', '/call_back/get_call_back')
    return resp.json()


def update_call_back(call_back_tag=None,
                     token=None,
                     aes_key=None,
                     url=None):
    check_none_params(call_back_tag=call_back_tag,
                      token=token,
                      aes_key=aes_key,
                      url=url)
    data = {
        "call_back_tag": call_back_tag,
        "token": token,
        "aes_key": aes_key,
        "url": url
    }
    resp = client.call('POST', '/call_back/update_call_back',
                       json=data)
    return resp.json()


def delete_call_back():
    resp = client.call('GET', '/call_back/delete_call_back')
    return resp.json()


def get_call_back_failed_result():
    resp = client.call('GET', '/call_back/get_call_back_failed_result')
    return resp.json()
