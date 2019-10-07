import time

from dataclasses import dataclass
from typing import List
from datetime import datetime

import msgpack

from mashumaro import DataClassMessagePackMixin
from mashumaro.serializer.yaml import DataClassYAMLMixin


def main_to_msgpack():

    @dataclass
    class DataClass(DataClassMessagePackMixin):
        x: List[int]

    dumped = msgpack.packb({'x': [1, 2, 3]})
    print(f"DataClass([1, 2, 3]).to_msgpack() {DataClass([1, 2, 3]).to_msgpack()}")
    assert DataClass([1, 2, 3]).to_msgpack() == dumped


def main_from_msgpack():

    @dataclass
    class DataClass(DataClassMessagePackMixin):
        x: List[int]

    dumped = msgpack.packb({'x': [1, 2, 3]})
    assert DataClass.from_msgpack(dumped) == DataClass([1, 2, 3])


def main_to_msg_pack_datetime():

    @dataclass
    class DataClass(DataClassMessagePackMixin):
        x: datetime

    dt = datetime(2018, 10, 29, 12, 46, 55, 308495)
    dumped = msgpack.packb({'x': dt.isoformat()})
    print(f"DataClass(dt).to_msgpack() {DataClass(dt).to_msgpack()}")
    assert DataClass(dt).to_msgpack() == dumped


main_to_msgpack()
main_from_msgpack()
main_to_msg_pack_datetime()


@dataclass(frozen=True)
class NoSqlRecord(DataClassMessagePackMixin, DataClassYAMLMixin):
    value:str


@dataclass(frozen=True)
class Message(DataClassMessagePackMixin, DataClassYAMLMixin):
    some = '123'
    header:str
    stamped:datetime
    value_list:List[NoSqlRecord]


source = Message("hello-kitty", datetime.now(), [NoSqlRecord('hello'), NoSqlRecord('kitty')])
print(f"source: {source}")
binary = source.to_msgpack()
print(f"binary: {binary}")
target = Message.from_msgpack(binary)
print(f"target: {target}")
assert source == target

print(f"---")
print(f"some: {source.some}")
print(f"yaml: {source.to_yaml()}")
print(f"---")

count = 10000

start_time = time.time()

for index in range(count):
    binary = source.to_msgpack()
    target = Message.from_msgpack(binary)

finish_time = time.time()

diff_time = finish_time - start_time
unit_time = diff_time / count
print(f"unit_time, us: {unit_time * 1000000}")
