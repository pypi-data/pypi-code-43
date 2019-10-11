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
from titanfe.messages import BrickDescription

from .runner import BrickRunner

log = logging.getLogger(__name__)


class Brick:
    """Encapsulate the Brick functions"""
    def __init__(self, flow, name, module_path, parameters):

        self.uid = create_uid("B-")

        self.flow = flow
        self.name = name
        self.module_path = module_path
        self.parameters = parameters
        self.inlet = False
        self.output = None
        self.runners = []

    def __repr__(self):
        return (
            f"Brick({self.name}, {self.uid}, {self.module_path}, "
            f"parameters={self.parameters})"
            )

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

        parameters.update(brick_instance_config.get("Parameters", {}))
        name = brick_instance_config.get("Name", identifier)
        return cls(flow, name, module_path, parameters)

    def start(self):
        self.start_new_runner()

    def start_new_runner(self):
        runner = BrickRunner(self).start()
        self.runners.append(runner)
        self.flow.control_peer.runners[runner.uid] = runner

        log.debug("%s started runner %s", self, runner)

    async def stop(self):
        for runner in self.runners:
            await runner.stop()
            del self.flow.control_peer.runners[runner.uid]
            self.runners.remove(runner)

    async def runner_available(self) -> BrickRunner:
        """waits until a runner for the brick has registered it's input address"""
        runner = first(
            runner for runner in self.runners if runner.input_address is not None
        )
        while not runner:
            await asyncio.sleep(0.0001)
            runner = first(
                runner for runner in self.runners if runner.input_address is not None
            )

        return runner

    @property
    def description(self):
        return BrickDescription(
            flowname=self.flow.name,
            name=self.name,
            uid=self.uid,
            path_to_module=str(self.module_path),
            parameters=self.parameters,
            is_inlet=self.inlet,
        )
