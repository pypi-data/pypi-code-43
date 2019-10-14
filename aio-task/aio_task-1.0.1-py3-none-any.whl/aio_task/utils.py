""" Broker produce tasks that will be processed by consumers. """
from importlib import import_module


def load_cache(cache_type):
    cache_module = import_module(f"aio_task.cache.{cache_type}")
    return getattr(cache_module, "Cache")


def load_producer(queue_type):
    queue_module = import_module(f"aio_task.queue.{queue_type}")
    return getattr(queue_module, "Producer")


def load_consumer(queue_type):
    queue_module = import_module(f"aio_task.queue.{queue_type}")
    return getattr(queue_module, "Consumer")
