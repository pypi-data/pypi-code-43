#
# Copyright (c) 2019-present, wobe-systems GmbH
#
# Licensed under the Apache License, Version 2.0 (the "License");
# found in the LICENSE file in the root directory of this source tree.
#

"""Flow config: parsing and representation"""
import asyncio
from collections import defaultdict
from enum import IntEnum
from pathlib import Path
from typing import List

from ruamel import yaml

import titanfe.log as logging

from titanfe.constants import DEFAULT_PORT
from titanfe.utils import create_uid

from .brick import Brick

log = logging.getLogger(__name__)


class FlowState(IntEnum):
    ACTIVE = 1
    INACTIVE = 2


class Flow:
    """Represent a flow configuration with it bricks and connections

    Arguments:
        flow_config (dict): the flow configuration as dict
        bricks_config (dict): the bricks part of the configuration as dict
        path_to_bricks (Path): path to directory holding the "./bricks" folder
    """

    def __init__(self, control_peer, flow_config, bricks_config, path_to_bricks):
        self.control_peer = control_peer

        self.name = flow_config["Name"]
        self.uid = create_uid("F-")
        self.state = FlowState.INACTIVE

        bricks_general_config_by_name = {brick["Name"]: brick for brick in bricks_config}
        self.bricks = [
            Brick.from_config(
                self,
                bricks_general_config_by_name[brick_instance_config["Brick"]],
                brick_instance_config,
                path_to_bricks,
            )
            for brick_instance_config in flow_config["Bricks"]
        ]

        self.bricks_by_uid = {b.uid: b for b in self.bricks}
        connections = defaultdict(list)
        targets = set()
        for connection in flow_config["Connections"]:
            targets.add(connection["Target"])
            brick_name = connection["Source"]
            connections[brick_name].append(
                (connection["Target"], connection.get("Ports", {}).get("Source", DEFAULT_PORT))
            )

        bricks_by_name = {b.name: b for b in self.bricks}
        for brick in self.bricks:
            brick.output = [
                (bricks_by_name[target], port) for target, port in connections.get(brick.name, [])
            ]
            if brick.name not in targets:
                brick.inlet = True

    def __repr__(self):
        return f"Flow({self.name}, {self.bricks})"

    def start(self):
        """start brick runners for each brick in the flow"""
        log.debug("start flow: %s", self.name)
        self.state = FlowState.ACTIVE
        for brick in self.bricks:
            brick.start()

    async def stop(self):
        """send a stop signal to all bricks"""
        log.info("stopping all bricks for: %s", self)
        await asyncio.gather(*[brick.stop() for brick in self.bricks])
        self.state = FlowState.INACTIVE
        log.info("%s stopped", self)


def parse_flows(control_peer, config_file) -> List[Flow]:
    """parse a flow configuration file (yaml)"""
    config_root = Path(config_file).resolve().parent
    with open(config_file) as config:
        config = yaml.safe_load(config)

    flows = [
        Flow(control_peer, flow_config, config["Bricks"], config_root)
        for flow_config in config["Flows"]
    ]

    return flows
