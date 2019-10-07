"""
"""

from __future__ import annotations

from typing import List

from healer.support.wired.base import *
from healer.support.wired.typing import WiredBytes
from healer.cluster.talk import NodeInfo
from healer.support.network import NetworkSupport
from dataclasses import field
from healer.support.hronos import DateTime

#
#
#


@dataclass
class TreeItem(WiredDict):
    value:str = None
    stamp:DateTime = field(default_factory=DateTime.now)


@dataclass
class TreeBase(WiredPack, WiredYaml):
    guid:WiredBytes = None
    base_item:TreeItem = None


@dataclass
class TreeCore(TreeBase):
    link:bytes = None
    total:float = 0
    comment:str = None
    core_item:TreeItem = None


def test_wired_props():
    print()

    instance = TreeCore()

    print(f"TreeCore: {TreeCore}")
    print(f"instance: {instance}")
    print(f"dir: {dir(TreeCore)}")
    print(f"__dataclass_params__: {TreeCore.__dataclass_params__}")

    print(f"--- field ---")
    for key, value in TreeCore.__dataclass_fields__.items():
        print(f"{key} : {value}")

    print(f"--- __dict__ ---")
    for key, value in TreeCore.__dict__.items():
        print(f"{key} : {value}")


def test_codec_inherit():
    print()

    instance = TreeCore(
        guid=WiredBytes(b'1234'),
        link=b'5678',
        total=3.0,
        comment='comment/comment',
        base_item=TreeItem(value='abc'),
        core_item=TreeItem(value='def'),
    )
    print(f"instance: {instance}")
    print(f"build_config: {TreeCore.wired_build_config}")

    data = instance.wired_into_dict()
    print(len(str(data)))
    print(data)

    data = instance.wired_into_pack()
    print(len(data))
    print(data)

    data = instance.wired_into_yaml()
    print(len(data))
    print(data)

    node_info = NodeInfo(
        guid=WiredBytes.generate(),
        addr=NetworkSupport.private_address(),
        port=20000,
    )

    data = node_info.wired_into_pack()
    print(len(data))
    print(data)

#
#
#


@dataclass
class DataItem():
    value:str
    suffix:str = None
    stamp:DateTime = None


@dataclass
class DataBase():
    guid:WiredBytes = None
    base_item:DataItem = None


@dataclass
class DataCore(DataBase):
    link:bytes = None
    total:float = 0
    comment:str = None
    core_item:DataItem = None
    some_list:List[str] = None
    more_list:List[DataItem] = None


def test_codec_apply():
    print()

    WiredApply.process_class(DataCore)

    instance_list = [
        DataItem('hello'),
        DataItem('hello', 'kitty'),
        DataItem('hello', 'kitty',
            stamp=DateTime(2018, 10, 11, 12, 13, 14, 123456),
        ),
        DataCore(
            guid=WiredBytes(b'1234'),
            link=b'5678',
            total=3.0,
            comment='comment/comment',
            base_item=DataItem(value='abc'),
            core_item=DataItem(value='def'),
            some_list=['aaa', 'bbb', 'ccc'],
            more_list=[DataItem('hello-1'), DataItem('hello-2'), DataItem('hello-3'), ],
        ),
    ]

    for instance in instance_list:
        verify_dict(instance)
        verify_pack(instance)
        verify_yaml(instance)


def verify_dict(source):
    print(f"source: {source}")
    binary = source.wired_into_dict()
    print(f"size: {len(str(binary))}")
    print(f"binary: {binary}")
    target = type(source).wired_from_dict(binary)
    print(f"target: {target}")
    assert source == target


def verify_pack(source):
    print(f"source: {source}")
    binary = source.wired_into_pack()
    print(f"size: {len(binary)}")
    print(f"binary: {binary}")
    target = type(source).wired_from_pack(binary)
    print(f"target: {target}")
    assert source == target


def verify_yaml(source):
    print(f"source: {source}")
    binary = source.wired_into_yaml()
    print(f"size: {len(binary)}")
    print(f"binary: {binary}")
    target = type(source).wired_from_yaml(binary)
    print(f"target: {target}")
    assert source == target


def test_codec_transient():
    print()

    @dataclass
    class DataTest(TreeBase):
        skip:str = field(default='hello-kitty', metadata={'transient':True})

    print(f"data: {dataclasses.fields(DataTest)}")
    data_test = DataTest()

    verify_pack(data_test)
