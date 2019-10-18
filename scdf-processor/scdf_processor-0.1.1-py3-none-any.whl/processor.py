#!/usr/bin/env python

import os
import sys

from kafka import KafkaConsumer, KafkaProducer
from .http_status_server import HttpHealthServer
from .task_args import get_kafka_binder_brokers, get_input_channel, get_output_channel, get_reverse_string

class Processor:
    def __init__(self):
        self.consumer = KafkaConsumer(get_input_channel(), bootstrap_servers=[get_kafka_binder_brokers()])
        self.producer = KafkaProducer(bootstrap_servers=[get_kafka_binder_brokers()])

    def run(self):
        HttpHealthServer.run_thread()

        while True:
            for message in self.consumer:
                producer.send(get_output_channel(), process_message(message))

    def process_message(self, message):
        return message.value