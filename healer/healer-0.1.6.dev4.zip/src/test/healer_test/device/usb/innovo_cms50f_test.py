import sys
import usb.core
import usb.util

from healer.device.usb.innovo_cms50f import *
from healer_test.device.invoker import invoker_innovo_cmd50f


def test_packet():
    print()

    packet = ControlPacketCMS.issue_stream_start()
    print(packet)

    packet = ControlPacketCMS.issue_stream_abort()
    print(packet)

    packet = ControlPacketCMS.issue_stored_start(user=1, segment=10)
    print(packet)

    packet = ControlPacketCMS.issue_stored_abort()
    print(packet)


def test_merge():
    print()
    packet1 = ControlPacketCMS.issue_stream_start()
    packet2 = ControlPacketCMS.issue_stream_abort()
    packet3 = BufferSupportCMS.packet_merge(packet1, packet2)
    print(packet3)


def test_device():
    print()
    invoker_innovo_cmd50f(verify_device_packet)
    invoker_innovo_cmd50f(verify_device_command)
    invoker_innovo_cmd50f(verify_device_identity)
    invoker_innovo_cmd50f(verify_stored_packets)


def verify_device_packet(device:DeviceInnovoCMS50F):

    device.packet_write(ControlPacketCMS.issue_device_ping())
    device.packet_write(ControlPacketCMS.issue_device_ping())
    device.packet_write(ControlPacketCMS.issue_device_ping())

    device.packet_write(ControlPacketCMS.issue_stream_abort())
    print(device.packet_read())

    device.packet_write(ControlPacketCMS.issue_stored_abort())
    print(device.packet_read())

    device.packet_write(ControlPacketCMS.query_device_id())
    print(device.packet_read())

    device.packet_write(ControlPacketCMS.query_device_notice())
    print(device.packet_read())

    device.packet_write(ControlPacketCMS.query_user_count())
    print(device.packet_read())

    device.packet_write(ControlPacketCMS.query_user_comment(user=0))
    print(device.packet_read())

    device.packet_write(ControlPacketCMS.query_segment_count(user=0))
    print(device.packet_read())

    device.packet_write(ControlPacketCMS.query_segment_meta(user=0, segment=0))
    print(device.packet_read())

    device.packet_write(ControlPacketCMS.query_segment_size(user=0, segment=0))
    print(device.packet_read())

    device.packet_write(ControlPacketCMS.query_segment_stamp(user=0, segment=0))
    print(device.packet_read())
    print(device.packet_read())

    device.packet_write(ControlPacketCMS.query_device_model())
    print(device.packet_read())
    print(device.packet_read())

    device.packet_write(ControlPacketCMS.query_device_brand())
    print(device.packet_read())


def verify_device_command(device:DeviceInnovoCMS50F):

    print(device.issue_stream_abort())
    print(device.issue_stored_abort())

    print(device.issue_device_ping())

    print(f"device_id: {device.query_device_id()}")
    print(f"device_notice: {device.query_device_notice()}")
    print(f"device_brand: {device.query_device_brand()}")
    print(f"device_model: {device.query_device_model()}")
    print(f"user_count: {device.query_user_count()}")

    for user in range(device.query_user_count()):
        print(f"user_comment: {device.query_user_comment(user=user)}")
        for segment in range(device.query_segment_count(user=user)):
            print(f"stored_size: {device.query_segment_size(user=user, segment=segment)}")
            print(f"stored_stamp: {device.query_segment_stamp(user=user, segment=segment)}")

    print(device.write_device_clock(DateTime.now()))


def verify_device_identity(device:DeviceInnovoCMS50F):
#     device.issue_device_id('user0')

    identity_past = device.query_device_id()
    print(f"identity_past: {identity_past}")

    identity_test = 'user123'
    assert identity_test != identity_past

    device.issue_device_id(identity_test)
    identity_next = device.query_device_id()
    print(f"identity_next: {identity_next}")

    device.issue_device_id(identity_past)
    assert identity_test == identity_next


def verify_stored_packets(device:DeviceInnovoCMS50F):

    # FIXME
    "this test may leave broken device segment and interfere with other tests"

    record_count = device.query_segment_size(user=0, segment=0)
    print(f"record_count: {record_count}")

    packet_count = int(record_count / RegularPacketCMS.PacketStoredBucket.data_size)
    print(f"packet_count: {packet_count}")

    device.packet_write(ControlPacketCMS.issue_stored_start(user=0, segment=0))

    sequence = 1
    bucket_count = 0

    tester_count = min(10, packet_count)

    try :
        for _ in range(tester_count):
            packet = device.packet_read()
            data_list = packet.data_list(sequence)
            sequence += packet.data_size
            print(f"data_list: {data_list}")
            if packet.packet_type == PacketTypeCMS.stored_bucket:
                bucket_count += 1
            elif packet.packet_type == PacketTypeCMS.device_ready:
                break
            else:
                raise RuntimeError(f"wrong packet: {packet}")
    except Exception as error:
        print(error)

    device.issue_stored_abort()

    print(f"bucket_count={bucket_count}")

    assert bucket_count == tester_count
