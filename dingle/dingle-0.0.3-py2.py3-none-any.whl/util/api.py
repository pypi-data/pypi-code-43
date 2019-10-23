# -*- coding: utf-8 -*-
'''
Provide basic dingtalk api call interface.
'''
import logging
import requests
import datetime
import hmac
import hashlib
from .conf import get_config
from .log import json_log

DINGTALK_API_BASE = 'https://oapi.dingtalk.com'
DINGTALK_TOP_API_BASE = 'https://eco.taobao.com/router/rest'


def check_none_params(**kwargs):
    '''
    Check whether params in kwargs are None.
    '''
    for k, v in kwargs.items():
        if v is None:
            raise Exception("Param %s should not be None." % k)
    return True


class APIClient(object):
    def __init__(self, manager=None):
        self.session = requests.Session()
        self.set_manager(manager)

    def set_manager(self, manager):
        self.manager = manager

    def call(self, method, path, **kwargs):
        '''
        Call an dingtalk api.
        '''
        if method not in ['GET', 'POST', 'PUT', 'DELETE']:
            raise Exception("Unsupported HTTP method %s." % method)
        if 'params' not in kwargs:
            kwargs['params'] = {}

        if 'access_token' not in kwargs and path != '/gettoken':
            kwargs['params']['access_token'] = self.manager.get_access_token()
        path = '/%s' % path.lstrip('/')
        url = '%s%s' % (DINGTALK_API_BASE, path)
        resp = self.session.request(method, url, **kwargs)
        logger = logging.getLogger(__name__)
        json_log({"method": method,
                  "path": path,
                  "kwargs": kwargs,
                  "content": resp.json()}, 'call')
        return resp

    def top_call(self, method, session=None, format='json', **kwargs):
        '''
        Call an dingtalk top api.
        '''
        config = get_config()
        if session is None:
            session = self.manager.get_access_token()
        data = {
            u'method': method,
            u'session': session,
            u'format': format,
            u'partner_id': config['corp_id'],
            u'v': u'2.0'
        }
        data[u'timestamp'] = (datetime.datetime.utcnow() + datetime.timedelta(0, 3600 * 8))\
                            .strftime('%Y-%m-%d %H:%M:%S')
        data.update(kwargs)
        resp = self.session.request('POST', DINGTALK_TOP_API_BASE, data=data)
        json_log({"method": method,
                  "kwargs": kwargs,
                  "content": resp.json()}, 'top_call')
        return resp

client = APIClient()
