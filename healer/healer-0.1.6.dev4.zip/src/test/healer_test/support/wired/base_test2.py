
from __future__ import annotations

from healer.support.wired.base import *

import dataclasses
from dataclasses import dataclass

from healer.support.wired.typing import WiredBytes
from healer.support.network import NetworkSupport

frozen = dataclass(frozen=True)  # message part


@frozen
class NodeBase(WiredDatum):
    """
    """
    guid:WiredBytes
    addr:str
    port:int


def test_codec_inherit():
    print()

    print(dataclasses.fields(NodeBase))

    node_info = NodeBase(
        guid=WiredBytes.generate(),
        addr=NetworkSupport.private_address(),
        port=20000,
    )
    print(node_info)

#
    data = node_info.wired_into_pack()
    print(len(data))
    print(data)
