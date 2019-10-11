"""
Consumer implementation of the base connection wrapper
"""

import logging
from typing import Callable, Generator

from retry.api import retry_call

from talus.base import DurableBlockingBaseWrapper


logger = logging.getLogger(__name__)


__all__ = ["DurableBlockingConsumerWrapper"]


class DurableBlockingConsumerWrapper(DurableBlockingBaseWrapper):
    """
    RabbitMQ connector for consuming from a single queue in RabbitMQ.
    """

    def __init__(
        self,
        consumer_queue: str,
        rabbitmq_host: str = "localhost",
        rabbitmq_port: int = 5672,
        rabbitmq_user: str = "guest",
        rabbitmq_pass: str = "guest",
        retry_delay: int = 1,
        retry_backoff: int = 2,
        retry_jitter: int = (1, 10),
        retry_max_delay: int = 300,
        prefetch_count: int = 1,
        connection_name: str = "consumer connection",
    ):
        """
        Constructor for the consumer connector

        :param consumer_queue: Name of the queue the consumer will listen for messages on.

        :param rabbitmq_host: Host name or IP of the rabbitMQ server. e.g. 127.0.0.1

        :param rabbitmq_port: Port the rabbitmq server listens on e.g. 5674

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
        super().__init__(
            rabbitmq_host=rabbitmq_host,
            rabbitmq_port=rabbitmq_port,
            rabbitmq_user=rabbitmq_user,
            rabbitmq_pass=rabbitmq_pass,
            retry_delay=retry_delay,
            retry_backoff=retry_backoff,
            retry_jitter=retry_jitter,
            retry_max_delay=retry_max_delay,
            prefetch_count=prefetch_count,
            connection_name=connection_name,
        )
        self.consumer_queue = consumer_queue

    def _connect_consumer(self) -> None:
        """
        Configures and initiates consumer connection to the RabbitMQ server.
        :return:
        """
        if not self.is_connected:
            super().connect()

        self.channel.queue_declare(queue=self.consumer_queue, durable=True)
        logger.info(f"Queue Created: queue={self.consumer_queue}")

    def connect(self) -> None:
        """
        Retries configuration of consumer connection to the RabbitMQ server
        :return:
        """
        retry_call(self._connect_consumer, **self.retry_config)
        logger.info(f"Connected to RabbitMQ: " f"connection={self.connection_parameters}")

    def _listen(self, callback: Callable) -> None:
        """
        Listens for messages on the channel configured on the consumer instance

        :param callback: Function to execute when a message is recieved. with the signature
        (ch, method, properties, body).
        ch: Copy of the channel used to acknowledge receipt (pika.Channel)
        method: Management keys for the delivered message e.g. delivery mode (pika.spec.Basic.Deliver)
        properties: Message properties (pika.spec.BasicProperties)
        body: Message body for a transfer message (bytes)

        :return: None
        """
        if not self.is_connected:
            self.connect()
        logger.info(f"Starting Listener on Queue: consumer_queue={self.consumer_queue}")
        self.channel.basic_consume(queue=self.consumer_queue, on_message_callback=callback)
        self.channel.start_consuming()

    def listen(self, callback: Callable) -> None:
        """
        Retries calls to _listen

        :param callback: Function to execute when a message is recieved. with the signature
        (ch, method, properties, body).
        ch: Copy of the channel used to acknowledge receipt (pika.Channel)
        method: Management keys for the delivered message e.g. delivery mode (pika.spec.Basic.Deliver)
        properties: Message properties (pika.spec.BasicProperties)
        body: Message body for a transfer message (bytes)

        :return: None
        """
        retry_call(self._listen, fargs=[callback], **self.retry_config)

    def consume_generator(self, auto_ack=False, inactivity_timeout: float = .1) -> Generator:
        """
        Creates a generator for messages that are on the instance consumer_queue.
        Retry logic is not applied to prevent the resetting of the generator cursor

        :param inactivity_timeout:

        :return: Generator of (method, properties, body)
        """
        if not self.is_connected:
            self.connect()
        logger.info(f"Creating consumer generator on Queue: consumer_queue={self.consumer_queue}")
        return self.channel.consume(
            queue=self.consumer_queue, auto_ack=auto_ack, inactivity_timeout=inactivity_timeout
        )

    def cancel_consume_generator(self) -> None:
        """
        Resets the active consume generator
        :return: None
        """
        logger.info(f"Cancelling consumer generator on Queue: consumer_queue={self.consumer_queue}")
        self.channel.cancel()

    def acknowledge_message(self, delivery_tag) -> None:
        """
        Record a message as acknowledged.
        Retry logic is not applied since creating a new channel would be unable
        to acknowledge the message recieved on the now dead channel

        :param delivery_tag: method.delivery_tag

        :return: None
        """
        self.channel.basic_ack(delivery_tag)

    def reject_message(self, delivery_tag) -> None:
        """
        Record a message as rejected.  Will go to dead letter exchange if configured on the server.
        Retry logic is not applied since creating a new channel would be unable
        to acknowledge the message recieved on the now dead channel

        :param delivery_tag: method.delivery_tag

        :return: None
        """
        self.channel.basic_reject(delivery_tag=delivery_tag, requeue=False)

    def requeue_message(self, delivery_tag) -> None:
        """
        Return message back to the queue.
        Retry logic is not applied since creating a new channel would be unable
        to acknowledge the message recieved on the now dead channel

        :param delivery_tag: method.delivery_tag

        :return: None
        """
        self.channel.basic_nack(delivery_tag=delivery_tag, requeue=True)
