"""
Replicated file store manager
"""

from __future__ import annotations

import logging

from healer.cluster.talk import ConfigTalk
from healer.cluster.talk import FileTalk
from healer.cluster.talk import HoodTalk
from healer.config import CONFIG
from healer.support.actor.master import WorkerActor
from healer.support.actor.proper import ProperRef
from healer.support.actor.proper import proper_receive_type
from healer.support.typing import override

logger = logging.getLogger(__name__)


class FilesActor(
        WorkerActor,
    ):
    """
    Replicated file store manager
    """

    wire_actor:ProperRef = None

    store_path:str = None

    def __init__(self, store_path:str=None, **kwargs):
        super().__init__(**kwargs)
        cluster_database = CONFIG['storage']['cluster_session']
        self.store_path = store_path or cluster_database

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
    def on_state_query(self, message:FileTalk.StateQuery):
        pass

    @proper_receive_type
    def on_state_reply(self, message:FileTalk.StateReply):
        pass

    @proper_receive_type
    def on_file_create(self, message:FileTalk.EventCreate):
        pass

    @proper_receive_type
    def on_file_delete(self, message:FileTalk.EventDelete):
        pass

    @proper_receive_type
    def on_hood_node_connect(self, message:HoodTalk.LinkConnected) -> None:
        logger.debug(f"message: {message}")

    @proper_receive_type
    def on_hood_node_disconnect(self, message:HoodTalk.LinkDisconnected) -> None:
        logger.debug(f"message: {message}")
