#
# Copyright (c) 2019-present, wobe-systems GmbH
#
# Licensed under the Apache License, Version 2.0 (the "License");
# found in the LICENSE file in the root directory of this source tree.
#

"""Encapsulate brick runner related things"""
import asyncio
import subprocess
import sys

import titanfe.log as logging
from titanfe.connection import NetworkAddress

from titanfe.messages import (
    MessageType,
    AssignmentMessage,
    InputSourceMessage,
    TERMINATE,
)
from titanfe.utils import create_uid

log = logging.getLogger(__name__)


class BrickRunner:
    """The BrickRunner can be used to start brick runner processes and hold corresponding data

    Arguments:
        controlpeer_address (NetworkAddress): the address on which the control peer is listening
        kafka_bootstrap_servers (str):
            'host[:port]' string (or list of 'host[:port]' strings)
            to contact the Kafka bootstrap servers on
    """

    def __init__(self, brick):
        self.uid = create_uid(prefix="R-")
        self.brick = brick

        self.available = asyncio.Event()

        self.known_sources = set()

        self.process = None
        self.output_address = None
        self.connection = None
        self.send = None

    def __repr__(self):
        return (
            f"BrickRunner(id={self.uid},"
            f"brick={self.brick},"
            f"output_address={self.output_address})"
        )

    def start(self) -> "BrickRunner":
        """Start a new brick runner process"""
        host, port = self.brick.flow.control_peer.server_address
        br_command = [
            sys.executable,
            "-m",
            "titanfe.apps.brick_runner",
            "-id",
            str(self.uid),
            "-controlpeer",
            f"{host}:{port}",
            "-kafka",
            self.brick.flow.control_peer.kafka_bootstrap_servers,
        ]

        log.debug("command: %r", br_command)
        self.process = subprocess.Popen(br_command)
        br_exitcode = self.process.poll()
        if br_exitcode is not None:
            log.error("Failed to start runner. (%s)", br_exitcode)
            return None

        return self

    async def stop(self):
        """request and await runner termination"""
        await self.send(TERMINATE)
        exit_code = self.process.poll()
        while exit_code is None:
            await asyncio.sleep(0.01)
            exit_code = self.process.poll()

        log.info("%s terminated.", self)
        return self

    async def process_messages(self, connection):
        """ process incoming messages"""
        self.send = connection.send

        async for message in connection:
            if message.type == MessageType.AssignmentRequest:
                self.output_address = NetworkAddress(*message.content)
                await self.send_assignment()
            if message.type == MessageType.SlowQueueAlert:
                self.brick.handle_slow_consumer(message.content)

    async def send_assignment(self):
        """send the assignment to the runner"""
        assignment = self.brick.create_assignment()
        self.known_sources = set(assignment.input_sources)

        log.info("Assign runner: %r", assignment)
        await self.send(AssignmentMessage(assignment))
        self.available.set()

    async def update_input_sources(self, input_sources):
        """notify following bricks about a scaling and the corresponding new source for their inputs
        """
        await self.available.wait()
        new_sources = set(input_sources).difference(self.known_sources)
        if new_sources:
            self.known_sources.update(new_sources)
            await self.send(InputSourceMessage(new_sources))
