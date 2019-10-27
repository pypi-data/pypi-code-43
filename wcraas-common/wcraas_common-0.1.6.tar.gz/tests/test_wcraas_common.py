#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Tests for `wcraas_common` package."""

import os
import pytest

from collections import namedtuple

from wcraas_common.config import AMQPConfig
from wcraas_common.wcraas_common import WcraasWorker
from wcraas_common.decorator import is_rpc, consume


def test_default_env_load():
    conf = AMQPConfig.fromenv()
    assert isinstance(conf, tuple)
    assert conf._fields == ("host", "port", "user", "password")
    assert conf.host == "localhost"
    assert conf.port == 5672
    assert conf.user == "guest"
    assert conf.password == "guest"

def test_custom_env_load():
    os.environ["COTTONTAIL_HOST"] = "127.0.0.1"
    os.environ["COTTONTAIL_PORT"] = "5673"
    os.environ["COTTONTAIL_USER"] = "admin"
    os.environ["COTTONTAIL_PASS"] = "admin"
    conf = AMQPConfig.fromenv()
    assert conf.host == "127.0.0.1"
    assert conf.port == 5673
    assert conf.user == "admin"
    assert conf.password == "admin"

def test_subclass_worker_creation():
    # WcraasWorker is now an abstruct class and cannot be instantiated
    # without subclassing it to implement the start coroutine.
    class WcraasWorkerTest(WcraasWorker):
        async def start(self):
            pass
    conf = AMQPConfig.fromenv()
    worker = WcraasWorkerTest(conf, 20)
    assert str(worker) == f"{worker.__class__.__name__}(amqp={worker.amqp}, loglevel={worker.loglevel})"
    assert worker._amqp_pool is not None

def test_direct_worker_creation():
    conf = AMQPConfig.fromenv()
    # Ensure direct creation of WcraasWorker is not allowed
    with pytest.raises(TypeError):
        worker = WcraasWorker(conf, 20)

def test_decorator_is_rpc():
    command_name = "awesome_command"
    def fun(): pass
    assert getattr(fun, "is_rpc", False) is False
    @is_rpc(command_name)
    def fun(): pass
    assert getattr(fun, "is_rpc", False) is True
    assert getattr(fun, "rpc_command", None) == command_name

def test_decorator_consume():
    queue_name = "awesome_queue"
    def fun(): pass
    assert getattr(fun, "is_consume", False) is False
    @consume(queue_name)
    def fun(): pass
    assert getattr(fun, "is_consume", False) is True
    assert getattr(fun, "consume_queue", None) == queue_name

def test_worker_func_discover():
    # WcraasWorker is now an abstruct class and cannot be instantiated
    # without subclassing it to implement the start coroutine.
    class WcraasWorkerTest(WcraasWorker):
        async def start(self):
            pass
    conf = AMQPConfig.fromenv()
    w = WcraasWorkerTest(conf, 20)
    assert w._discover("is_rpc") == []
    assert w._discover("is_consume") == []
    @is_rpc("awesome_command")
    def foo(self): pass
    @consume("awesome_queue")
    def bar(self): pass
    WcraasWorker.foo = foo
    WcraasWorker.bar = bar
    assert w._discover("is_consume") == [w.bar]
