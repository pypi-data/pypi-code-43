"""
Message formats
"""

from __future__ import annotations

import functools
import itertools
from dataclasses import dataclass
from dataclasses import field
from typing import Any
from typing import List
from typing import Mapping
from typing import Optional
from typing import Type

from healer.persist.session import SessionIdentity
from healer.persist.session import SessionType
from healer.persist.support.schemaless import NoSqlEvent
from healer.support.actor.proper import ProperRef
from healer.support.wired.base import WiredDatum
from healer.support.wired.typing import WiredBytes

frozen = dataclass(frozen=True)  # message part
missive = dataclass(frozen=True)  # full message


@dataclass
class NodeInfo(WiredDatum):
    "cluster node descriptor"
    guid:WiredBytes
    addr:str
    port:int


@frozen
class WithNodeInfo:
    "message with node info"
    node_info:NodeInfo = None


@missive
class AnyMissive:
    "cluster message base"


@frozen
class WithConfigContext:
    "cluster actor report"
    bus_actor:ProperRef
    wire_actor:ProperRef
    hood_actor:ProperRef
    data_actor:ProperRef
    files_actor:ProperRef


@missive
class ConfigMissive(AnyMissive):
    "cluster config discovery"


class ConfigTalk:
    "cluster config discovery"

    Any = ConfigMissive

    @missive
    class ContextQuery(ConfigMissive): ""

    @missive
    class ContextReply(WithConfigContext, ConfigMissive): ""

#
#
#


@missive
class DeviceMissive(AnyMissive):
    "device actor message"


@frozen
class WithSession:
    "message with session information"
    session_type:SessionType
    session_identity:SessionIdentity


class DeviceTalk:
    "device actor message"

    Any = DeviceMissive

    @missive
    class SessionCreate(WithSession, DeviceMissive):
        "announce device record session creation"

    @missive
    class SessionDelete(WithSession, DeviceMissive):
        "announce device record session deletion"

#
#
#


@missive
class BusMissive(AnyMissive):
    "event bus message"


class BusTalk:
    "cluster actor group messaging"

    Any = BusMissive

    @missive
    class Publish(BusMissive):
        "publish message to the topic"
        topic:str
        message:Any

    @missive
    class Subscribe(BusMissive):
        "subscribe actor into the topic"
        topic:str
        actor:ProperRef

    @missive
    class Unsubscribe(BusMissive):
        "unsubscribe actor from the topic"
        topic:str
        actor:ProperRef


@missive
class HoodMissive(AnyMissive): "neighborhood message"


@missive
class HoodNodeMissive(WithNodeInfo, HoodMissive): "neighborhood with node info"


class HoodTalk:
    "cluster neighborhood discovery"

    Any = HoodMissive

    @missive
    class SelfNodeQuery(HoodMissive): "query own node info"

    @missive
    class SelfNodeReply(HoodNodeMissive): "report own node info"

    @missive
    class IssueEnable(HoodNodeMissive): "command: show node"

    @missive
    class IssueDisable(HoodNodeMissive): "command: hide node"

    @missive
    class NodeDetected(HoodNodeMissive): "event: node present"

    @missive
    class NodeUndetected(HoodNodeMissive): "event: node missing"

    @missive
    class LinkConnected(HoodNodeMissive): "event: node link up"

    @missive
    class LinkDisconnected(HoodNodeMissive): "event: node link down"

#
# wire protocol
#


WireMissiveGroup = itertools.count(1, 64)
WireMissiveCount = itertools.count()

#
#
#


@frozen
class WithMissiveType:
    missive_type = None


@frozen
class ActorRoute(WiredDatum):
    "node-to-node message route"
    src:WiredBytes = WiredBytes.empty()  # source node guid
    src_id:WiredBytes = WiredBytes.empty()  # source actor id
    dst:WiredBytes = WiredBytes.empty()  # target node guid
    dst_id:WiredBytes = WiredBytes.empty()  # target actor id

    @staticmethod
    def empty() -> 'ActorRoute':
        return WireStore.actor_route_empty


class WireStore:

    actor_route_empty = ActorRoute()

    missive_class_map = dict()

    @staticmethod
    def register_missive_type(cls:Type) -> None:
        assert not cls.missive_type in WireStore.missive_class_map
        WireStore.missive_class_map[cls.missive_type] = cls


@frozen
class WithActorRoute:
    route:ActorRoute = field(default=ActorRoute.empty(), metadata={'transient':True})


@missive
class WireMissive(WithMissiveType, WithActorRoute, WiredDatum, AnyMissive):

    @classmethod
    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        cls.missive_type = next(WireMissiveCount).to_bytes(2, 'big')
        WireStore.register_missive_type(cls)


WireMissiveCount = itertools.count(next(WireMissiveGroup))


class WireTalk:

    @missive
    class LinkUp(WithNodeInfo, WireMissive):
        pass

    @missive
    class LinkDown(WithNodeInfo, WireMissive):
        pass

#
# data store
#


@frozen
class WithStoreName:
    store:str = None


@frozen
class ColumnState(WiredDatum):
    col_id:str = None
    time_start:float = None
    time_finish:float = None


@frozen
class WithStoreState(WithStoreName):
    state_list:List[ColumnState] = None


@frozen
class WithColumntState(WithStoreName):
    state:ColumnState = None


@missive
class DataMissive(WireMissive):
    pass


WireMissiveCount = itertools.count(next(WireMissiveGroup))


class DataTalk:

    Any = DataMissive

    @missive
    class StoreQuery(WithStoreName, DataMissive): ""

    @missive
    class StoreReply(WithStoreState, DataMissive): ""

    @missive
    class RecordQuery(WithColumntState, DataMissive): ""

    @missive
    class RecordReply(WithColumntState, DataMissive): ""

    @missive
    class RecordEvent(NoSqlEvent, DataMissive): ""

    @staticmethod
    def produce_record(event:NoSqlEvent):
        return DataTalk.RecordEvent(
            store=event.store,
            action=event.action,
            row_id=event.row_id,
            col_id=event.col_id,
            bundle=event.bundle,
            stamp=event.stamp,
            token=event.token,
        )

#
# file store
#


@frozen
class WithFilePath:
    path:str = None  # relative path in store
    time:int = None  # modification time, seconds
    size:int = None  # system reported file size


@frozen
class WithFileChunk:
    path:str = None  # relative path in store
    beg:int = None  # offset: begin
    end:int = None  # offset: endin


@missive
class FileMissive(WireMissive):
    pass


WireMissiveCount = itertools.count(next(WireMissiveGroup))


class FileTalk:

    Any = FileMissive

    @missive
    class StateQuery(FileMissive): ""

    @missive
    class StateReply(FileMissive): ""

    @missive
    class ListQuery(FileMissive): ""

    @missive
    class ListReply(WithFilePath, FileMissive): ""

    @missive
    class ChunkQuery(WithFileChunk, FileMissive): ""

    @missive
    class ChunkReply(WithFileChunk, FileMissive):
        content:bytes = None

    @missive
    class EventCreate(WithFilePath, FileMissive): ""

    @missive
    class EventDelete(WithFilePath, FileMissive): ""

#
# user gui
#


@missive
class StationMissive(AnyMissive): ""


class StationTalk:

    Any = StationMissive
