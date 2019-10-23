#
# Copyright (c) 2019-present, wobe-systems GmbH
#
# Licensed under the Apache License, Version 2.0 (the "License");
# found in the LICENSE file in the root directory of this source tree.
#

"""A Brick"""
import asyncio

from ruamel import yaml

import titanfe.log as logging

from titanfe.utils import create_uid, first
from titanfe.messages import BrickDescription, AssignmentContent, OutputTarget, InputSource

from .runner import BrickRunner

log = logging.getLogger(__name__)


class Brick:
    """Encapsulate the Brick functions"""

    # pylint: disable=too-many-arguments
    def __init__(
            self,
            flow,
            name,
            module_path,
            parameters,
            autoscale,
            autoscale_max_instances,
            autoscale_queue_level,
    ):

        self.uid = create_uid("B-")
        self.flow = flow
        self.name = name
        self.module_path = module_path
        self.parameters = parameters

        self.autoscale = autoscale
        self.autoscale_max_instances = autoscale_max_instances
        self.autoscale_queue_level = autoscale_queue_level

        self.input_connections = []
        self.output_connections = []
        self.targets = []

        self.runners = []
        self.tasks = []

    def __repr__(self):
        return (
            f"Brick({self.name}, {self.uid}, {self.module_path}, "
            f"parameters={self.parameters},"
            f"autoscale={self.autoscale},"
            f"autoscale_queue_level={self.autoscale_queue_level},"
            f"autoscale_max_instances={self.autoscale_max_instances})"
        )

    def __hash__(self):
        return hash(self.uid)

    def __eq__(self, other):
        if isinstance(other, Brick):
            return other.uid == self.uid
        return False

    @classmethod
    def from_config(cls, flow, brick_general_config, brick_instance_config, path_to_modul_dir):
        """Add brick configuration using default and flow-specific parameters if available"""
        identifier = brick_general_config["Name"]
        module_path = path_to_modul_dir / brick_general_config["Module"]

        config_file = module_path.parent / "config.yml"
        try:
            with open(config_file) as config_file:
                parameters = yaml.safe_load(config_file)
        except FileNotFoundError:
            parameters = {}

        autoscale = brick_instance_config.get("autoscale", False)
        autoscale_max_instances = brick_instance_config.get("autoscale_max_instances", 2)
        autoscale_queue_level = brick_instance_config.get("autoscale_queue_level", 25)

        parameters.update(brick_instance_config.get("Parameters", {}))

        name = brick_instance_config.get("Name", identifier)
        brick = cls(
            flow,
            name,
            module_path,
            parameters,
            autoscale,
            autoscale_max_instances,
            autoscale_queue_level,
        )

        return brick

    def update_connections(self, input_connections, output_connections):
        self.input_connections = input_connections
        self.output_connections = output_connections
        self.targets = {connection.target for connection in self.output_connections}

    def start(self):
        self.start_new_runner()

    def start_new_runner(self):
        """start a new brickrunner"""
        runner = BrickRunner(self).start()
        self.runners.append(runner)
        self.flow.control_peer.runners[runner.uid] = runner

        log.debug("%s started runner %s", self, runner)

        task = asyncio.create_task(self.announce_runner_to_targets(runner))
        self.tasks.append(task)
        task.add_done_callback(self.tasks.remove)

    async def stop(self):
        for runner in self.runners:
            await runner.stop()
            del self.flow.control_peer.runners[runner.uid]
            self.runners.remove(runner)

    async def announce_runner_to_targets(self, runner):
        if not self.targets:
            return

        await runner.available.wait()
        await asyncio.wait(
            {target.add_input_source(self, runner.output_address) for target in self.targets}
        )

    async def add_input_source(self, source_brick, source_address):
        """inform runners that a new input source has become available"""
        new_input_sources = [
            (connection.source.name, connection.source_port, source_address)
            for connection in self.input_connections
            if connection.source == source_brick
        ]

        await asyncio.wait(
            {runner.update_input_sources(new_input_sources) for runner in self.runners}
        )

    def create_assignment(self):
        """create an assignment for a brickrunner"""
        input_sources = [
            InputSource(connection.source.name, connection.source_port, runner.output_address)
            for connection in self.input_connections
            for runner in connection.source.runners
            if runner.available.is_set()
        ]

        output_targets = [
            OutputTarget(
                connection.target.name,
                connection.source_port,
                connection.target.autoscale_queue_level,
            )
            for connection in self.output_connections
        ]

        return AssignmentContent(self.description, input_sources, output_targets)

    def handle_slow_consumer(self, target_name):
        """Autoscaling: create new brick runner instance"""
        log.debug("scaling request for connection %s <-> %s", self.name, target_name)
        target = first(target for target in self.targets if target.name == target_name)
        target.scale()

    def scale(self):
        """scale self by starting another runner if the configuration allows it"""
        if not self.autoscale:
            log.warning("%s is consuming slowly, but not allowed to scale", self)
            return

        if len(self.runners) > self.autoscale_max_instances:
            log.warning(
                "%s is still consuming slowly, but maximum number of instances already reached",
                self,
            )
            return

        self.start_new_runner()

    @property
    def description(self):
        return BrickDescription(
            flowname=self.flow.name,
            name=self.name,
            uid=self.uid,
            path_to_module=str(self.module_path),
            parameters=self.parameters,
            is_inlet=not bool(self.input_connections),
        )
