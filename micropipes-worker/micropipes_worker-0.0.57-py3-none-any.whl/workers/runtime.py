import threading
import queue
import json
import time
from datetime import datetime
import pika.exceptions as exceptions
from micropipes.shared.utils import LOG, create_mq_connection, close_mq_connection, create_stats_job_entry, create_stats_customer_entry
from micropipes.shared.constants_runtime import *

MAX_BATCH_ENTRIES = 200
DEFAULT_SEND_DELAY = 10

class RuntimeClient(threading.Thread):

    def __init__(self, send_delay = DEFAULT_SEND_DELAY):
        threading.Thread.__init__(self)
        self.setDaemon(True)
        self.should_work = True
        self.connection = None
        self.channel = None
        self.send_delay = send_delay
        self.logs_que = queue.Queue()
        self.stats_que = queue.Queue()
        self.stats_customer_que = queue.Queue()

    def isReady(self):
        return (self.channel is not None)


    def _check_and_publish(self, _queue, callable_publish):
        entries = []
        try:
            while _queue.qsize() > 0 and len(entries) < MAX_BATCH_ENTRIES:
                log_entry = _queue.get_nowait()
                entries.append(log_entry)
                _queue.task_done()
        except queue.Empty:
            pass
        if len(entries) > 0:
            callable_publish(json.dumps(entries))

    def run(self):
        LOG.info('Starting RuntimeClient')
        self.connection = create_mq_connection()
        if not self.connection:
            LOG.error('Failed to create mq connection - exiting')
            return
        self.prepareChannel()
        last_sent = time.time()
        while self.should_work:
            try:
                self.connection.process_data_events()
                delta = time.time() - last_sent
                if delta < self.send_delay:
                    time.sleep(0.05)
                    continue
                # logs
                self._check_and_publish(self.logs_que, self._publish_log_entries)
                self._check_and_publish(self.stats_que, self._publish_stats_entries)
                self._check_and_publish(self.stats_customer_que, self._publish_stats_customer_entries)
                last_sent = time.time()
            except TypeError as e:
                LOG.error(e, exc_info=True)
                self.prepareChannel()
            except Exception as e:
                LOG.error(e, exc_info=True)
                if not self.channel or (self.channel.is_closed and isinstance(self.channel._closing_reason,
                                                 exceptions.ChannelClosedByBroker)):
                    self.prepareChannel()

        # LOG.info('Finishing RuntimeClient')

    def _stop(self):
        try:
            LOG.debug('Trying to stop RuntimeClient')
            self.should_work = False
            self.channel = None
            close_mq_connection(self.connection)
        except Exception as e:
            LOG.error(e, exc_info=True)

    def prepareChannel(self):
        LOG.debug('RuntimeClient preparing channel')
        if self.connection and self.connection.is_closed:
            LOG.warning('Reconnecting')
            self.connection = create_mq_connection()
        self.channel = self.connection.channel()
        self.channel.exchange_declare(exchange=MQ_RUNTIME_EXCHANGE, exchange_type=MQ_RUNTIME_EXCHANGE_TYPE)

    def _publish_log_entries(self , entry):
        try:
            self.channel.basic_publish(
                exchange=MQ_RUNTIME_EXCHANGE, routing_key=MQ_RUNTIME_LOGS_ADD,
                body=entry)
        except Exception as e:
            LOG.error(e, exc_info=True)

    def _publish_stats_entries(self , entry):
        try:
            self.channel.basic_publish(
                exchange=MQ_RUNTIME_EXCHANGE, routing_key=MQ_RUNTIME_STATS_ADD,
                body=entry)
        except Exception as e:
            LOG.error(e, exc_info=True)

    def _publish_stats_customer_entries(self , entry):
        try:
            self.channel.basic_publish(
                exchange=MQ_RUNTIME_EXCHANGE, routing_key=MQ_RUNTIME_STATS_CUSTOMER_ADD,
                body=entry)
        except Exception as e:
            LOG.error(e, exc_info=True)

    def thread_safe_stop(self):
        try:
            if self.connection:
                self.connection.add_callback_threadsafe(self._stop)
        except Exception as e:
            LOG.error(e, exc_info=True)

    def add_log(self, worker_type, worker_id, customer_id, job_id, log_level:LogLevel, log_message):
        if not isinstance(log_level, LogLevel):
            raise TypeError('log_level must be an instance of LogLevel Enum')
        log = {
           'time': datetime.utcnow().isoformat(),
           'worker_type': worker_type,
           'worker_id': worker_id,
           'customer_id': customer_id,
           'job_id': job_id,
           'log_level': log_level.value,
           'message': log_message
        }
        self.logs_que.put_nowait(log)

    def add_stats(self, worker_type, worker_id, customer_id, job_id, stats_name, stats_value):
        self.stats_que.put_nowait(
            create_stats_job_entry(worker_type, worker_id, customer_id, job_id, stats_name, stats_value)
        )

    def add_stats_customer(self, worker_type, worker_id, customer_id, stats_name, stats_value):
        self.stats_customer_que.put_nowait(
            create_stats_customer_entry(worker_type, worker_id, customer_id, stats_name, stats_value)
        )