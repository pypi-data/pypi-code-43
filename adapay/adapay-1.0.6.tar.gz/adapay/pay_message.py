#!/usr/bin/env python
import json
import threading
import uuid

from paho.mqtt import client as mqtt

import adapay
from adapay.api.api_request import ApiRequest
from adapay.api.urls import pay_message_token
from adapay.utils.log_util import log_info, log_error


class AdapayMessage:
    instance_id = ''
    access_key = ''
    group_id = ''
    client_id = ''
    topic = ''
    broker_url = ''

    connect_callback = None
    subscribe_callback = None
    message_received = None

    @staticmethod
    def init():
        AdapayMessage.instance_id = 'post-cn-0pp18zowf0m'

        AdapayMessage.access_key = 'LTAIOP5RkeiuXieW'

        AdapayMessage.group_id = 'GID_CRHS_ASYN'

        AdapayMessage.client_id = AdapayMessage.group_id + '@@@' + str(
            hash(adapay.api_key + (str(uuid.uuid1()))))

        AdapayMessage.topic = 'topic_crhs_sender/' + adapay.api_key

        AdapayMessage.broker_url = 'post-cn-0pp18zowf0m.mqtt.aliyuncs.com'

    @staticmethod
    def _on_connect(client, userdata, flags, resp_code):
        """
        建立长连接成功回调
        """
        log_info('connected with result code ' + str(resp_code))

        if AdapayMessage.connect_callback is not None:
            AdapayMessage.connect_callback(resp_code)

        if resp_code == 0:
            client.subscribe(AdapayMessage.topic, 0)

    @staticmethod
    def _on_disconnect(client, userdata, resp_code):
        """
        :param resp_code:
         长连接链接失败回调
        1	伪造 Token，不可解析
        2	Token 已经过期
        3	Token 已经被吊销
        4	资源和 Token 不匹配
        5	权限类型和 Token 不匹配
        8	签名不合法
        -1	帐号权限不合法

        :return:
        """
        log_info('unexpected disconnection %s' % resp_code)

        if AdapayMessage.connect_callback is not None:
            AdapayMessage.connect_callback(resp_code)

    @staticmethod
    def _on_subscribe(client, userdata, mid, granted_qos):
        """
        订阅成功回调
        """
        log_info('on_subscribe')
        if AdapayMessage.subscribe_callback is not None:
            AdapayMessage.subscribe_callback(0)

    @staticmethod
    def _on_unsubscribe(client, userdata, mid):
        """
        订阅成功回调
        """
        log_info('on_unsubscribe')
        if AdapayMessage.subscribe_callback is not None:
            AdapayMessage.subscribe_callback(-1)

    @staticmethod
    def _on_message(client, userdata, messages):
        """
        接收到交易结果回调
        """
        message_str = messages.payload.decode('utf-8')
        log_info('on_msg_receive:' + message_str)

        if AdapayMessage.message_received is not None:
            try:
                msg_dict = json.loads(message_str)
                AdapayMessage.message_received(msg_dict)
            except Exception as e:
                log_error(str(e))
                log_error('pay message loads error:' + message_str)

    @staticmethod
    def set_subscribe_callback(connect_callback=None, subscribe_callback=None):
        """
        设置建立长连接和订阅的回调
        :return:
        """
        AdapayMessage.connect_callback = connect_callback
        AdapayMessage.subscribe_callback = subscribe_callback

    @staticmethod
    def subscribe(on_message_received):
        AdapayMessage.message_received = on_message_received
        pay_msg_thread = threading.Thread(target=AdapayMessage._execute)
        pay_msg_thread.start()

    @staticmethod
    def _execute():
        client = mqtt.Client(AdapayMessage.client_id, protocol=mqtt.MQTTv311, clean_session=True)

        client.on_connect = AdapayMessage._on_connect
        client.on_disconnect = AdapayMessage._on_disconnect
        client.on_subscribe = AdapayMessage._on_subscribe
        client.on_unsubscribe = AdapayMessage._on_unsubscribe
        client.on_message = AdapayMessage._on_message

        user_name = 'Token|' + AdapayMessage.access_key + '|' + AdapayMessage.instance_id
        token = AdapayMessage._request_token()
        password = 'R|' + token
        client.username_pw_set(user_name, password)
        client.connect(AdapayMessage.broker_url, 1883, 60)
        client.loop_forever()

    @staticmethod
    def _request_token():
        expire_time = 30_000_000_000
        data = ApiRequest.post(adapay.base_url + pay_message_token, {'expire_time': expire_time})

        if 'succeeded' != data.get('status'):
            log_info('token request failed')

        return data.get('token', '')

