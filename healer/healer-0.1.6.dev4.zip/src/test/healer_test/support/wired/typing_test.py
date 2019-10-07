
import uuid
from healer.support.wired.typing import *
from dataclasses import dataclass
from healer.support.wired.base import WiredApply

frozen = dataclass(frozen=True)


@frozen
class SomeItem:
    value:int


@frozen
class SomeBase:
    name:str


@frozen
class SomeNode(SomeBase):
    guid:WiredBytes
    item:SomeItem


def test_wired_guid():
    print()

    WiredApply.process_class(SomeNode)

#     for entry in dir(SomeNode):
#         print(f"EEE {entry}")

    guid = WiredBytes.generate()
    item = SomeItem(123)

    source = SomeNode('abc', guid, item)
    print(f"source: {source}")

    binary = source.wired_into_pack()
    print(f"binary: {binary}")

    target = SomeNode.wired_from_pack(binary)
    print(f"target: {target}")

    assert source == target


def test_wired_from_int():
    print()

    print(f"empty: {WiredBytes.empty()}")

    instance = WiredBytes.generate()
    copy_one = instance.copy()
    copy_two = instance.copy()
    print(f"copy: {id(instance)}")
    print(f"copy: {id(copy_one)}")
    print(f"copy: {id(copy_two)}")
    assert id(instance) != id(copy_one)
    assert id(instance) != id(copy_two)
    assert id(copy_one) != id(copy_two)

    source = 1234123412341234123412341234123412341234123412341234123412341234
    print(f"source: {source}")

    binary = WiredBytes.from_int(source)
    print(f"binary: {binary}")

    target = binary.to_int()
    print(f"target: {target}")

    assert source == target
