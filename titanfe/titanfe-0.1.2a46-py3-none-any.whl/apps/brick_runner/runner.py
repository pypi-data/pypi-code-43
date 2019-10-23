#
# Copyright (c) 2019-present, wobe-systems GmbH
#
# Licensed under the Apache License, Version 2.0 (the "License");
# found in the LICENSE file in the root directory of this source tree.
#

"""The actual brick runner"""

import asyncio

import titanfe.log as logging

from titanfe.messages import BrickDescription

from .controlpeer import ControlPeer
from .input import Input
from .metrics import MetricEmitter
from .output import Output
from .brick import Brick
from .packet import Packet


class BrickRunner:
    """The BrickRunner will create an Input, get an Assignment from the control peer,
       create corresponding outputs and then start processing packets from the input.

    Arguments:
        uid (str): a unique id for the runner
        controlpeer_address (NetworkAddress): (host, port) of the control peer's server
        kafka_bootstrap_servers (str):
            'host[:port]' string (or list of 'host[:port]' strings)
            to contact the Kafka bootstrap servers on
    """

    def __init__(self, uid, controlpeer_address, kafka_bootstrap_servers):
        self.uid = uid
        self.log = logging.getLogger(f"{__name__}.{self.uid}")
        self.loop = asyncio.get_event_loop()
        self.kafka_bootstrap_servers = kafka_bootstrap_servers

        cp_host, cp_port = controlpeer_address.rsplit(":", 1)
        self.cp_address = cp_host, int(cp_port)

        # done async in setup
        self.input = None
        self.output = None
        self.control_peer = None
        self.brick = None

        self.setup_completed = asyncio.Event()

        self.metric_emitter = None
        self.task_to_output_results = None

    @classmethod
    async def create(cls, uid, controlpeer_address, kafka_bootstrap_servers):
        """Creates a brick runner instance and does the initial setup phase before returning it"""
        br = cls(uid, controlpeer_address, kafka_bootstrap_servers)  # pylint: disable=invalid-name
        await br.setup()
        return br

    async def setup(self):
        """does the inital setup parts that have to be awaited"""
        self.metric_emitter = await MetricEmitter.create(self.kafka_bootstrap_servers, self.log)
        self.input = Input(self)
        self.output = await Output.create(self)

        self.control_peer = ControlPeer.from_runner(self)

        brick, input_sources, output_targets = await self.control_peer.request_assignment(
            self.output.address
        )

        self.brick = Brick(self, BrickDescription(*brick))
        self.input.add_sources(input_sources)
        self.output.add_targets(output_targets, self.control_peer.send_slow_queue_alert)
        if output_targets:
            self.task_to_output_results = asyncio.create_task(self.output_results())
        self.setup_completed.set()

    async def run(self):
        """process items from the input"""
        self.log.info("start runner: %s", self.uid)

        if self.brick.is_inlet:
            # trigger processing
            await self.input.put(Packet())

        await self.process_input()
        await self.shutdown()
        self.log.info("Exit")

    async def process_input(self):
        with self.brick:
            async for packet in self.input:
                packet.update_input_exit()
                self.log.debug("process packet: %s", packet)
                await self.brick.execute(packet)

    async def stop_processing(self):
        """stop processing bricks"""
        self.log.info("Stop Processing")
        await self.input.close()
        self.brick.terminate()
        await self.output.close()
        for task in asyncio.all_tasks():
            task.cancel()

    async def shutdown(self):
        """shuts down the brick runner"""
        self.log.info("Initiate Shutdown")
        if self.task_to_output_results:
            self.task_to_output_results.cancel()
        await self.metric_emitter.stop()
        await self.control_peer.disconnect()
        self.log.info("Shutdown sequence complete - should exit soon")

    async def output_results(self):
        """get results from the brick execution and add them to the output queues of this runner"""
        async for packet, port in self.brick.get_results():
            await self.output[port].enqueue(packet)
