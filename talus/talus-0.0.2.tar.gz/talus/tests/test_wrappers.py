"""
Tests the producer wrapper
"""
import json
import pytest

from talus import (DurableBlockingProducerWrapper,
                   DurableBlockingConsumerWrapper)


ROUTING_KEY = 'test.message.m'
QUEUE_NAME = 'test.queue.q'
BINDINGS = [{'routing_key': ROUTING_KEY, 'bound_queue': QUEUE_NAME},]
EXCHANGE = 'amq.direct'


@pytest.fixture
def producer():
    """
    Fixture producing an instance of the DurableBlockingProducerWrapper.  Disconnects on exit
    :return: DurableBlockingProducerWrapper
    """
    producer_wrapper = DurableBlockingProducerWrapper(BINDINGS, EXCHANGE)
    yield producer_wrapper
    producer_wrapper.disconnect()


@pytest.fixture
def consumer():
    """
    Fixture producing an instance of the DurableBlockingConsumerWrapper.  Disconnects on exit
    :return: DurableBlockingConsumerWrapper
    """
    consumer_wrapper = DurableBlockingConsumerWrapper(QUEUE_NAME)
    yield consumer_wrapper
    consumer_wrapper.disconnect()


@pytest.fixture
def empty_queue(consumer):
    """
    Fixture that empties the test queue
    :param consumer: Fixture returning Instance of the DurableBlockingConsumerWrapper
    :return: None
    """
    for method, properties, body in consumer.consume_generator(auto_ack=True):
        if method is None:
            consumer.cancel_consume_generator()
    return


@pytest.fixture
def single_message_on_queue(producer, empty_queue):
    """
    Fixture that produces a single message to an empty test queue
    :param producer: Fixture returning Instance of the DurableBlockingProducerWrapper
    :return: dict of the message that was placed on the queue
    """
    message = {'test_case': 'message_to_consume fixture'}
    producer.post(ROUTING_KEY, message)
    return message


def test_post_message(producer, consumer, empty_queue):
    """
    Given - An instantiated producer and consumer and an empty test queue
    When - Post a message to the test queue
    Then - Message consumed from the test queue matches the posted one.
    :param producer: Fixture returning Instance of the DurableBlockingProducerWrapper
    :param consumer: Fixture returning Instance of the DurableBlockingConsumerWrapper
    :param empty_queue: Fixture returning None that ensured an empty test queue
    :return: None
    """
    message = {"test_case": "test_post_message"}
    producer.post(ROUTING_KEY, message)

    for method, properties, body in consumer.consume_generator(auto_ack=True):
        assert (json.loads(body) == message)
        break


def test_consume_acknowledge(consumer, single_message_on_queue):
    """
    Given - An consumer instance and a message on a queue
    When - Consumer consumes and acknowledges message
    Then - Queue is empty
    :param consumer: Fixture returning Instance of the DurableBlockingConsumerWrapper
    :param single_message_on_queue: Fixture returning a dict body of a single message on the test queue
    :return: None
    """
    for i, (method, properties, body) in enumerate(consumer.consume_generator(auto_ack=False)):
        if i == 0:
            assert (json.loads(body) == single_message_on_queue)
            consumer.acknowledge_message(method.delivery_tag)
        if i == 1:
            assert body is None
            break


def test_consume_reject(consumer, single_message_on_queue):
    """
    Given - An consumer instance and a message on a queue
    When - Consumer consumes and rejects message
    Then - Queue is empty
    :param consumer: Fixture returning Instance of the DurableBlockingConsumerWrapper
    :param single_message_on_queue: Fixture returning a dict body of a single message on the test queue
    :return: None
    """
    for i, (method, properties, body) in enumerate(consumer.consume_generator(auto_ack=False)):
        if i == 0:
            assert (json.loads(body) == single_message_on_queue)
            consumer.reject_message(method.delivery_tag)
        if i == 1:
            assert body is None
            break


def test_consume_requeue(consumer, single_message_on_queue):
    """
    Given - An consumer instance and a message on a queue
    When - Consumer consumes and requeues message
    Then - Queue has the requeued message
    :param consumer: Fixture returning Instance of the DurableBlockingConsumerWrapper
    :param single_message_on_queue: Fixture returning a dict body of a single message on the test queue
    :return: None
    """
    for i, (method, properties, body) in enumerate(consumer.consume_generator(auto_ack=False)):
        if i == 0:
            assert (json.loads(body) == single_message_on_queue)
            consumer.requeue_message(method.delivery_tag)
        if i == 1:
            assert (json.loads(body) == single_message_on_queue)
            break

def test_listen(consumer, single_message_on_queue):
    """
    Given - A consumer instance and a single message on the queue
    When - Listening for messages on the queue
    Then - Single message is consumed
    :param consumer: Fixture returning Instance of the DurableBlockingConsumerWrapper
    :param single_message_on_queue: Fixture returning a dict body of a single message on the test queue
    :return: None
    """
    def verify_message(ch, method, properties, body):
        assert (json.loads(body) == single_message_on_queue)
        ch.basic_ack(method.delivery_tag)
        consumer.disconnect()

    consumer.listen(verify_message)


def test_context(single_message_on_queue):
    """
    Given - A single message on a queue
    When - When instantiating the consumer using 'with' and consuming a message
    Then - Consumer is connected inside the with and disconnected outside
    :return: None
    """
    with DurableBlockingConsumerWrapper(QUEUE_NAME) as consumer:
        for method, properties, body in consumer.consume_generator(auto_ack=True):
            assert (json.loads(body) == single_message_on_queue)
            break
        assert consumer.is_connected

    assert not consumer.is_connected


def test_invalid_routing_key(producer):
    """
    Given - A producer instance
    When - Post a message with a non-configured routing key
    Then - raise a value error
    :param producer: Fixture returning Instance of the DurableBlockingProducerWrapper
    :return: None
    """
    with pytest.raises(ValueError):
        producer.post('bad_key', {'foo': 'bar'})


def test_listen_connect(producer, consumer):
    """
    Given - A producer and consumer instance
    When - A message is posted and consumed first by listen
    Then - the consumer is connected.
    :param producer: Fixture returning Instance of the DurableBlockingProducerWrapper
    :param consumer: Fixture returning Instance of the DurableBlockingConsumerWrapper
    :return: None
    """
    producer.post(ROUTING_KEY, {'foo': 'bar'})

    def callback(ch, method, properties, body):
        ch.basic_ack(method.delivery_tag)
        assert consumer.is_connected
        consumer.disconnect()

    consumer.listen(callback)
