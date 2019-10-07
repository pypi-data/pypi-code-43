
from healer.device.record import *


@dataclass
class RecordId(DeviceRecord):
    """
    """
    device_codec_guid = 1919
    id:int


@dataclass
class RecordKey(DeviceRecord):
    """
    """
    device_codec_guid = 2929
    key:str


@dataclass
class DummyRecord(DeviceRecord):

    device_codec_guid = 33333

    name:str = "dummy"
    value:float = 3.0


def test_record_codec():
    print()

    source = DummyRecord()
    print(f"source: {source}")

    binary = RecordSupport.record_encode(source)
    print(f"binary: {binary}")

    target = RecordSupport.record_decode(binary)
    print(f"target: {target}")

    assert source == target


def test_record_session():
    print()

    session = RecordSupport.produce_session()

    session.context_put("summary", RecordId("hello-kitty"))

    session.message_put("index-1", RecordId("hello-kitty-1"))
    session.message_put("index-2", RecordId("hello-kitty-2"))

    for key, value in session.context_dict.items():
        print(f"key={key} value={value}")

    for key, value in session.message_dict.items():
        print(f"key={key} value={value}")

    session.close()
