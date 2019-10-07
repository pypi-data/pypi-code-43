"""
Object serialization support
"""

from __future__ import annotations

import dataclasses
import functools
import importlib
import inspect
import typing
from contextlib import suppress
from dataclasses import Field
from dataclasses import dataclass
from datetime import timezone
from typing import Any
from typing import Iterable
from typing import List
from typing import Mapping
from typing import Type
from typing import Union

from healer.support.hronos import DateTime
from healer.support.wired.typing import WiredBytes


class WiredBuilder:
    "codec chain builder"

    wired_type:Type  # target data class
    wired_config:'WiredConfig'

    def __init__(self, wired_type:Type):
        self.wired_type = wired_type
        self.wired_config = wired_type.wired_build_config

    def field_list(self) -> List[Field]:
        return self.wired_type.__dataclass_fields__.values()

    def make_chain(self) -> List['WiredCodec']:
        "produce codecs for every data class field"
        codec_chain = []
        module = importlib.import_module(self.wired_type.__module__)
        globals_dict = dict(inspect.getmembers(module))
        for field in self.field_list():
            if WiredProvider.has_field_transient(field):
                continue  # exclude transient fields
            field_name = field.name
            field_type = field.type  # can be type or type name
            if isinstance(field_type, str):
                # resolve type from type name
                field_type = eval(field.type , globals_dict)
            codec_class = WiredProvider.find_codec_class(field_type)
            codec_entry = codec_class(field_name, field_type, self.wired_config)
            codec_chain.append(codec_entry)
        return codec_chain


class WiredRegistry:
    "register all codec classes"

    codec_class_list:List['WiredCodec'] = list()

    @staticmethod
    def register_codec_class(codec_class:Type) -> None:
        assert not codec_class in WiredRegistry.codec_class_list, f"need unique: {codec_class}"
        WiredRegistry.codec_class_list.append(codec_class)


@dataclass
class WiredCodec:
    "base type for dataclass field serializer"

    typer = None  # codec category by generic field type

    field_name:str = None  # dataclass field name
    field_type:Type = None  # exact declared field type
    config:WiredConfig = None  # serializer behaviour adjust

    @classmethod
    def __init_subclass__(cls, **kwargs):
        "register all codec classes"
        super().__init_subclass__(**kwargs)
        WiredRegistry.register_codec_class(cls)

    def wire_from_data(self, data:Any) -> Any:
        "convert field value into byte array"
        wire = data
        return wire

    def data_from_wire(self, wire:Any) -> Any:
        "convert byte array into field value"
        data = wire
        return data

    def entry_wire_get(self, instance:Any) -> Any:  # wire
        "extract field value as serialized byte array"
        data = object.__getattribute__(instance, self.field_name)  # bypass frozen
        if data is not None:
            wire = self.wire_from_data(data)
            return wire

    def entry_wire_set(self, instance:Any, wire:Any) -> None:
        "inject field value from serialized byte array"
        if wire is not None:
            data = self.data_from_wire(wire)
            object.__setattr__(instance, self.field_name, data)


class WithBytesCodec:
    "behaviour adjust: control byte array representation"

    def wire_from_bytes(self, entry:bytes) -> Union[str, bytes]:
        if self.config.use_bytes:
            return entry
        else:
            return entry.hex()  # if entry else None

    def bytes_from_wire(self, entry:Union[str, bytes]) -> bytes:
        if self.config.use_bytes:
            return entry
        else:
            return bytes.fromhex(entry)  # if entry else None


class WithTypeParamCodec:
    "serializer for generic type with one parameter"

    def origin_type(self) -> Type:
        "generic container type: list, map, etc"
        return self.field_type.__origin__

    def origin_instance(self) -> object:
        "produce generic container instance"
        return  self.origin_type().__new__(self.origin_type())

    def __post_init__(self):
        "setup container entry codec: serializer for the contained elements"
        type_args = self.field_type.__args__
        assert len(type_args) == 1, f"need solo args: {type_args}"
        param_field_name = 'param'
        param_field_type = type_args[0]
        codec_class = WiredProvider.find_codec_class(param_field_type)
        self.entry_codec = codec_class(param_field_name, param_field_type, self.config)


class WiredFormat:
    "codecs for the supported serializtion formats"

    @dataclass
    class CodecWiredBytes(WiredCodec, WithBytesCodec):
        typer = WiredBytes

        def wire_from_data(self, data:WiredBytes) -> bytes:
            data = bytes(data)  # if data else None
            wire = self.wire_from_bytes(data)
            return wire

        def data_from_wire(self, wire:bytes) -> WiredBytes:
            data = self.bytes_from_wire(wire)
            data = WiredBytes(data)  # if data else None
            return data

    @dataclass
    class CodecInt(WiredCodec):
        typer = int

    @dataclass
    class CodecStr(WiredCodec):
        typer = str

    @dataclass
    class CodecFloat(WiredCodec):
        typer = float

    @dataclass
    class CodecDateTime(WiredCodec):
        "use utc unix time stamp as wired representation"
        typer = DateTime

        def wire_from_data(self, data:DateTime) -> float:
            return data.astimezone(tz=timezone.utc).timestamp()

        def data_from_wire(self, wire:float) -> DateTime:
            return DateTime.utcfromtimestamp(wire).replace(tzinfo=timezone.utc)

    @dataclass
    class CodecBytes(WiredCodec, WithBytesCodec):
        typer = bytes

        def wire_from_data(self, data:bytes) -> Union[str, bytes]:
            wire = self.wire_from_bytes(data)
            return wire

        def data_from_wire(self, wire:Union[str, bytes]) -> bytes:
            data = self.bytes_from_wire(wire)
            return data

    @dataclass
    class CodecIterable(WiredCodec, WithTypeParamCodec):
        typer = Iterable

        def wire_from_data(self, data_list:Iterable) -> Iterable:
            if not data_list: return None
            wire_list = self.origin_instance()
            for data in data_list:
                wire = self.entry_codec.wire_from_data(data)
                wire_list.append(wire)
            return wire_list

        def data_from_wire(self, wire_list:Iterable) -> Iterable:
            if not wire_list: return None
            data_list = self.origin_instance()
            for wire in wire_list:
                data = self.entry_codec.data_from_wire(wire)
                data_list.append(data)
            return data_list

    @dataclass
    class CodecDataClass(WiredCodec):
        typer = None  # no auto mapping

        def wire_from_data(self, data:object) -> dict:
            return data.wired_into_dict()  # if data else None

        def data_from_wire(self, wire:dict) -> object:
            return self.field_type.wired_from_dict(wire)  # if wire else None


class WiredProvider:
    "produce field codec for a field type"

    @staticmethod
    @functools.lru_cache(maxsize=1)
    def codec_mapper() -> Mapping[Type, WiredCodec]:
        "resolve field codec from field type"
        codec_class_list = WiredRegistry.codec_class_list
        codec_mapping = map(lambda class_type: (class_type.typer, class_type), codec_class_list)
        return dict(codec_mapping)

    @staticmethod
    def find_codec_class(typer:Type) -> WiredCodec:
        "resolve field codec from field type"
        has_type = isinstance(typer, (type, typing._GenericAlias))
        assert(has_type), f"need type: {typer}"
        codec_mapper = WiredProvider.codec_mapper()
        # auto mapping
        for codec_class in codec_mapper.values():
            if codec_class.typer :
                # scalar type check
                with suppress(TypeError):
                    if issubclass(typer, codec_class.typer):
                        return codec_class
                # generic type check
                with suppress(AttributeError):
                    if issubclass(typer.__origin__, codec_class.typer.__origin__):
                        return codec_class
        # explicit mapping
        if dataclasses.is_dataclass(typer):
            return WiredFormat.CodecDataClass
        # undefined mapping
        raise RuntimeError(f"unknown type: {typer}")

    @staticmethod
    def has_field_transient(field:Field) -> bool:
        "exclude transient field from serizlization"
        return field.metadata.get('transient', False)
