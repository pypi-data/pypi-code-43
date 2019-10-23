#
# Copyright (c) 2019-present, wobe-systems GmbH
#
# Licensed under the Apache License, Version 2.0 (the "License");
# found in the LICENSE file in the root directory of this source tree.
#

"""Encapsulate communication with the ControlPeer"""
import asyncio

from titanfe.connection import Connection
from titanfe.messages import RegisterMessage, AssignmentRequest, MessageType, SlowQueueAlert


class ControlPeer:
    """The ControlPeer class encapsulates the connection and communication
       with the ControlPeer instance.

    Arguments:
        runner (BrickRunner): THE brick runner
    """

    # pylint: disable=too-many-arguments
    def __init__(self, runner_uid, cp_address, logger, terminate_cb, new_input_source_cb):
        self.log = logger.getChild("ControlPeer")
        self.runner_uid = runner_uid
        self.cp_address = cp_address
        self.terminate_cb = terminate_cb
        self.new_input_source_cb = new_input_source_cb

        self.connection = None
        self.listener = None
        self.assignment = None
        self._assigned = asyncio.Event()

    @classmethod
    def from_runner(cls, runner):
        return cls(
            runner.uid,
            runner.cp_address,
            runner.log,
            runner.stop_processing,
            runner.input.add_sources,
        )

    async def connect(self):
        self.connection = await Connection.open(self.cp_address, self.log)
        self.listener = asyncio.create_task(self.listen())

    async def disconnect(self):
        self.listener.cancel()
        await self.connection.close()

    async def listen(self):
        """process incoming messages"""
        async for message in self.connection:
            if message.type == MessageType.Assignment:
                self.log.info("received assignment: %r", message.content)
                self.assignment = message.content
                self._assigned.set()

            elif message.type == MessageType.NewInputSource:
                self.new_input_source_cb(message.content)
            elif message.type == MessageType.Terminate:
                await self.terminate_cb()

    async def send(self, *args, **kwargs):
        if not self.connection:
            await self.connect()
            await self.register()
        return await self.connection.send(*args, **kwargs)

    async def register(self):
        await self.send(RegisterMessage(self.runner_uid))

    async def request_assignment(self, output_address):
        await self.send(AssignmentRequest(output_address))
        await self._assigned.wait()
        return self.assignment

    async def send_slow_queue_alert(self, group_name):
        """send brick scaling request"""
        await self.send(SlowQueueAlert(group_name))
