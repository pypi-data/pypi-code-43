from .utils import encode_bson, decode_bson
from pika.exceptions import ProbableAccessDeniedError, ConnectionClosedByBroker
from re import match
import pika
import logging
import requests
import json
import uuid
import copy
import sys

LOGGER = logging.getLogger()  # root logger
LOGGER.setLevel(logging.INFO)
stream_handler = logging.StreamHandler(sys.stdout)
LOGGER.addHandler(stream_handler)


class CreateVhostException(Exception):
    pass


class CreatePermissionException(Exception):
    pass


class RabbitmqManagement(object):
    MANAGEMENT_PORT = 15672
    """
        Rabbitmq management api requests
    """

    def __init__(self, host, username, password):
        self.username = username
        self.password = password
        self.host = host
        self.uri = "http://%s:%s" % (self.host, self.MANAGEMENT_PORT)

    def request_with_credentials(self, url, method="get", data=None):
        req = getattr(requests, method)
        response = req(
            url,
            headers={"content-type": "application/json"},
            data=data,
            auth=(self.username, self.password)
        )
        response.raise_for_status()
        return json.loads(response.content)

    @property
    def messages(self):
        url = "%s/api/queues/" % self.uri
        res = self.request_with_credentials(url)
        return res

    def create_vhost(self, vhost):
        url = "%s/api/vhosts/%s" % (self.uri, vhost)
        try:
            self.request_with_credentials(url, method="put")
        except Exception:
            raise CreateVhostException("Attempt to create temporary vhost=%s failed. url=%r" % (vhost, url))

    def create_permission(self, vhost):
        url = "%s/api/permissions/%s/%s" % (self.uri, vhost, self.username)
        try:
            self.request_with_credentials(url, method="put",
                                          data=json.dumps({"configure": ".*", "write": ".*", "read": ".*"}))
        except Exception:
            raise CreatePermissionException("Attempt to configure premissions on vhost=%s failed. url=%r"
                                            % (vhost, url))

    @classmethod
    def create_vhost_and_permission(cls, vhost, *args, **kwargs):
        klass = cls(*args, **kwargs)
        klass.create_vhost(vhost=vhost)
        klass.create_permission(vhost=vhost)


class Queue(object):
    def __init__(self, uri, vhost, queue_name="", routing_key="", exchange="", exchange_type='fanout'):
        uri = uri.replace('<vhost>', vhost)
        self.uri = uri
        self.exchange = exchange
        self.queue_name = queue_name
        self.routing_key = routing_key
        self.exchange_type = exchange_type
        self.connection, self.channel = self.connect(uri)

    def close(self):
        self.connection.close()
        self.channel.close()

    @classmethod
    def connect(cls, uri):
        """
        :param uri: amqp://guest:guest@rabbitmq.marathon.mesos:5672/vhost?socket_timeout=10
        :return: connection, channel
        """
        LOGGER.info('Connection to %s', uri)
        params = pika.URLParameters(uri)
        try:
            connection = pika.BlockingConnection(params)
        except (ProbableAccessDeniedError, ConnectionClosedByBroker) as e:
            try:
                code, message = e
            except TypeError:
                code, message = e.args
            if match('NOT_ALLOWED - vhost \S+ not found', message):
                RabbitmqManagement.create_vhost_and_permission(params.virtual_host, params.host,
                                                               params.credentials.username, params.credentials.password)
            connection = pika.BlockingConnection(params)
        channel = connection.channel()
        return connection, channel

    def configure(self):
        """ Declare exchange and queue then queue bind to exchange
        :return:
        """
        self.exchange_declare()
        self.queue_declare()
        self.queue_bind()

    def queue_declare(self, durable=True, exclusive=False):
        return self.channel.queue_declare(queue=self.queue_name, durable=durable, exclusive=exclusive)

    def exchange_declare(self):
        return self.channel.exchange_declare(exchange=self.exchange, exchange_type=self.exchange_type)

    def queue_bind(self):
        return self.channel.queue_bind(queue=self.queue_name, exchange=self.exchange)

    def publish(self, body, properties=None):
        prop_dict = copy.deepcopy(properties)
        if properties:
            properties = pika.BasicProperties(**properties)
        try:
            self.channel.basic_publish(exchange=self.exchange, routing_key=self.queue_name, body=body,
                                       properties=properties)
        except Exception as cex:
            LOGGER.info('Exception=%s , Re-configuring the publisher' % cex)
            self.connection, self.channel = self.connect(self.uri)
            self.configure()
            self.publish(body, prop_dict)

    def get_message(self):
        method, properties, body = self.channel.basic_get(self.queue_name, auto_ack=True)
        return method, properties, decode_bson(body)


class BaseConsumer(object):
    def __init__(self, queue):
        self.channel = queue.channel
        self.connection = queue.connection
        self.queue_name = queue.queue_name
        self.callback_func = lambda ch, method, properties, body: self.process(ch, method, properties,
                                                                               decode_bson(body))

    def start_consuming(self, prefetch_count=1):
        self.channel.basic_qos(prefetch_count=prefetch_count)
        self.channel.basic_consume(self.queue_name, self.callback_func)
        self.channel.start_consuming()

    def process(self, ch, method, properties, body):
        """ Callback function
        :param body:
        :return:
        """
        raise NotImplementedError()

    def close(self):
        self.channel.close()
        self.connection.close()

    def start(self):
        """ basic_consume and start_consuming operations
        :return:
        """
        while True:
            try:
                self.start_consuming()
                LOGGER.info('Consuming started.')
            except pika.exceptions.StreamLostError as stream_lost_error:
                LOGGER.info(stream_lost_error)
                continue
            except pika.exceptions.ChannelWrongStateError as channel_wrong_state_error:
                LOGGER.info(channel_wrong_state_error)
                continue
            except pika.exceptions.ConnectionClosedByBroker as connection_closed_by_broker:
                LOGGER.info(connection_closed_by_broker)
                continue
            except pika.exceptions.AMQPChannelError as err:
                LOGGER.info("Caught a channel error: {}, stopping...".format(err))
                break
            except pika.exceptions.AMQPConnectionError:
                LOGGER.info("Connection was closed, retrying...")
                continue
            except KeyboardInterrupt:
                self.close()

    def get_and_publish(self):
        """ Consume one message and close connection
        :return:
        """
        self.channel.basic_qos(prefetch_count=1)
        self.channel.basic_consume(self.queue_name, self.callback_func, auto_ack=True)
        self.connection.process_data_events(time_limit=None)
        self.connection.close()

    def stop(self):
        self.channel.stop_consuming()
        LOGGER.info('Consuming stopped.')


class RpcClient(object):
    def __init__(self, uri, vhost, publish_to):
        """
        Rpc server is match with "options.wait_response" flag in body, publish the response to callback_queue
        """
        self.queue = Queue(uri, vhost)
        self.publish_to = publish_to
        self.callback_queue = self.queue.queue_declare(durable=False, exclusive=True).method.queue
        self.queue.channel.basic_consume(
            queue=self.callback_queue,
            on_message_callback=self.on_response,
            auto_ack=True)

    def on_response(self, ch, method, props, body):
        if self.corr_id == props.correlation_id:
            self.response = body

    def publish_and_wait(self, body, wait_response=True, continue_pipe=True):
        body['options'] = {
            "wait_response": wait_response,
            "continue_pipe": continue_pipe
        }
        self.response = None
        self.corr_id = str(uuid.uuid4())
        self.queue.channel.basic_publish(
            exchange='',
            routing_key=self.publish_to,
            body=encode_bson(body),
            properties=pika.BasicProperties(reply_to=self.callback_queue, correlation_id=self.corr_id)
        )
        while self.response is None:
            self.queue.connection.process_data_events()
        return self.response
