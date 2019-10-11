#
# Copyright (c) 2019-present, wobe-systems GmbH
#
# Licensed under the Apache License, Version 2.0 (the "License");
# found in the LICENSE file in the root directory of this source tree.
#

"""The OUTPUT side of a brick (runner)"""

import asyncio

from titanfe.connection import Connection
from titanfe.constants import DEFAULT_PORT


class Output:
    """The output side of a brick runner creates a connection to the input of another brick runner.
       On this connection is will then send packets as requested by the input.
       The Output will also emit queue metrics every 0.1 sec if there are packets in the queue.

    Arguments:
        runner (BrickRunner): instance of a parent brick runner
        name (str): a name for the output destination
        address (NetworkAddress): the network address of the output's destination
    """

    def __init__(self, runner, name, address, port=DEFAULT_PORT):
        self.runner = runner
        self.name = f"Output.{name}"
        self.address = address
        self.log = runner.log.getChild(self.name)
        self.packets = asyncio.Queue()
        self.port = port
        self.metric_emitter = runner.metric_emitter

        # async in create
        self.connection = None
        self.output_task = None
        self.metric_task = None

    @classmethod
    async def create(cls, runner, target_name, address, port) -> "Output":
        """Creates a new instance and starts it's sending- and metrics-tasks"""
        output = cls(runner, target_name, address, port)
        await output.start()
        return output

    async def start(self):
        """start the metrics task and open a connection to the destination's input"""
        self.connection = await Connection.open(self.address, self.log)
        self.metric_task = asyncio.create_task(self.emit_queue_metrics())
        self.output_task = asyncio.create_task(self.provide_packets())

    async def stop(self):
        self.metric_task.cancel()
        self.output_task.cancel()
        await self.connection.close()

    async def add(self, packet):
        """add a packet to the output queue"""
        self.log.debug("queue for output: %s", packet)
        packet.update_output_entry()
        await self.packets.put(packet)

    async def provide_packets(self):
        """await a batch request from the destination's input and send corresponding packets"""
        async for message in self.connection:
            await asyncio.sleep(0)  # be cooperative
            self.log.debug("Got request %s", message)
            quantity_requested = message.content
            await self.output(quantity_requested)

    async def output(self, quantity_requested):
        """get packets from the queue and send them until the requested quantity is reached"""
        for _ in range(quantity_requested):
            packet = await self.packets.get()
            packet.update_output_exit()
            await self.connection.send(packet.as_message())
            self.packets.task_done()

    async def emit_queue_metrics(self):
        """endless coroutine to emit queue metrics every 100 ms if the queue ain't empty
        to be scheduled as task and cancelled when no longer required"""
        # TODO: there's some duplication in Input/Output
        # can we wrap that into some base class or a Queue-Component?
        while True:
            queue_length = self.packets.qsize()
            if queue_length:
                await self.metric_emitter.emit_for_queue(self.runner, self.name, queue_length)
            await asyncio.sleep(0.1)
