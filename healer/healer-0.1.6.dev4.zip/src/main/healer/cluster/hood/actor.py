"""
Cluster node neighbourhood discovery process
"""

from __future__ import annotations

import logging

from healer.cluster.talk import ConfigTalk
from healer.cluster.talk import HoodTalk
from healer.cluster.talk import NodeInfo
from healer.support.actor.master import WorkerActor
from healer.support.actor.proper import ProperRef
from healer.support.actor.proper import proper_receive_type
from healer.support.typing import override

from .mdns import BrowserMDNS
from .mdns import ListenerMDNS
from .mdns import SupportMDNS
from .mdns import WithHoodReactor

logger = logging.getLogger(__name__)


class HoodActor(
        WithHoodReactor,
        WorkerActor,
    ):
    """
    """

    wire_actor:ProperRef = None
    listener_mdns:ListenerMDNS = None
    browser_mdns:BrowserMDNS = None

    @override
    def on_start(self):
        self.customer_set = set()
        self.listener_mdns = ListenerMDNS(self)
        self.browser_mdns = BrowserMDNS(self.listener_mdns)
        self.query_master(ConfigTalk.ContextQuery())

    @override
    def on_stop(self):
        SupportMDNS.issue_service_terminate()
        self.browser_mdns.done = True
        self.browser_mdns = None

    @proper_receive_type
    def on_config_context_reply(self, message:ConfigTalk.ContextReply) -> None:
        self.wire_actor = message.wire_actor
        for node_info in self.listener_mdns.sevice_map.copy().values():
            self.react_node_detected(node_info)

    @proper_receive_type
    def on_issue_enable(self, message:HoodTalk.IssueEnable) -> None:
        SupportMDNS.issue_node_enable(message.node_info)

    @proper_receive_type
    def on_issue_disable(self, message:HoodTalk.IssueDisable) -> None:
        SupportMDNS.issue_node_disable(message.node_info)

    @override
    def react_node_detected(self, node_info:NodeInfo) -> None:
        self.publish_node_event(HoodTalk.NodeDetected(node_info))

    @override
    def react_node_undetected(self, node_info:NodeInfo) -> None:
        self.publish_node_event(HoodTalk.NodeUndetected(node_info))

    def publish_node_event(self, message:HoodTalk.Any) -> None:
        if self.wire_actor:
            self.wire_actor.tell(message)
        else:
            logger.warning(f"no wire_actor for message: {message}")
