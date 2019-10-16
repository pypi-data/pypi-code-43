# -*- coding: utf-8 -*-
"""
Created By Murray(m18527) on 2019/9/4 15:29
"""
from __future__ import absolute_import, unicode_literals

import os
import sys
from collections import namedtuple

import requests

from .constants import UNKNOWN_ERROR, MSG, GONE_AWAY
from .loggerutils import logging

logger = logging.getLogger(__name__)

CONNECT_TIMEOUT = int(os.getenv("CONNECT_TIMEOUT", 3))
READ_TIMEOUT = int(os.getenv("READ_TIMEOUT", 10))

Resp = namedtuple("Resp", ["status_code", "code", "data", "msg"])


def resp_parse_process(resp=None):
    """parse resp"""
    if not resp:
        return Resp(status_code=400, code=UNKNOWN_ERROR, data={}, msg=MSG[UNKNOWN_ERROR])
    status_code = resp.status_code
    if 200 <= status_code < 300:
        data = resp.json()
        code = data.get("code", GONE_AWAY)
        if code:
            return Resp(status_code=status_code, code=code, data=data, msg=data.get("message") or MSG.get(code))
        return Resp(status_code=status_code, code=code, data=data, msg=MSG.get(code))
    if isinstance(resp.reason, bytes):
        try:
            reason = resp.reason.decode('utf-8')
        except UnicodeDecodeError:
            reason = resp.reason.decode('iso-8859-1')
    else:
        reason = resp.reason
    return Resp(status_code=status_code, code=UNKNOWN_ERROR, data={}, msg=reason)


def _get_request_headers(headers=None, token=None, school=None):
    if not isinstance(headers, dict):
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Trident/7.0; rv:11.0) like Gecko',
            "Content-Type": "application/json",
            'Connection': 'close'
        }
    if token:
        headers['Authorization'] = '{}'.format(token)
    if school:
        headers["X-Custom-Header-3School"] = school
    return headers


def do_get_request(url, params=None, headers=None, token=None, school_in_header=None):
    """send http get request"""
    headers = _get_request_headers(headers=headers, token=token, school=school_in_header)
    resp = None
    try:
        resp = requests.get(url=url, params=params, headers=headers, timeout=(CONNECT_TIMEOUT, READ_TIMEOUT))
        return resp_parse_process(resp=resp)
    except Exception as e:
        logger.error("Error: {}, Detail: {}".format(sys._getframe().f_code.co_name, e))
        return resp_parse_process()
    finally:
        if resp:
            resp.close()


def do_post_request(url, token=None, json=None, data=None, headers=None, school_in_header=None):
    """send http post request"""
    headers = _get_request_headers(headers=headers, token=token, school=school_in_header)
    resp = None
    try:
        resp = requests.post(url=url, json=json, data=data, headers=headers, timeout=(CONNECT_TIMEOUT, READ_TIMEOUT))
        return resp_parse_process(resp=resp)
    except Exception as e:
        logger.error("Error: {}, Detail: {}".format(sys._getframe().f_code.co_name, e))
        return resp_parse_process()
    finally:
        if resp:
            resp.close()
