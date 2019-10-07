
import time
import uuid

from healer.cluster.talk import *
from healer.support.network import NetworkSupport
from healer.support.actor.proper import ProperActor
from healer.support.typing import TypingSupport


def xxx_actor_ref():
    print()

    actor_ref = ProperActor.start()

    print(f"actor_ref: {actor_ref}")

    source = HoodTalk.ConsumerSubscribe(actor_ref)
    print(f"source: {source}")

    binary = source.to_msgpack()
    print(f"binary: {binary}")

    target = HoodTalk.ConsumerSubscribe.from_msgpack(binary)
    print(f"target: {target}")

    assert source == target

    actor_ref.stop()


def test_data_talk():
    print()

    token = WiredBytes.generate()
    stamp = time.time()

    data_event = NoSqlEvent(
        store='store',
        action='create',
        row_id='hello',
        col_id='world',
        bundle='{"a":1}',
        stamp=stamp,
        token=token.copy(),
    )

    data_record = DataTalk.produce_record(data_event)
    print(data_record)
    print(data_record.wired_into_pack())


def xtest_hood_talk():
    print("test_hood_talk")

    print(WireTalk.LinkUp.__qualname__)

    node_info = NodeInfo(
        guid=WiredBytes.generate(),
        addr=NetworkSupport.private_address(),
        port=20000,
    )

    print(node_info)
    print(node_info.wired_into_pack())
