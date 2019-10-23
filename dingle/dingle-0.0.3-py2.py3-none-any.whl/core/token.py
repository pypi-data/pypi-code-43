# -*- coding: utf-8 -*-
'''
Manage dingtalk tokens, for example access token.
'''
import time
import uuid
import urllib.parse
import hashlib
import threading
from ..util.api import client
from ..util.data_store import DictStore


class TokenManager(object):
    def __init__(self,
                 app_key=None,
                 app_secret=None,
                 corp_id=None,
                 corp_secret=None,
                 agent_id=None,
                 token_store=None,
                 token_key_prefix='',
                 token_lock=None,
                 **kwargs):
        self.app_key = app_key
        self.app_secret = app_secret
        self.corp_id = corp_id
        self.corp_secret = corp_secret
        self.agent_id = agent_id
        self.token_store = DictStore() if not token_store else token_store
        self.token_key_prefix = token_key_prefix or ''
        self.token_lock = threading.Lock() if not token_lock else token_lock

    def get_key(self, key):
        return '%s%s' % (self.token_key_prefix, key)

    def get_access_token(self):
        access_token = self.token_store.get(self.get_key('access_token')) or {}
        if not access_token or access_token['expires'] <= time.time():
            if self.app_key and self.app_secret:
                resp = client.call('GET', '/gettoken', params={'appkey': self.app_key,
                                                               'appsecret': self.app_secret})
            elif self.corp_id and self.corp_secret:
                resp = client.call('GET', '/gettoken', params={'corpid': self.corp_id,
                                                               'corpsecret': self.corp_secret})
            else:
                raise Exception("Neither app_key/app_secret pair nor corp_id/copr_secret pair provided.")
            ret = resp.json()
            if ret['errcode'] == 0:
                access_token = {'value': ret['access_token'], 'expires': int(time.time()) + 7100}
            else:
                access_token = {}
            self.token_store.set(self.get_key('access_token'), access_token)
        return access_token.get('value')

    def set_access_token(self, token):
        data = {'value': token,
                'expires': int(time.time()) + 3600}
        self.token_store.set(self.get_key('access_token'), data)

    def get_jsapi_ticket(self):
        jsapi_ticket = self.token_store.get(self.get_key('jsapi_ticket'))
        if not jsapi_ticket or jsapi_ticket['expires'] <= time.time():
            resp = client.call('GET', '/get_jsapi_ticket',
                               params={'access_token': self.get_access_token()})
            ret = resp.json()
            if ret['errcode'] == 0:
                jsapi_ticket = {'ticket': ret['ticket'], 'expires': int(time.time() - 60) + ret['expires_in']}
            else:
                jsapi_ticket = {'expires': 0}
            self.token_store.set(self.get_key('jsapi_ticket'), jsapi_ticket)
        return jsapi_ticket.get('ticket')

    def get_js_signature(self, noncestr, timestamp, url):
        pairs = [('jsapi_ticket', self.get_jsapi_ticket()),
                 ('noncestr', noncestr),
                 ('timestamp', timestamp),
                 ('url', url)]
        sign_str = '&'.join(["%s=%s" % (k, v) for (k, v) in pairs]).encode('utf-8')
        signature = hashlib.sha1(sign_str).hexdigest()
        return signature

    def get_dd_config(self, url, api_list=None, type=0):
        unquoted_url = urllib.parse.unquote(url)
        if api_list is None:
            api_list = []
        ret = {
            'nonceStr': str(uuid.uuid1()),
            'agentId': self.agent_id,
            'timeStamp': str(int(time.time())),
            'corpId': self.corp_id,
            'type': type
        }
        ret['signature'] = self.get_js_signature(ret['nonceStr'],
                                                 ret['timeStamp'],
                                                 unquoted_url)
        ret['jsApiList'] = api_list
        return ret
