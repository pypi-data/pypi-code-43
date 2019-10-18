import signal
import functools
import os
import logging

from typing import Callable

import pika.exceptions

from .connectors import Connector, Reconnector
from .message import MQMessage
from .publishers import Publisher, JSONPublisher


class Consumer:
    def __init__(self, connector: Connector, handler: Callable):
        self.connector = connector
        self.handler = handler

    def start_consuming(self):
        self.connector.create_connection()
        self.connector.channel.basic_consume(self.connector.queue, self.handler)
        self.connector.channel.start_consuming()

    def stop_consuming(self):
        self.connector.channel.stop_consuming()

    def run(self):
        try:
            self.start_consuming()
        except KeyboardInterrupt:
            pass
        finally:
            self.stop_consuming()

    def get_publisher(self, publisher_cls) -> Publisher:
        return publisher_cls(self.connector)

    # noinspection PyTypeChecker
    def get_json_publisher(self) -> JSONPublisher:
        return JSONPublisher(self.connector)


class ReconConsumer(Consumer):
    def __init__(self, connector: Reconnector, handler: Callable, logger: logging.Logger = None):
        assert isinstance(connector, Reconnector), 'connector must be Reconnector instance'
        self.logger = logger
        super().__init__(connector, handler)

    def run(self):
        while True:
            try:
                super(ReconConsumer, self).run()
                raise RuntimeError("Unreachable statement")
            except pika.exceptions.AMQPError:
                if self.logger:
                    self.logger.exception('RabbitMQ consumer exception')


class SafeConsumer(ReconConsumer):
    def term_sig_handler(self, signum, frame):
        self.received_signal = signum
        print(f'Received {signum} signal')
        if self.process_msg:
            self.got_term_signal = True
        else:
            print('Process was terminated')
            os._exit(signum)

    def add_signal_handlers(self):
        signal.signal(signal.SIGTERM, self.term_sig_handler)
        signal.signal(signal.SIGINT, self.term_sig_handler)

    def __init__(self, connector: Reconnector, handler: Callable, logger: logging.Logger = None):
        self.received_signal = None
        self.process_msg = False
        self.got_term_signal = False
        self.add_signal_handlers()

        def safe_wrapper(func):
            @functools.wraps(func)
            def wraps(*args, **kwargs):
                self.process_msg = True
                try:
                    result = func(*args, **kwargs)
                    if self.got_term_signal:
                        print('Process was terminated')
                        os._exit(self.received_signal or -1)
                    return result
                finally:
                    self.process_msg = False
            return wraps

        safe_handler = safe_wrapper(handler)
        super().__init__(connector, safe_handler, logger=logger)


class MultipleConsumer(Consumer):
    def __init__(self, connector: Connector, multi_handler: Callable):
        self.msg_limit = connector.prefetch_count
        self.mq_messages = []
        self.multi_handler = multi_handler
        super().__init__(connector, self.msg_handler)

    def msg_handler(self, channel, method, properties, body):
        self.mq_messages.append(MQMessage(channel, method, properties, body))
        if len(self.mq_messages) >= self.msg_limit or len(self.connector.channel._pending_events) == 0:
            self.multi_handler(self.mq_messages)
            while self.mq_messages:
                mq_msg = self.mq_messages.pop()
                mq_msg.channel.basic_ack(delivery_tag=mq_msg.method.delivery_tag)


class NotEmptyConsumer(Consumer):

    class CountCallback:
        def __init__(self, count: int, handler: Callable, finish_handler: Callable = None):
            self.count = count
            self.handler = handler
            self.finish_handler = finish_handler

        def __call__(self, ch, method, properties, body):
            self.handler(ch, method, properties, body)
            self.count -= 1
            if self.count <= 0:
                if self.finish_handler:
                    self.finish_handler()
                ch.stop_consuming()

    def __init__(self, connector: Connector, handler: Callable, finish_handler: Callable = None):
        self.finish_hadler = finish_handler
        super().__init__(connector, handler)

    def start_consuming(self):
        self.connector.create_connection()
        msg_count = self.connector.declared_queue.method.message_count
        if msg_count > 0:
            callback = self.CountCallback(msg_count, self.handler, finish_handler=self.finish_hadler)
            self.connector.channel.basic_consume(callback, queue=self.connector.queue)
            self.connector.channel.start_consuming()
        else:
            if self.finish_hadler:
                self.finish_hadler()

