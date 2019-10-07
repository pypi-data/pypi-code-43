import sys
import usb.core
import usb.util

from healer.device.usb.ionhealth_ih02 import *
from healer_test.device.invoker import invoker_ionhealth_ih02


def test_packet_format():
    print()
    date_time = DateTime(
        year=2019,
        month=7,
        day=10,
        hour=17,
        minute=30,
    )

    packet = PacketSupportIH02.produce_device_info()
    print(packet)

    packet = PacketSupportIH02.produce_storage_info()
    print(packet)

    packet = PacketSupportIH02.produce_date_time()
    packet.date_time = date_time
    print(packet)

    packet = PacketSupportIH02.produce_record_date_time()
    packet.date_time = date_time
    print(packet)

    packet = PacketSupportIH02.produce_record_measurement()
    print(packet)


def test_packet_date_time():
    print()
    date_time = DateTime(
        year=2019,
        month=7,
        day=10,
        hour=17,
        minute=30,
    )
    packet = PacketSupportIH02.produce_date_time()
    packet.date_time = date_time
    print(packet)
    assert packet.year == date_time.year
    assert packet.moon == date_time.month
    assert packet.diem == date_time.day
    assert packet.hour == date_time.hour
    assert packet.minute == date_time.minute


def test_device():
    print()
    invoker_ionhealth_ih02(verify_device_packet)
    invoker_ionhealth_ih02(verify_record_stream)
    invoker_ionhealth_ih02(verify_device_record)
    invoker_ionhealth_ih02(verify_device_clock)
    invoker_ionhealth_ih02(verify_storage_reset)


def verify_device_packet(device:DeviceIonHealthIH02):
    print(f"verify_device_packet")

    for index in range(2):
        print(f"--- {index} ---")
        packet = PacketSupportIH02.produce_device_info()
        print(f"packet: {packet}")
        device.packet_write(packet)
        packet = device.packet_read()
        print(f"packet: {packet}")

    for index in range(2):
        print(f"--- {index} ---")
        packet = PacketSupportIH02.produce_storage_info()
        print(f"packet: {packet}")
        device.packet_write(packet)
        packet = device.packet_read()
        print(f"packet: {packet}")

    for index in range(2):
        print(f"--- {index} ---")
        packet = PacketSupportIH02.produce_date_time()
        packet.date_time = DateTime(
            year=2019,
            month=7,
            day=10,
            hour=17,
            minute=30,
        )
        print(packet)
        device.packet_write(packet)
        packet = device.packet_read()
        print(f"packet: {packet}")


def verify_device_clock(device:DeviceIonHealthIH02):
    print(f"verify_device_clock")
    source = DateTime.now()
    packet = device.write_device_clock(source)
    target = packet.date_time
    print(f"source {source}")
    print(f"packet {packet}")
    print(f"target {target}")
    assert source.year == target.year
    assert source.month == target.month
    assert source.day == target.day
    assert source.hour == target.hour
    assert source.minute == target.minute


def verify_device_record(device:DeviceIonHealthIH02):
    print(f"verify_device_record")
    storage_status = device.read_storage_status()
    print(storage_status)
    record_count = storage_status.record_count
    for index in range(record_count):
        print(f"--- {index} ---")
        record = device.read_device_record(index)
        print(record)


def verify_record_stream(device:DeviceIonHealthIH02):
    print(f"verify_record_stream")
    device.read_record_stream()


def verify_storage_reset(device:DeviceIonHealthIH02):
    return
    # manual test enable
    print(f"verify_storage_reset")
    result = device.issue_storage_reset()
    print(result)
