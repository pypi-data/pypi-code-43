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
        self.input, self.outputs = None, None
        self.control_peer = None
        self.brick = None

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
        self.input = await Input.create(self)
        self.control_peer = ControlPeer(self)

        brick, output_targets = await self.control_peer.request_assignment()
        self.log.info("received assignment: %r, %r", brick, output_targets)

        self.brick = Brick(self, BrickDescription(*brick))

        if output_targets:
            self.outputs = await asyncio.gather(
                *[
                    Output.create(self, name, address, port)
                    for name, address, port in output_targets
                ]
            )

        self.task_to_output_results = asyncio.create_task(self.output_results())

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
                self.log.debug("process packet: %s", packet)
                await self.brick.execute(packet)

    async def stop_processing(self):
        self.log.info("Stop Processing")
        await self.input.stop()
        self.brick.terminate()

    async def shutdown(self):
        """shuts down the brick runner"""
        self.log.info("Initiate Shutdown")
        self.task_to_output_results.cancel()
        await asyncio.gather(*[output.stop() for output in self.outputs])
        await self.metric_emitter.stop()
        await self.control_peer.disconnect()
        self.log.info("Shutdown sequence complete - should exit soon")

    async def output_results(self):
        """get results from the brick execution and add them to the output queues of this runner"""
        async for packet, port in self.brick.get_results():
            await asyncio.gather(
                *[
                    output.add(packet)
                    for output in self.outputs
                    if (port == output.port)
                ]
            )
            await asyncio.sleep(0)
