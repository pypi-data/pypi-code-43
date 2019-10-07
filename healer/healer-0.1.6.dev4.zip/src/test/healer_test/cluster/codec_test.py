
from healer.cluster.codec import *
from healer.cluster.talk import *
from healer.support.network import NetworkSupport


def test_wire_codec():
    print()

    node_info = NodeInfo(
        guid=WiredBytes.generate(),
        addr=NetworkSupport.private_address(),
        port=20202,
    )

    message_list = [
        WireTalk.LinkUp(node_info=node_info),
        WireTalk.LinkDown(node_info=node_info),
    ]

    for source in message_list:
        print()
        print(f"--- {type(source)} ---")
        print(f"source: {source}")
        packet = WireCodec.message_encode(source)
        print(f"packet: {packet}")
        target = WireCodec.message_decode(packet)
        print(f"target: {target}")
        assert source == target
