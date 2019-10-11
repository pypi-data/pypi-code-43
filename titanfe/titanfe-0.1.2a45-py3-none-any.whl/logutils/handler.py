#
# Copyright (c) 2019-present, wobe-systems GmbH
#
# Licensed under the Apache License, Version 2.0 (the "License");
# found in the LICENSE file in the root directory of this source tree.
#

"""custom Handlers for titan logging"""

import sys
import atexit
import logging
from logging.config import ConvertingList
from logging.handlers import QueueHandler, QueueListener
from multiprocessing import Queue

from kafka import KafkaProducer


class QueueLogHandler(QueueHandler):
    """Puts Logrecords into a Queue an runs a separate Thread
      in which the records are processed by attached handlers

    Arguments:
        handlers (Sequence[logging.Handler]): attach handlers to the QueueListener
    """

    def __init__(self, handlers):
        queue = Queue()
        QueueHandler.__init__(self, queue)

        if isinstance(handlers, ConvertingList):
            # entries are converted in __getitem__ :/
            handlers = [handlers[i] for i in range(len(handlers))]

        self._listener = QueueListener(self.queue, *handlers, respect_handler_level=True)

        self.start()
        atexit.register(self.stop)

    def start(self):
        self._listener.start()

    def stop(self):
        self._listener.stop()

    def emit(self, record):  # pylint: disable=useless-super-delegation
        return super().emit(record)


class KafkaLogHandler(logging.Handler):
    """Stream LogRecords to Kafka

    Arguments:
        bootstrap_server (str): 'Host:Port' of a kafka bootstrap server
        topic (str): the kafka topic to produce into
    """
    def __init__(self, bootstrap_server, topic):
        logging.Handler.__init__(self)
        # self.level = logging.NOTSET
        # super().__init__(self)
        # TODO Buffer/Flush to improve performance?
        # self.flush_buffer_size = flush_buffer_size
        # self.flush_interval = flush_interval
        # self.Q = Queue()
        self.topic = topic
        self.producer = KafkaProducer(bootstrap_servers=bootstrap_server, key_serializer=str.encode)

    def emit(self, record):
        """emits the record"""
        if record.name.startswith("kafka"):
            # drop kafka logging to avoid infinite recursion
            return

        try:
            # TODO: format/encode as needed
            log_message = self.format(record)
            self.producer.send(self.topic, log_message)
        except Exception:  # pylint: disable=broad-except
            import traceback

            exc_info = sys.exc_info()
            traceback.print_exception(exc_info[0], exc_info[1], exc_info[2], None, sys.stderr)
            del exc_info

    def close(self):
        self.producer.close()
        logging.Handler.close(self)
