
from healer.support.wired.builder import *


def test_time_zone():
    print()

    codec = WiredFormat.CodecDateTime()

    source = DateTime.now()
    print(f"source: {source}")

    binary = codec.wire_from_data(source)
    print(f"binary: {binary}")

    target = codec.data_from_wire(binary)
    print(f"target: {target}")

    assert source == target
