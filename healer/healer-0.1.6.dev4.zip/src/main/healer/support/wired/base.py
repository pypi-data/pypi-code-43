"""
Object serialization support
"""

from __future__ import annotations

import dataclasses
import importlib
import inspect
import types
from dataclasses import dataclass
from typing import Any
from typing import List
from typing import Mapping
from typing import Type
from typing import Union

import msgpack
import yaml

from .builder import WiredBuilder


class Wired:

    @staticmethod
    def transient(class_field:dataclasses.Field) -> dataclasses.Field:
        assert isinstance(class_field, dataclasses.Field), f"need data field: {class_field}"
        return class_field


@dataclass
class WiredConfig:
    "serializer behaviour adjust"

    use_bytes:bool  # use bare bytes vs store bytes.hex() as serialized representation


@dataclass
class WiredDict():
    "trait: serializer for dictionary representation"

    # data class field serializer list
    wired_codec_chain = None

    # serializer behaviour adjust
    wired_build_config = WiredConfig(
        use_bytes=False,
    )

    @classmethod
    def wired_chain(cls) -> List['WiredCodec']:
        "produce serializer list on demand"
        if not cls.wired_codec_chain:
            builder = WiredBuilder(cls)
            cls.wired_codec_chain = builder.make_chain()
        return cls.wired_codec_chain

    @classmethod
    def wired_from_dict(cls, wire_dict:Mapping[str, Any]) -> 'WiredDict':
        "convert dictionary into instance"
        instance = object.__new__(cls)
        for codec in cls.wired_chain():
            wire_entry = wire_dict.get(codec.field_name, None)
            if wire_entry is not None:
                codec.entry_wire_set(instance, wire_entry)
        return instance

    def wired_into_dict(self) -> Mapping[str, Any]:
        "convert instance into dictionary"
        wire_dict = dict()
        for codec in self.wired_chain():
            wire_entry = codec.entry_wire_get(self)
            if wire_entry is not None:
                wire_dict[codec.field_name] = wire_entry
        return wire_dict


@dataclass
class WiredPack(WiredDict):
    "trait: serializer for msgpack representation"

    wired_build_config = WiredConfig(
        use_bytes=True,
    )

    @classmethod
    def wired_from_pack(cls, wire_bytes:bytes) -> 'WiredPack':
        "convert msgpack byte array into instance"
        return cls.wired_from_dict(msgpack.unpackb(packed=wire_bytes, raw=False))

    def wired_into_pack(self) -> bytes:
        "convert instance into msgpack byte array"
        return msgpack.packb(o=self.wired_into_dict(), use_bin_type=True)


@dataclass
class WiredYaml(WiredDict):
    "trait: serializer for yaml representation"

    wired_build_config = WiredConfig(
        use_bytes=False,
    )

    @classmethod
    def wired_from_yaml(cls, yaml_text:str) -> 'WiredYaml':
        "convert yaml text into instance"
        return cls.wired_from_dict(yaml.safe_load(yaml_text))

    def wired_into_yaml(self) -> str:
        "convert instance into yaml text"
        return yaml.dump(self.wired_into_dict())


@dataclass
class WiredDatum(WiredYaml, WiredPack, WiredDict):
    "trait: serializer for multiple representations"

    wired_build_config = WiredConfig(
        use_bytes=True,
    )


class WiredApply:
    """
    make data class serializable on demand
    """

    @staticmethod
    def copy_func(func:types.FunctionType):
        return types.FunctionType(
            func.__code__,
            func.__globals__,
            func.__name__,
            func.__defaults__,
            func.__closure__,
        )

    @staticmethod
    def resolve_type(data_type:Type, type_name:Union[str, Type]) -> Type:
        if isinstance(type_name, type):
            return type_name
        else:
            module = importlib.import_module(data_type.__module__)
            globals_dict = dict(inspect.getmembers(module))
            type_class = eval(type_name, globals_dict)
            return type_class

    @staticmethod
    def process_class(data_type:Type) -> None:
        "make data class serializable on demand"

        if hasattr(data_type, 'wired_codec_chain'):
            return

        assert(inspect.isclass(data_type)), f"need data class: {data_type}"
        assert dataclasses.is_dataclass(data_type), f"need data class: {data_type}"

        for name, member in inspect.getmembers(WiredDatum):
            if name.startswith('_'):
                continue
            if inspect.ismethod(member):  # class method
                method = WiredApply.copy_func(member)
                method = classmethod(method)
                method.__self__ = data_type
                setattr(data_type, name, method)
            elif inspect.isfunction(member):  # instance/static method
                setattr(data_type, name, member)
            else:  # attribute, etc
                setattr(data_type, name, member)

        for field in data_type.__dataclass_fields__.values():
            type_name = field.type
            field_type = WiredApply.resolve_type(data_type, type_name)
            if dataclasses.is_dataclass(field_type):
                WiredApply.process_class(field_type)
