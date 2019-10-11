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

from titanfe.messages import MessageType, AssignmentMessage, AssignmentContent
from titanfe.utils import create_uid
from titanfe.messages import TERMINATE

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

        self.process = None

        self.input_address = None
        self.connection = None
        self.send = None

    def __repr__(self):
        return f"BrickRunner(id={self.uid}, brick={self.brick}, input_address={self.input_address}"

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
        self.send = connection.send

        async for message in connection:
            if message.type == MessageType.AssignmentRequest:
                await self.send_assignment(message.content)

    async def send_assignment(self, input_address):
        """send the assignment to the runner and schedule a trigger package for inlet-runners"""
        self.input_address = input_address

        output_targets = None
        if self.brick.output:
            targets, ports = zip(*self.brick.output)

            target_runners = await asyncio.gather(
                *[target.runner_available() for target in targets]
            )
            output_targets = [
                (runner.brick.name, runner.input_address, port)
                for runner, port in zip(target_runners, ports)
            ]

        assignment = AssignmentContent(self.brick.description, output_targets)
        log.info("Assign runner: %r", assignment)
        await self.send(AssignmentMessage(assignment))
