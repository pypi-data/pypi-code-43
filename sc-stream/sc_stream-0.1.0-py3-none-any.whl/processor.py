#!/usr/bin/env python

import os
import sys
import json

from kafka import KafkaConsumer, KafkaProducer
from .http_status_server import HttpHealthServer
from .task_args import get_kafka_binder_brokers, get_input_channel, get_output_channel
from .message import Message

class Processor:
    def __init__(self):
        self.consumer = KafkaConsumer(get_input_channel(), bootstrap_servers=[get_kafka_binder_brokers()])
        self.producer = KafkaProducer(bootstrap_servers=[get_kafka_binder_brokers()])

    def run(self):
        HttpHealthServer.run_thread()

        while True:
            for message in self.consumer:
                returned_message = process_message(message)
                producer.send(
                    get_output_channel(),
                    key = returned_message.key,
                    value = returned_message.value,
                    headers = returned_message.headers)

    """
    默认透传key和headers。
    如果不希望默认行为，需重写该方法。
    """
    def process_message(self, message):
        return Message(
            key = message.key,
            value = process_value(message.value),
            headers = message.headers)

    """
    默认value为utf-8编码的json字符串。
    如果不符合该规范，需重写该方法。
    """
    def process_value(self, value):
        json_string = bytearray(value).decode()
        json_value = json.loads(json_string)
        returned_json_value = process_json_value(json_value)
        returned_json_string = json.dumps(returned_json_value)
        return returned_json_string.encode('utf-8')

    """
    默认透传value。
    绝大部分情况下都需要重写该方法提供业务功能。
    参数 json_value 为 json.loads 后的结果。
    返回结果确保能被 json.dumps 正确序列化成字符串。
    """
    def process_json_value(self, json_value):
        return json_value