"""
Cluster manager
"""

from __future__ import annotations

import logging
from typing import Any

from healer.config import CONFIG
from healer.support.actor.master import ProjectActor
from healer.support.actor.proper import ProperRef
from healer.support.actor.proper import proper_receive_type
from healer.support.typing import override
from healer.support.typing import unused
from healer.support.wired.typing import WiredBytes

from .bus import BusActor
from .bus import BusTopic
from .data.actor import DataActor
from .files.actor import FilesActor
from .hood.actor import HoodActor
from .talk import BusTalk
from .talk import ConfigTalk
from .talk import HoodTalk
from .talk import NodeInfo
from .wire import WireActor

logger = logging.getLogger(__name__)


class Cluster:
    ""


class ClusterActor(ProjectActor):
    """
    Cluster manager
    """

    node_guid:WiredBytes
    node_info:NodeInfo

    bus_actor:ProperRef
    hood_actor:ProperRef
    wire_actor:ProperRef
    data_actor:ProperRef
    files_actor:ProperRef

    def __init__(self, node_guid:WiredBytes=None, **kwargs):
        super().__init__(**kwargs)
        self.node_guid = node_guid
        self.node_info = None

    @override
    def on_start(self):
        super().on_start()
        self.bus_actor = self.worker_start(BusActor)
        self.wire_actor = self.worker_start(WireActor, node_guid=self.node_guid)
        self.data_actor = self.worker_start(DataActor)
        self.files_actor = self.worker_start(FilesActor)
        self.hood_actor = self.worker_start(HoodActor)
        self.wire_actor.tell(HoodTalk.SelfNodeQuery(), reply_to=self.actor_ref)

    @override
    def on_stop(self):
        super().on_stop()

    @proper_receive_type
    def on_config_context_query(self, message:ConfigTalk.ContextQuery) -> ConfigTalk.Any:
        unused(message)
        return ConfigTalk.ContextReply(
            bus_actor=self.bus_actor,
            wire_actor=self.wire_actor,
            hood_actor=self.hood_actor,
            data_actor=self.data_actor,
            files_actor=self.files_actor,
        )

    @proper_receive_type
    def on_self_node_reply(self, message:HoodTalk.SelfNodeReply) -> None:
        if self.node_info == message.node_info:
            logger.debug(f"no change")
            return
        if self.node_info:
            logger.debug(f"node disable")
            self.hood_actor.tell(HoodTalk.IssueDisable(self.node_info))
            self.node_info = None
        if message.node_info:
            logger.debug(f"node enable")
            self.node_info = message.node_info
            self.hood_actor.tell(HoodTalk.IssueEnable(self.node_info))
