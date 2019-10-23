#
# Copyright (c) 2019-present, wobe-systems GmbH
#
# Licensed under the Apache License, Version 2.0 (the "License");
# found in the LICENSE file in the root directory of this source tree.
#

"""Handle creation of metric data and streaming it to Kafka"""

import asyncio
import os
import pickle
import platform
from abc import ABC
from dataclasses import dataclass, field

import aiokafka

from titanfe.utils import DictConvertable, iso_utc_time_string

# tiny little hack for development purposes only
DISABLED = os.getenv("TITAN_METRICS_DISABLED") is not None
ENABLED = not DISABLED


class MetricEmitter:
    """The MetricEmitter encapsulates creation of metric data and sending them to a Kafka instance

    Arguments:
        kafka_bootstrap_servers (str):
            'host[:port]' string (or list of 'host[:port]' strings)
            to contact the Kafka bootstrap servers on
        log (logging.logger): the parent's logger instance
    """

    def __init__(self, kafka_bootstrap_servers, log):
        self.log = log
        self.kafka_bootstrap_servers = kafka_bootstrap_servers
        self.kafka = None

    @classmethod
    async def create(cls, kafka_bootstrap_servers, log) -> "MetricEmitter":
        """Creates, starts and returns a MetricEmitter instance"""
        me = cls(kafka_bootstrap_servers, log)  # pylint: disable=invalid-name
        await me.start()
        return me

    async def start(self):
        """creates and starts the internal Kafka producer"""
        if ENABLED:
            self.log.info("Starting Kafka producer")
            self.kafka = aiokafka.AIOKafkaProducer(
                loop=asyncio.get_event_loop(),
                bootstrap_servers=self.kafka_bootstrap_servers,
                # key_serializer=str.encode,
                # value_serializer=str.encode
                value_serializer=pickle.dumps,
            )
            await self.kafka.start()

    async def emit(self, metrics_dict):
        self.log.metric("%s", metrics_dict)

        if self.kafka:
            await self.kafka.send("titanfe.metrics", metrics_dict)

    async def emit_for_packet(self, runner, packet, duration):
        pm = PacketMetricsAtBrick.generate(runner, packet, duration)  # pylint: disable=invalid-name
        await self.emit(pm.to_dict())

    async def emit_for_brick(self, runner, execution_time):
        bm = BrickMetrics.generate(runner, execution_time)  # pylint: disable=invalid-name
        await self.emit(bm.to_dict())

    async def stop(self):
        if self.kafka is not None:
            await self.kafka.stop()


class QueueWithMetrics(asyncio.Queue):
    """an ayncio.Queue that emits metrics (queue length)"""
    def __init__(self, emitter, queue_metrics, interval=0.1, maxsize=0):
        super().__init__(maxsize)

        self.metrics = asyncio.create_task(self.emit_metrics(emitter, queue_metrics, interval))

    async def emit_metrics(self, emitter, metrics, interval=0.1):
        """automatically scheduled as task"""
        while True:
            await asyncio.sleep(interval)
            queue_length = self.qsize()
            if queue_length:
                metrics.update(queue_length)
                await emitter.emit(metrics.to_dict())

    async def put(self, item):
        await super().put(item)


@dataclass
class MetricsMetadata(DictConvertable, ABC):
    """Information that every "metric" should contain"""

    flow: str = "FlowName?"
    brick: str = "BrickName?"
    runner: str = "RunnerUid?"
    host: str = platform.node()
    timestamp: str = field(default_factory=iso_utc_time_string)

    @staticmethod
    def extract_from_runner(runner):
        """extract the basic information from a brick runner instance"""
        if runner.brick:
            return dict(runner=runner.uid, brick=runner.brick.name, flow=runner.brick.flowname)

        return dict(runner=runner.uid)


@dataclass
class PacketMetricsAtBrick(MetricsMetadata):
    """Metric data for a packet being processed at a Brick"""

    content_type: str = "titan-packet-metrics"
    packet: str = "PacketUid?"
    execution_time: float = 0.0
    traveling_time: float = 0.0
    time_in_input: float = 0.0
    time_in_output: float = 0.0
    time_on_wire: float = 0.0
    at_outlet: bool = False  # TODO

    @classmethod
    def generate(cls, runner, packet, duration):
        return cls(
            **cls.extract_from_runner(runner),
            packet=packet.uid,
            execution_time=duration,
            traveling_time=packet.traveling_time,
            **packet.queue_times,
        )


@dataclass
class QueueMetrics(MetricsMetadata):
    """Metric data for Input/Output-queues"""

    content_type: str = "titan-queue-metrics"
    queue_name: str = "QueueName?"
    queue_length: int = 0

    @classmethod
    def generate(cls, runner, queue_name=None, queue_length=None):
        return cls(
            **cls.extract_from_runner(runner), queue_name=queue_name, queue_length=queue_length
        )

    def update(self, queue_length):
        self.timestamp = iso_utc_time_string()
        self.queue_length = queue_length


@dataclass
class BrickMetrics(MetricsMetadata):
    """Metric data for brick executions"""

    content_type: str = "titan-brick-metrics"
    execution_time: float = 0.0

    @classmethod
    def generate(cls, runner, execution_time):
        return cls(**cls.extract_from_runner(runner), execution_time=execution_time)
