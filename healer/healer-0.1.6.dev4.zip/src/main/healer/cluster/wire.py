"""
Cluster network provider
"""

from __future__ import annotations

import logging
import threading
from dataclasses import dataclass
from typing import Any
from typing import List
from typing import Mapping
from urllib.parse import urlparse

import zmq

from healer.support.actor.master import WorkerActor
from healer.support.actor.proper import ProperRef
from healer.support.actor.proper import ProperRegistry
from healer.support.actor.proper import proper_receive_basetype
from healer.support.actor.proper import proper_receive_type
from healer.support.files import FilesSupport
from healer.support.network import NetworkSupport
from healer.support.typing import override
from healer.support.typing import unused
from healer.support.wired.typing import WiredBytes

from .codec import WireCodec
from .codec import WirePacket
from .talk import ConfigTalk
from .talk import DataTalk
from .talk import FileTalk
from .talk import HoodTalk
from .talk import NodeInfo
from .talk import WireMissive
from .talk import WireTalk
from .zeromq import SupportZMQ

frozen = dataclass(frozen=True)

logger = logging.getLogger(__name__)


class WireActorRef(ProperRef):
    """
    proxy to remote wire actor
    """

    local_guid:WiredBytes = None
    remote_guid:WiredBytes = None
    client_socket:zmq.Socket = None

    def __init__(self,
            local_guid:WiredBytes,
            remote_guid:WiredBytes,
            client_socket:zmq.Socket,
        ):
        self.local_guid = local_guid
        self.remote_guid = remote_guid
        self.actor_urn = remote_guid.to_urn()
        self.client_socket = client_socket

    @override
    def ask(self, message, block=True, timeout=None):
        raise RuntimeError(f"TODO")

    @override
    def tell(self, message:WireMissive) -> None:
        "serialize message and send packet"
        assert isinstance(message, WireMissive), f"need wire: {message}"
        # packet proper
        packet = WireCodec.message_encode(message)
        # deflate routing
        if packet.src == self.local_guid:
            packet.src = WiredBytes.empty()
        if packet.dst == self.remote_guid:
            packet.dst = WiredBytes.empty()
        self.client_socket.send_multipart(packet.send_part_list)

    @override
    def is_alive(self) -> bool:
        return not self.client_socket.closed

    @override
    def stop(self, block=True, timeout=None):
        raise RuntimeError(f"TODO")


class WireSupport:
    """
    """

    @staticmethod
    def default_node_id():
        return WiredBytes.from_hex(FilesSupport.machine_id())

    @staticmethod
    def node_info_from(bind_url:str, node_guid:str) -> NodeInfo:
        public_address = NetworkSupport.public_address()
        private_address = NetworkSupport.private_address()
        bind_unit = urlparse(bind_url)
        node_info = NodeInfo(
            guid=node_guid,
            addr=private_address,  # TODO
            port=bind_unit.port,
        )
        return node_info


class WireActor(WorkerActor):
    """
    transport for node-to-node links
    """

    node_guid:WiredBytes

    node_info:NodeInfo
    server_socket:zmq.Socket
    server_thread:threading.Thread
    server_bind_url:str
    remote_link_map:Mapping[WiredBytes, WiredBytes]  # zmq link -> guid
    remote_node_map:Mapping[WiredBytes, WireActorRef]  # guid -> actor

    data_actor:ProperRef
    files_actor:ProperRef

    def __init__(self, node_guid:str=None, **kwargs):
        super().__init__(**kwargs)
        self.node_guid = node_guid or WireSupport.default_node_id()

    @override
    def on_start(self):
        self.remote_link_map = dict()
        self.remote_node_map = dict()
        self.server_socket = SupportZMQ.socket_router()
        self.server_bind_url = SupportZMQ.perform_local_bind(self.server_socket)
        self.node_info = WireSupport.node_info_from(self.server_bind_url, self.node_guid)
        self.server_thread = threading.Thread(target=self.server_task, daemon=True)
        self.server_thread.start()
        self.query_master(ConfigTalk.ContextQuery())

    @override
    def on_stop(self):
        for remote in self.remote_node_map.values():
            self.remote_node_delete(remote)

    def server_task(self) -> None:  # non-actor thread
        while not self.actor_stopped.is_set():
            part_list = self.server_socket.recv_multipart()
            list_size = len(part_list)
            if list_size == WirePacket.part_size:
                packet = WirePacket(part_list)
                self.tell(packet)  # forward to on_packet_receive
            else:
                logger.warning(f"wrong packet: {part_list}")

    @proper_receive_type
    def on_packet_receive(self, packet:WirePacket) -> None:
        "deserialize packet and dispatch message"
        packet_head = packet.head
        packet_link = WiredBytes(packet.link)
        remote_guid = self.remote_link_map.get(packet_link, None)
        # inflate routing
        if not packet.src and remote_guid:
            packet.src = remote_guid
        if not packet.dst:
            packet.dst = self.node_guid
        # dispatch message
        message = WireCodec.message_decode(packet)
        if WireTalk.LinkUp.missive_type == packet_head:
            self.remote_link_create(packet_link, message.node_info)
        elif WireTalk.LinkDown.missive_type == packet_head:
            self.remote_link_delete(packet_link, message.node_info)
        elif remote_guid:
            self.on_message_receive(message)  # forward to on_message_receive
        else:
            logger.warning(f"wrong packet: {packet}")

    def on_message_receive(self, message:WireMissive) -> None:
        "forward message from remote wire actor to local actor"
        logger.trace(f"message: {message}")
        if message.route.dst_id:
            # forward to specific local
            local = ProperRegistry.find_by_uid(message.route.dst_id)
            if local:
                local.tell(message)
            else:
                logger.warning(f"no local for message: {message}")
        else:
            # forward to local by message type
            if isinstance(message, DataTalk.Any):
                self.data_actor.tell(message)
            elif isinstance(message, FileTalk.Any):
                self.files_actor.tell(message)
            else:
                logger.warning(f"no route for message: {message}")

    def remote_link_create(self, link:WiredBytes, remote:NodeInfo) -> None:
        logger.trace(f"link: {link} remote: {remote}")
        self.remote_node_create(remote)
        self.remote_link_map[link] = remote.guid

    def remote_link_delete(self, link:WiredBytes, remote:NodeInfo) -> None:
        logger.trace(f"link: {link} remote: {remote}")
        self.remote_link_map.pop(link, None)
        self.remote_node_delete(remote)

    def remote_node_create(self, remote:NodeInfo) -> None:
        if remote.guid in self.remote_node_map:
            return
        logger.debug(f"remote: {remote}")
        remote_url = f"tcp://{remote.addr}:{remote.port}"
        client_socket = SupportZMQ.socket_dealer()
        client_socket.connect(remote_url)
        remote_ref = WireActorRef(self.node_guid, remote.guid, client_socket)
        self.remote_node_map[remote.guid] = remote_ref
        remote_ref.tell(WireTalk.LinkUp(node_info=self.node_info))
        self.publish_hood_event(HoodTalk.LinkConnected(node_info=remote))

    def remote_node_delete(self, remote:NodeInfo) -> None:
        if not remote.guid in self.remote_node_map:
            return
        logger.debug(f"remote: {remote}")
        remote_ref = self.remote_node_map.pop(remote.guid)
        remote_ref.tell(WireTalk.LinkDown(node_info=self.node_info))
        remote_ref.client_socket.close()
        self.publish_hood_event(HoodTalk.LinkDisconnected(node_info=remote))

    @proper_receive_type
    def on_hood_node_detect(self, message:HoodTalk.NodeDetected) -> None:
        if message.node_info == self.node_info:
            logger.debug(f"skip self node: {message.node_info}")
        else:
            logger.debug(f"register  node: {message.node_info}")
            self.remote_node_create(message.node_info)

    @proper_receive_type
    def on_hood_node_undetect(self, message:HoodTalk.NodeUndetected) -> None:
        if message.node_info == self.node_info:
            logger.debug(f"skip self  node: {message.node_info}")
        else:
            logger.debug(f"unregister node: {message.node_info}")
            self.remote_node_delete(message.node_info)

    def publish_hood_event(self, message:HoodTalk.Any) -> None:
        if self.data_actor:
            self.data_actor.tell(message)
        else:
            logger.warning(f"no data_actor for message: {message}")
        if self.files_actor:
            self.files_actor.tell(message)
        else:
            logger.warning(f"no files_actor for message: {message}")

    @proper_receive_type
    def on_config_context_reply(self, message:ConfigTalk.ContextReply) -> None:
        self.data_actor = message.data_actor
        self.files_actor = message.files_actor

    @proper_receive_type
    def on_self_node_query(self, message:HoodTalk.SelfNodeQuery) -> HoodTalk.Any:
        unused(message)
        return HoodTalk.SelfNodeReply(self.node_info)

    @proper_receive_basetype
    def on_message_transmit(self, message:WireMissive) -> None:
        "forward message from local actor to remote wire actor"
        logger.trace(f"message: {message}")
        if message.route.dst:  # specific remote
            remote = self.remote_node_map.get(message.route.dst, None)
            if remote:
                remote.tell(message)
            else:
                logger.warning(f"no remote for message: {message}")
        else:  # broadcast to live remote list
            for remote in self.remote_node_map.values():
                remote.tell(message)
