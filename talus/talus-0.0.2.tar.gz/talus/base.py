"""
Base wrapper definition shared by both consumer and producer wrappers
"""

import logging

import pika
from pika.exceptions import (
    AMQPConnectionError,
    AMQPHeartbeatTimeout,
    ChannelClosed,
    ChannelWrongStateError,
    ConnectionClosed,
    ConnectionWrongStateError,
    StreamLostError,
)
from retry.api import retry_call


logger = logging.getLogger(__name__)
SECONDS_60 = 60


class DurableBlockingBaseWrapper:
    """
    RabbitMQ connector that establishes a blocking connection and channel
    """

    def __init__(
        self,
        rabbitmq_host: str,
        rabbitmq_port: int,
        rabbitmq_user: str,
        rabbitmq_pass: str,
        retry_delay: int,
        retry_backoff: int,
        retry_jitter: int,
        retry_max_delay: int,
        connection_name: str,
        prefetch_count: int,
    ):
        """
        Constructor for the base connector

        :param rabbitmq_host: Host name or IP of the rabbitMQ server. e.g. 127.0.0.1

        :param rabbitmq_port: Port the rabbitmq server listens on e.g. 5672

        :param rabbitmq_user: Username for the rabbitMQ server e.g. guest

        :param rabbitmq_pass: Password for the rabbitMQ server e.g. guest

        :param retry_delay: initial delay between attempts.

        :param retry_backoff: multiplier applied to delay between attempts.

        :param retry_jitter: extra seconds added to delay between attempts.
                   fixed if a number, random if a range tuple (min, max)

        :param retry_max_delay: the maximum value of delay.

        :param connection_name: Name of the connection that will be visible in the rabbitmq admin console

        :param prefetch_count: Number of un-acked messages that can be consumed
        """
        self.connection_parameters = pika.ConnectionParameters(
            host=rabbitmq_host,
            port=rabbitmq_port,
            credentials=pika.credentials.PlainCredentials(rabbitmq_user, rabbitmq_pass),
            heartbeat=SECONDS_60,
            client_properties={"connection_name": connection_name},
        )
        self.connection = None
        self.channel = None
        self.prefetch_count = prefetch_count
        self.retry_config = {
            "exceptions": (
                AMQPConnectionError,
                AMQPHeartbeatTimeout,
                ChannelClosed,
                ChannelWrongStateError,
                ConnectionClosed,
                ConnectionWrongStateError,
                StreamLostError,
            ),
            "delay": retry_delay,
            "backoff": retry_backoff,
            "jitter": retry_jitter,
            "max_delay": retry_max_delay,
            "tries": -1,
        }

    @property
    def is_connected(self):
        """
        Current state of the connection.  Only updated when the connection is used.

        :return: Latest connection state
        """
        if self.connection:
            return self.connection.is_open
        return False

    def _connect(self):
        """
        Configures and initiates connection to the RabbitMQ server.

        :return: None
        """
        logger.debug(
            f"Attempt to connect to RabbitMQ: connection_params={self.connection_parameters}"
        )
        self.connection = pika.BlockingConnection(self.connection_parameters)
        logger.info(f"Connection Created")
        self.channel = self.connection.channel()
        logger.info("Channel Created")
        self.channel.confirm_delivery()  # ensure persistence prior to message confirmation
        self.channel.basic_qos(
            prefetch_count=self.prefetch_count
        )  # Number of un-Acked message delivered at a time
        logger.info("Channel configured")

    def connect(self):
        """
        Retries as configured the connection to the RabbitMQ server.

        :return: None
        """
        retry_call(self._connect, **self.retry_config)

    def disconnect(self):
        """
        Closes connection and related channels to the RabbitMQ Server.

        :return: None
        """
        if self.is_connected:
            self.connection.close()
        logger.warning(f"Disconnected from RabbitMQ: " f"connection={self.connection_parameters}")

    def __enter__(self):
        """
        Entry for with context manager.

        :return: connected instance of self
        """
        self.connect()
        return self

    def __exit__(self, exc_type, value, traceback):
        """
        Exit for with context manager.  Disconnects from rabbitmq

        :return: None
        """
        self.disconnect()
