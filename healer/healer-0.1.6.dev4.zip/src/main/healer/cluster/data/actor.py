"""
Replicated database manager
"""

from __future__ import annotations

import logging
from typing import List
from typing import Set

from healer.cluster.support.reply import WithRouteReply
from healer.cluster.talk import ColumnState
from healer.cluster.talk import ConfigTalk
from healer.cluster.talk import DataTalk
from healer.cluster.talk import HoodTalk
from healer.persist.support.schemaless import NoSqlDatabase
from healer.persist.support.schemaless import NoSqlEvent
from healer.persist.support.schemaless import NoSqlReplicator
from healer.support.actor.master import ProjectActor
from healer.support.actor.master import WorkerActor
from healer.support.actor.proper import ProperRef
from healer.support.actor.proper import proper_receive_type
from healer.support.typing import override

logger = logging.getLogger(__name__)


class DataActor(
        NoSqlReplicator,
        WithRouteReply,
        WorkerActor,
    ):
    """
    """

    database:NoSqlDatabase = None
    store_list:List[str] = ['settings', 'control']

    wire_actor:ProperRef = None

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    @override
    def on_start(self):
        self.query_master(ConfigTalk.ContextQuery())

    @override
    def on_stop(self):
        pass

    @proper_receive_type
    def on_config_context_reply(self, message:ConfigTalk.ContextReply) -> None:
        self.wire_actor = message.wire_actor

    @proper_receive_type
    def on_store_query(self, message:DataTalk.StoreQuery) -> None:
        store = message.store
        if store in self.store_list:
            route = self.route_to_actor(message.route)
            state = ColumnState(col_id='some', time_start=1, time_finish=2)
            message = DataTalk.StoreReply(route=route, store=store, state_list=[state])
            self.transmit_message(message)
        else:
            logger.warning(f"no store: {store}")

    @proper_receive_type
    def on_store_reply(self, message:DataTalk.StoreReply) -> None:
        logger.debug(f"message: {message}")
        store = message.store
        route = self.route_to_actor(message.route)
        state = ColumnState(col_id='some', time_start=1, time_finish=2)
        message = DataTalk.RecordQuery(route=route, store=store, state=state)
        self.transmit_message(message)

    @proper_receive_type
    def on_record_query(self, message:DataTalk.RecordQuery) -> None:
        logger.debug(f"message: {message}")

    @proper_receive_type
    def on_record_event(self, message:DataTalk.RecordEvent) -> None:
        self.apply_event(message.event)

    def react_apply_event(self, event:NoSqlEvent) -> None:
        logger.debug(f"event: {event} @ {self}")

    def react_local_event(self, event:NoSqlEvent) -> None:
        logger.debug(f"event: {event} @ {self}")
        self.transmit_message(DataTalk.produce_record(event))

    @proper_receive_type
    def on_hood_node_connect(self, message:HoodTalk.LinkConnected) -> None:
        logger.debug(f"message: {message}")
        route = self.route_to_node(message.node_info.guid)
        for store in self.store_list:
            self.transmit_message(DataTalk.StoreQuery(route=route, store=store))

    @proper_receive_type
    def on_hood_node_disconnect(self, message:HoodTalk.LinkDisconnected) -> None:
        logger.debug(f"message: {message}")

    def transmit_message(self, message:DataTalk.Any) -> None:
        if self.wire_actor:
            self.wire_actor.tell(message)
        else:
            logger.warning(f"no wire_actor for message: {message}")


class SnapshotActor(
        WorkerActor,
    ):
    """
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
