#
# Copyright (c) 2019-present, wobe-systems GmbH
#
# Licensed under the Apache License, Version 2.0 (the "License");
# found in the LICENSE file in the root directory of this source tree.
#

"""Encapsulate communication with the ControlPeer"""
import asyncio

from titanfe.connection import Connection
from titanfe.messages import RegisterMessage, AssignmentRequest, MessageType


class ControlPeer:
    """The ControlPeer class encapsulates the connection and communication
       with the ControlPeer instance.

    Arguments:
        runner (BrickRunner): THE brick runner
    """

    def __init__(self, runner):
        self.runner = runner
        self.log = runner.log.getChild("ControlPeer")

        self.connection = None
        self.listener = None

        self.assignment = None

    async def connect(self):
        self.connection = await Connection.open(self.runner.cp_address, self.log)
        self.listener = asyncio.create_task(self.listen())

    async def disconnect(self):
        self.listener.cancel()
        await self.connection.close()

    async def listen(self):
        async for message in self.connection:
            if message.type == MessageType.Assignment:
                self.assignment = message.content
            elif message.type == MessageType.Terminate:
                asyncio.create_task(self.runner.stop_processing())

    async def send(self, *args, **kwargs):
        if not self.connection:
            await self.connect()
            await self.register()
        return await self.connection.send(*args, **kwargs)

    async def register(self):
        await self.send(RegisterMessage(self.runner.uid))

    async def request_assignment(self):
        await self.send(AssignmentRequest(self.runner.input.server_address))
        while not self.assignment:
            await asyncio.sleep(0.01)

        return self.assignment

    async def alert_on_slow_queue(self):
        pass  # TODO
