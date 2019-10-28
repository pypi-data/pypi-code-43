import threading
import time

from amqpstorm import AMQPConnectionError, AMQPError, UriConnection
from minty import Base
from minty.cqrs import CQRS


class AMQPClient(Base):
    """AMQPClient manages the connection to and consumers of RabbitMQ.

    The client holds one connection to the AMQP server, subsequently one channel
    (virtual connection) for each registered consumer is created.

    `amqpstorm` library manages heartbeats (keepalives) in the background.
    """

    def __init__(self, config, max_retries: int = 5, cqrs: CQRS = None):
        """Initialize AMQPClient.

        :param rabbitmq_url: url to rabbitmq server.
        :type rabbitmq_url: str
        :param max_retries: max_retries to get connection, defaults to 5
        :type max_retries: int, optional
        :param cqrs: CQRS layer injected in consumers, defaults to None
        :type cqrs: CQRS, optional
        """
        self.rabbitmq_url = config["amqp"]["url"]
        self.max_retries = max_retries
        self.cqrs = cqrs

        self._threading_events = []
        self._connection = None
        self._active_consumers = []
        self._stopped = threading.Event()

        self._registered_consumers = []
        self.config = config

    def start(self):
        """Create new connection to AMQP server, starts and recovers consumers.

        Loop runs continually until `stop` method is called. Each loop the
        connection and consumer(s) health are checked and will be recovered if
        any failures are detected.

        `self.threading_events` is checked after a consumer is started or re-started
        to allow time for initialization of the consumer.
        """
        self._stopped.clear()
        if not self._connection or self._connection.is_closed:
            self._create_connection()

        while not self._stopped.is_set():
            try:
                self._connection.check_for_errors()
                if self._connection.is_closed:
                    raise AMQPConnectionError("connection closed")
                self._update_consumers()
                for event in self._threading_events:
                    event.wait(timeout=1)

                self._check_consumers()
                for event in self._threading_events:
                    event.wait(timeout=1)

                self._cleanup_thread_events()
            except AMQPError as error:
                self.logger.warning(error)
                self._stop_consumers()
                self._create_connection()
            time.sleep(1)

    def stop(self):
        """Stop all consumers and close connection to AMQP server."""
        while self._active_consumers:
            consumer = self._active_consumers.pop()
            consumer.stop()
        self._stopped.set()
        self._connection.close()

    def _create_connection(self):
        """Create a connection to the AMQP server."""
        attempts = 0
        while not self._stopped.is_set():
            attempts += 1
            try:
                self._connection = UriConnection(self.rabbitmq_url)
                break
            except AMQPError as error:
                self.logger.warning(error)
                if self.max_retries and attempts > self.max_retries:
                    raise Exception("max number of retries reached")
                time.sleep(min(attempts * 2, 30))

    def _update_consumers(self):
        """Start consumers in `_registered_consumers` and append to `_active_consumers`."""
        for consumer in self._registered_consumers:
            if not any(consumer == c for c in self._active_consumers):
                self._start_consumer(consumer)
                self._active_consumers.append(consumer)

    def _check_consumers(self):
        """Check if all consumers are active and restart if needed."""
        for consumer in self._active_consumers:
            if not consumer.active:
                if consumer.failed_attempts >= 3:
                    self.logger.error(
                        f"Too many failed attempts: ({consumer.failed_attempts}) "
                        + "for consumer: '{consumer.__class__.__name__}' stopping program."
                    )
                    self.stop()
                else:
                    time.sleep(consumer.failed_attempts * 5)
                    self._start_consumer(consumer)

    def _stop_consumers(self):
        """Call `stop` method on consumers in `_active_consumers`."""
        for consumer in self._active_consumers:
            consumer.stop()

    def _start_consumer(self, consumer):
        """Start a consumer in a new thread.

        `threading.Event` is set in `self.thread_events` to signal when
        consumer is done with initialization.

        :param consumer: rabbitmq consumer.
        :type consumer: BaseConsumer
        """
        event = threading.Event()
        self._threading_events.append(event)

        thread = threading.Thread(
            target=consumer.start, args=(self._connection, event)
        )
        thread.daemon = True
        thread.start()

    def _cleanup_thread_events(self):
        """Iterate over `_threading_events` and discard set / True events."""
        for event in self._threading_events:
            self._threading_events = [
                event for event in self._threading_events if not event.is_set()
            ]

    def register_consumers(self, consumers):
        for consumer in consumers:
            config = self.config["amqp"][consumer.__name__]
            try:
                dlx = config["dead_letter_exchange"]
                dead_letter_config = {
                    "exchange": dlx["exchange"],
                    "retry_time_ms": int(dlx["retry_time_ms"]),
                    "queue": (config["queue_name"] + "_retry"),
                }
            except KeyError:
                dead_letter_config = None

            initialized_consumer = consumer(
                queue=config["queue_name"],
                exchange=config["exchange"],
                cqrs=self.cqrs,
                qos_prefetch_count=int(config["qos_prefetching"]),
                dead_letter_config=dead_letter_config,
            )

            self._registered_consumers.append(initialized_consumer)
