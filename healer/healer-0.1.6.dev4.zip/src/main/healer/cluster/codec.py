"""
Wire message serialization
"""

from __future__ import annotations

from typing import List

from healer.support.parser import parser_render_ascii
from healer.support.parser import parser_render_hex
from healer.support.wired.typing import WiredBytes

from .talk import ActorRoute
from .talk import WireMissive
from .talk import WireStore


class PacketIndex:
    "zmq packet structure"

    link = 0  # remote zmq id
    src = 1  # remote node guid
    src_id = 2  # remote node actor id
    dst = 3  # local node guid
    dst_id = 4  # local actor id
    head = 5  # message type
    body = 6  # message content


class WirePacket:
    "zmq packet structure"

    part_size = 7
    part_list:List[bytes] = None

    def __init__(self, part_list:List[bytes]):
        self.part_list = part_list

    def __repr__(self):
        return (
            f"WirePacket("
            f"link={parser_render_hex(self.link)}, "
            f"src={self.src}/{self.src_id}, "
            f"dst={self.dst}/{self.dst_id}, "
            f"head={parser_render_hex(self.head)}, "
            f"body={parser_render_ascii(self.body)}, "
            f")"
        )

    @property
    def link(self) -> bytes:
        return self.part_list[PacketIndex.link]

    @link.setter
    def link(self, value:bytes) -> None:
        self.part_list[PacketIndex.link] = value

    @property
    def src(self) -> WiredBytes:
        return self.part_list[PacketIndex.src]

    @src.setter
    def src(self, value:WiredBytes) -> None:
        self.part_list[PacketIndex.src] = value

    @property
    def src_id(self) -> WiredBytes:
        return self.part_list[PacketIndex.src_id]

    @src_id.setter
    def src_id(self, value:WiredBytes) -> None:
        self.part_list[PacketIndex.src_id] = value

    @property
    def dst(self) -> WiredBytes:
        return self.part_list[PacketIndex.dst]

    @dst.setter
    def dst(self, value:WiredBytes) -> None:
        self.part_list[PacketIndex.dst] = value

    @property
    def dst_id(self) -> WiredBytes:
        return self.part_list[PacketIndex.dst_id]

    @dst_id.setter
    def dst_id(self, value:WiredBytes) -> None:
        self.part_list[PacketIndex.dst_id] = value

    @property
    def head(self) -> WiredBytes:
        return self.part_list[PacketIndex.head]

    @head.setter
    def head(self, value:WiredBytes) -> None:
        self.part_list[PacketIndex.head] = value

    @property
    def body(self) -> bytes:
        return self.part_list[PacketIndex.body]

    @body.setter
    def body(self, value:bytes) -> None:
        self.part_list[PacketIndex.body] = value

    @property
    def send_part_list(self) -> List[bytes]:
        return self.part_list[1:]  # drop link on send


class WireCodec:
    """
    wire message serialization
    """

    default_part_list = [WiredBytes.empty()] * WirePacket.part_size

    @staticmethod
    def produce_packet() -> WirePacket:
        return WirePacket(WireCodec.default_part_list.copy())

    @staticmethod
    def message_encode(missive:WireMissive) -> WirePacket:
        "serialize message into packet"
        route = missive.route
        packet = WireCodec.produce_packet()
        packet.src = route.src
        packet.src_id = route.src_id
        packet.dst = route.dst
        packet.dst_id = route.dst_id
        packet.head = missive.missive_type
        packet.body = missive.wired_into_pack()
        return packet

    @staticmethod
    def message_decode(packet:WirePacket) -> WireMissive:
        "deserialize packet into message"
        route = ActorRoute(
            src=WiredBytes(packet.src),
            src_id=WiredBytes(packet.src_id),
            dst=WiredBytes(packet.dst),
            dst_id=WiredBytes(packet.dst_id),
        )
        head = packet.head
        missive_class = WireStore.missive_class_map[head]  # lookup by type
        missive = missive_class.wired_from_pack(packet.body)  # deserialize body
        object.__setattr__(missive, 'route', route)  # bypass frozen
        return missive
