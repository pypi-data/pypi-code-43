"""
Cluster actor group messaging
"""

from __future__ import annotations

import enum
import logging
from collections import defaultdict
from typing import Any
from typing import List
from typing import Mapping
from typing import Set

from healer.cluster.talk import BusTalk
from healer.support.actor.master import WorkerActor
from healer.support.actor.proper import ProperRef
from healer.support.actor.proper import ProperRegistry
from healer.support.actor.proper import proper_receive_type
from healer.support.typing import AutoNameEnum
from healer.support.typing import override

logger = logging.getLogger(__name__)


@enum.unique
class BusTopic(AutoNameEnum):

    cluster_self_node = enum.auto()  # cluster identity anouncement
    cluster_hood_node = enum.auto()  # neighborhood discovery anouncement
    cluster_letter_publish = enum.auto()  # broadcast message to live cluster members

    device_actor_session = enum.auto()  # announce new device session in the storage


class BusActor(WorkerActor):
    "Cluster actor group message distributor"

    # topic -> subscriber set
    registration_map:Mapping[str, Set[ProperRef]] = None

    @override
    def on_start(self):
        self.registration_map = defaultdict(set)

    @override
    def on_stop(self):
        self.registration_map.clear()

    @proper_receive_type
    def on_publish(self, publish:BusTalk.Publish) -> None:
        subscriber_set = self.registration_map[publish.topic]
        if not subscriber_set:
            logger.warning(f"emtpy topic: {publish.topic}")
            return
        for actor_ref in subscriber_set.copy():  # copy for edit
            if actor_ref.is_alive():
                try:
                    actor_ref.tell(publish.message)
                except Exception:
                    subscriber_set.discard(actor_ref)
            else:
                    subscriber_set.discard(actor_ref)

    @proper_receive_type
    def on_subscribe(self, subscribe:BusTalk.Subscribe) -> None:
        self.registration_map[subscribe.topic].add(subscribe.actor)

    @proper_receive_type
    def on_unsubscribe(self, unsubscribe:BusTalk.Unsubscribe) -> None:
        self.registration_map[unsubscribe.topic].discard(unsubscribe.actor)


class EventBus:
    "distribute message to the topic actor group"

    @staticmethod
    def publish_message(topic:str, message:Any) -> None:
        "distribute message to the topic actors"
        bus_actor = ProperRegistry.find_by_class(BusActor)
        if bus_actor:
            bus_actor.tell(BusTalk.Publish(topic, message))
        else:
            logger.warning(f"no bus actor for message: {message}")
