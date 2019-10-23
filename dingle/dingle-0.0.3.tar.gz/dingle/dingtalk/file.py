# -*- coding: utf-8 -*-
'''
Manage dingtalk files, including media and Ding drive.
Document available at
https://ding-doc.dingtalk.com/doc#/serverapi2/bcmg0i
and
https://ding-doc.dingtalk.com/doc#/serverapi2/wk3krc
'''
import time
from ..util.conf import get_config
from ..util.api import client


def get_custom_space(domain=None, agent_id=None):
    if agent_id is None:
        agent_id = get_config().get('agent_id')
    params = {
        'domain': domain,
        'agent_id': agent_id
    }
    resp = client.call('GET',
                       '/cspace/get_custom_space',
                       params=params)
    return resp.json()


def grant_custom_space(agent_id=None,
                       domain=None,
                       type=None,
                       userid=None,
                       path='/',
                       fileids=None,
                       duration=0):
    if agent_id is None:
        agent_id = get_config().get('agent_id')
    params = {
        "agent_id": agent_id,
        "domain": domain,
        "type": type,
        "userid": userid,
        "path": path,
        "fileids": fileids,
        "duration": duration
    }
    resp = client.call('GET', '/cspace/grant_custom_space',
                       params=params)
    return resp.json()
