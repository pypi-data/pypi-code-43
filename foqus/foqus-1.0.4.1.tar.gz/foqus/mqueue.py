#!/usr/bin/env python
import pika, uuid, threading
from foqus.configuration import *

import logging
import coloredlogs

if LOCAL is False:

    from azure_storage_logging.handlers import TableStorageHandler

    # configure the handler and add it to the logger
    logger = logging.getLogger(__name__)
    handler = TableStorageHandler(account_name=LOG_AZURE_ACCOUNT_NAME,
                                  account_key=LOG_AZURE_ACCOUNT_KEY,
                                  extra_properties=('%(hostname)s',
                                                    '%(levelname)s'))
    logger.setLevel(logging.DEBUG)
    logger.addHandler(handler)
else:

    logger = logging.getLogger(__name__)
    coloredlogs.install()
    logger.setLevel(logging.DEBUG)
    # create file handler which logs even debug messages
    fh = logging.FileHandler(LOG_PATH + 'trynfit_debug.log')
    fh.setLevel(logging.DEBUG)
    # create console handler with a higher log level
    ch = logging.StreamHandler()
    ch.setLevel(logging.ERROR)
    # create formatter and add it to the handlers
    formatter = logging.Formatter('[%(asctime)s] %(levelname)s [%(name)s:%(lineno)s] %(message)s', '%d/%b/%Y %H:%M:%S')
    ch.setFormatter(formatter)
    fh.setFormatter(formatter)
    # add the handlers to logger
    logger.addHandler(ch)
    logger.addHandler(fh)


class RabbitMQ:
    def __init__(self, mqueue_address=MESSAGE_QUEUE_ADDRESS, mqueue_name="backend", mqueue_port=5672, mqueue_ssl=False,
                 mqueue_user=MESSAGE_QUEUE_USER, mqueue_password=MESSAGE_QUEUE_PASSWORD, headers=None, callback=None, no_ack=False):
        self.consuming_thread = None
        self.mqueue_name = mqueue_name
        self.callback = callback
        self.no_ack = no_ack
        self.headers = headers
        conn_params = pika.ConnectionParameters(
            host=mqueue_address,
            port=mqueue_port,
            ssl=mqueue_ssl,
            # virtual_host=MESSAGE_QUEUE_VIRTUAL_HOST,
            credentials=pika.PlainCredentials(mqueue_user, mqueue_password),
            # Turn off heartbeats to avoid long task connection down
            heartbeat_interval=MESSAGE_QUEUE_HEARTBEAT_INTERVAL
        )
        self.connection = pika.BlockingConnection(conn_params)
        self.channel = self.connection.channel()
        self.channel.queue_declare(queue=mqueue_name, durable=True)
        self.channel.basic_qos(prefetch_count=1)

        if self.callback is not None:
            self.channel.basic_consume(self.callback,
                                       queue=self.mqueue_name,
                                       no_ack=self.no_ack)

    def publish(self, message_body=""):
        self.channel.basic_publish(exchange='',
                                   properties=pika.BasicProperties(
                                       delivery_mode=2,  # make message persistent
                                       headers=self.headers  # Add a key/value header
                                   ),
                                   routing_key=self.mqueue_name,
                                   body=message_body)
        logger.info("Sending message to the message queue '" + self.mqueue_name + "'")
        logger.info("Message header: '" + str(self.headers))
        logger.info("Message body: '" + message_body + "'")

    def consume_thread(self):
        if self.callback is None:
            logger.error("Please specify a callback function before starting consuming from the message queue!")
            return
        else:
            self.channel.basic_consume(self.callback,
                                       queue=self.mqueue_name,
                                       no_ack=self.no_ack)

        logger.info("'" +  self.mqueue_name + "' Message Queue Thread Started: Waiting for messages coming to the queue...")
        self.channel.start_consuming()

    def consume(self):
        logger.info("Starting '" +  self.mqueue_name + "' Message Queue consuming thread...")
        self.consuming_thread = threading.Thread(target=self.consume_thread)
        self.consuming_thread.start()

    def set_callback(self, callback_function):
        self.callback = callback_function

    def close(self):
        logger.info("Closing '" +  self.mqueue_name + "' Message Queue...")
        self.connection.close()



class RpcServer:
    def __init__(self, mqueue_address="localhost", mqueue_port=5672, mqueue_ssl=False,
                 mqueue_user="backend", mqueue_password="backend", operational_function=None):
        self.consuming_thread = None
        self.function = operational_function

        conn_params = pika.ConnectionParameters(
            host=mqueue_address,
            port=mqueue_port,
            ssl=mqueue_ssl,
            # virtual_host=VIRTUAL_HOST,
            credentials=pika.PlainCredentials(mqueue_user, mqueue_password),
            heartbeat_interval=0  # Turn off heartbeats to avoid long task connection down
        )
        self.connection = pika.BlockingConnection(conn_params)

        self.channel = self.connection.channel()
        self.channel.queue_declare(queue='rpc_queue')

    def on_request(self, ch, method, properties, body):
        response = self.function(headers=properties.headers, body=body)

        ch.basic_publish(exchange='',
                         routing_key=properties.reply_to,
                         properties=pika.BasicProperties(correlation_id=properties.correlation_id),
                         body=str(response))
        ch.basic_ack(delivery_tag=method.delivery_tag)

    def consume_thread(self):
        self.channel.basic_qos(prefetch_count=1)
        self.channel.basic_consume(self.on_request,
                                   queue='rpc_queue')

        logger.info('RPC Message Queue Thread Started: Waiting for messages coming to the queue...')
        self.channel.start_consuming()

    def consume(self):
        logger.info("Starting RPC Message Queue consuming thread...")
        self.consuming_thread = threading.Thread(target=self.consume_thread)
        self.consuming_thread.start()


class RpcClient(object):
    def __init__(self, mqueue_address="localhost", mqueue_port=5672, mqueue_ssl=False,
                 mqueue_user="backend", mqueue_password="backend", headers=None):
        self.response = None
        self.correlation_id = None
        self.headers = headers

        conn_params = pika.ConnectionParameters(
            host=mqueue_address,
            port=mqueue_port,
            ssl=mqueue_ssl,
            # virtual_host=VIRTUAL_HOST,
            credentials=pika.PlainCredentials(mqueue_user, mqueue_password),
            heartbeat_interval=0  # Turn off heartbeats to avoid long task connection down
        )
        self.connection = pika.BlockingConnection(conn_params)

        self.channel = self.connection.channel()
        result = self.channel.queue_declare(exclusive=True)
        self.callback_queue = result.method.queue
        self.channel.basic_consume(self.on_response, no_ack=True,
                                   queue=self.callback_queue)

    def on_response(self, ch, method, properties, body):
        if self.correlation_id == properties.correlation_id:
            self.response = body

    def call(self, headers=None, message_body=""):
        self.response = None

        if headers is not None:
            self.headers = headers

        self.correlation_id = str(uuid.uuid4())
        logger.info("Sending RPC message to the message queue")
        logger.info("RPC Message header: '" + str(self.headers))
        logger.info("RPC Message body: '" + str(message_body) + "'")
        self.channel.basic_publish(exchange='',
                                   routing_key='rpc_queue',
                                   properties=pika.BasicProperties(
                                       headers=self.headers,
                                       reply_to=self.callback_queue,
                                       correlation_id=self.correlation_id,
                                   ),
                                   body=str(message_body))
        while self.response is None:
            self.connection.process_data_events()
        return self.response
