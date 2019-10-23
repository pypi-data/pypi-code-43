# -*- coding: utf-8 -*-
'''
Manage dingtalk messages.
'''
import time
import json
import urllib.parse
from ..util.conf import get_config
from ..util.api import client


def get_pc_link(link, pc_slide='true'):
    '''
    获取pc跳转url
    '''
    pc_slide = 'true' if pc_slide == 'true' else 'false'
    pc_link = 'dingtalk://dingtalkclient/page/link?pc_slide=%s&url=%s'\
              % (pc_slide, urllib.parse.quote(link))
    return pc_link


class Message(dict):
    def as_msg(self):
        msg = {'msgtype': self.msgtype}
        msg[self.msgtype] = dict(self)
        return msg


class TextMessage(Message):
    msgtype = 'text'

    def __init__(self, content):
        self['content'] = content


class ImageMessage(Message):
    msgtype = 'image'

    def __init__(self, media_id):
        self['media_id'] = media_id


class VoiceMessage(Message):
    msgtype = 'voice'

    def __init__(self, media_id, duration=None):
        self['media_id'] = media_id
        if duration:
            self['duration'] = duration


class FileMessage(Message):
    msgtype = 'file'

    def __init__(self, media_id):
        self['media_id'] = media_id


class LinkMessage(Message):
    msgtype = 'link'

    def __init__(self, messageUrl, picUrl, title, text):
        self['messageUrl'] = messageUrl
        self['picUrl'] = picUrl
        self['title'] = title
        self['text'] = text


class OAMessage(Message):
    msgtype = 'oa'

    def __init__(self, message_url, head, body,
                 pc_message_url):
        self['message_url'] = message_url
        self['head'] = head
        self['body'] = body
        if pc_message_url is not None:
            self['pc_message_url'] = pc_message_url


class MarkdownMessage(Message):
    msgtype = 'markdown'

    def __init__(self, title, text):
        self['title'] = title
        self['text'] = text


class ActionCardMessage(Message):
    msgtype = 'action_card'
    optional_fields = ['single_title', 'single_url=None',
                       'btn_orientation', 'btn_json_list']

    def __init__(self, title, markdown,
                 single_title=None, single_url=None,
                 btn_orientation=None, btn_json_list=None):
        self['title'] = title
        self['markdown'] = markdown
        for field_name in self.optional_fields:
            if locals().get(field_name) is not None:
                self[field_name] = locals()[field_name]


def corpconversation_asyncsend(agent_id=None, msg=None,
                               userid_list=None, dept_id_list=None, to_all_user=False):
    '''
    发送企业通知消息

    Param
    '''
    if agent_id is None:
        agent_id = get_config().get('agent_id')
    if not (agent_id and msg):
        raise Exception("Both agent_id and msg must be provided.")
    if isinstance(userid_list, list):
        userid_list = ','.join(userid_list)
    if isinstance(dept_id_list, list):
        userid_list = ','.join(dep_id_list)
    params = {k: v for k, v in dict(agent_id=agent_id,
                              userid_list=userid_list,
                              dept_id_list=dept_id_list,
                              to_all_user=to_all_user).items() if v}
    if isinstance(msg, Message):
        msg = msg.as_msg()
    params['msg'] = json.dumps(msg)
    resp = client.call('POST',
                       '/topapi/message/corpconversation/asyncsend_v2',
                       data=params)
    return resp.json()


def corpconversation_asyncsendbycode(agent_id=None, msg=None,
                                     userid_list=None, dept_id_list=None,
                                     to_all_user=False, code=None):
    '''
    通过用户授权码发送企业通知消息
    '''
    if agent_id is None:
        agent_id = get_config().get('agent_id')
    if not (agent_id and msg and code):
        raise Exception("All of agent_id, msg and code must be provided.")
    if isinstance(userid_list, list):
        userid_list = ','.join(userid_list)
    if isinstance(dept_id_list, list):
        userid_list = ','.join(dep_id_list)
    params = {k: v for k, v in dict(agent_id=agent_id,
                              userid_list=userid_list,
                              dept_id_list=dept_id_list,
                              to_all_user=to_all_user,
                              code=code).items() if v}
    params['msgtype'] = msg.msgtype
    params['msgcontent'] = dict(msg)
    resp = client.call('POST',
                       '/topapi/message/corpconversation/asyncsendbycode',
                       data=params)
    return resp.json()


def corpconversation_getsendprogress(agent_id=None, task_id=None):
    '''
    获取企业通知消息的发送进度
    '''
    if agent_id is None:
        agent_id = get_config().get('agent_id')
    if not (agent_id and task_id):
        raise Exception("Both agent_id and task_id must be provided.")
    params = {'agent_id': agent_id,
              'task_id': task_id}
    resp = client.call('POST',
                       '/topapi/message/corpconversation/getsendprogress',
                       data=params)
    return resp.json()


def corpconversation_getsendresult(agent_id=None, task_id=None):
    '''
    获取企业通知消息的发送结果
    '''
    if agent_id is None:
        agent_id = get_config().get('agent_id')
    if not (agent_id and task_id):
        raise Exception("Both agent_id and task_id must be provided.")
    params = {'agent_id': agent_id,
              'task_id': task_id}
    resp = client.call('POST',
                       '/topapi/message/corpconversation/getsendresult',
                       data=params)
    return resp.json()
