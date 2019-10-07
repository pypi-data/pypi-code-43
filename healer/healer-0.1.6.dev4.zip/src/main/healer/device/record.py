"""
Base type for persisted device record
"""

from __future__ import annotations

import enum
import logging
from dataclasses import dataclass
from dataclasses import field
from typing import Any
from typing import List
from typing import Mapping
from typing import Type

from healer.persist.session import PersistSession
from healer.persist.session import SessionIdentity
from healer.persist.session import SessionSupport
from healer.persist.session import SessionType
from healer.persist.support.base import StoredCodec
from healer.support.typing import AutoNameEnum
from healer.support.typing import override
from healer.support.wired.base import WiredDatum

logger = logging.getLogger(__name__)


@enum.unique
class RecordName(AutoNameEnum):
    "common record names"
    device_identity = enum.auto()
    session_summary = enum.auto()


@dataclass
class DeviceRecord(WiredDatum):
    """
    Base type for persisted device record
    """

    # permanent serialialization identity
    device_codec_guid = None  # must override

    @classmethod
    def __init_subclass__(cls, **kwargs):
        "register available derived records"
        super().__init_subclass__(**kwargs)
        RecordSupport.register_device_record(cls)


class RecordCodec(StoredCodec):
    "serializer for record sessions, uses string keys and record values"

    @override
    def encode(self, record_value:DeviceRecord) -> bytes:
        "uses record values"
        return RecordSupport.record_encode(record_value)

    @override
    def decode(self, stored_record:bytes) -> DeviceRecord:
        "uses record values"
        return RecordSupport.record_decode(stored_record)

    @override
    def encode_key(self, record_key:str) -> bytes:
        "uses string keys"
        return record_key.encode()

    @override
    def decode_key(self, stored_key:bytes) -> str:
        "uses string keys"
        return stored_key.decode()


class RecordSupport:
    """
    Record serialization functions
    """

    header_size = 2  # length of record header
    header_order = 'big'  # byte order of record header

    "track derived record types"
    device_record_map:Mapping[int, Type[DeviceRecord]] = dict()

    @staticmethod
    def register_device_record(record_class:Type[DeviceRecord]) -> None:
        "track derived record types"
        codec_guid = record_class.device_codec_guid
        assert codec_guid, f"no guid: {record_class}"
        assert isinstance(codec_guid, int), f"wrong guid: {codec_guid}"
        assert not codec_guid in RecordSupport.device_record_map, f"need unique: {record_class}"
        RecordSupport.device_record_map[codec_guid] = record_class

    @staticmethod
    def record_encode(record_value:DeviceRecord) -> bytes:
        "serialize device record into byte array"
        codec_guid = record_value.device_codec_guid
        assert codec_guid, f"no guid: {record_value}"
        assert isinstance(codec_guid, int), f"wrong guid: {codec_guid}"
        record_class = RecordSupport.device_record_map.get(codec_guid, None)
        assert record_class, f"no type: {record_value}"
        assert isinstance(record_value, record_class), f"wrong type: {record_value}"
        record_head = codec_guid.to_bytes(
            length=RecordSupport.header_size, byteorder=RecordSupport.header_order,
        )
        record_data = record_value.wired_into_pack()
        record_bytes = record_head + record_data
        return record_bytes

    @staticmethod
    def record_decode(record_bytes:bytes) -> DeviceRecord:
        "deserialize device record from byte array"
        record_head = record_bytes[0:RecordSupport.header_size]
        record_data = record_bytes[RecordSupport.header_size:]
        codec_guid = int.from_bytes(
            bytes=record_head, byteorder=RecordSupport.header_order,
        )
        record_class = RecordSupport.device_record_map.get(codec_guid, None)
        assert record_class, f"no guid: {codec_guid}"
        record_value = record_class.wired_from_pack(record_data)
        return record_value

    @staticmethod
    def produce_session(
            session_type:SessionType=None,
            session_identity:SessionIdentity=None,
        ) -> PersistSession:
        "session factory for device records"
        session_type = session_type or SessionType.tempdir
        session_identity = session_identity or SessionIdentity()
        return SessionSupport.produce_session(
            session_identity=session_identity, session_type=session_type, codec_class=RecordCodec,
        )


@dataclass
class DeviceIdentity(DeviceRecord):
    "persist unique device identity"

    device_codec_guid = 10

    device_identity:str = None
    device_description:str = None
