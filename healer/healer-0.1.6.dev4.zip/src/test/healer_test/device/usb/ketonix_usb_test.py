"""
"""

import threading

from healer.device.usb.ketonix_usb import *
from healer_test.device.invoker import invoker_ketonix_usb
from healer.config import CONFIG


def test_packet():
    print()
    buffer = usb.util.create_buffer(64)
    packet = KetonixPacket(buffer)
    packet.command = KetonixCommand.read_data.value
    packet.device_id = 1111
    packet.device_type = 9999
    packet.calibration = 4567
    packet.correction = 5678
    packet.level_grn = 123
    packet.level_yel = 234
    packet.level_red = 345
    packet.output = 1234
    packet.sensor = 2345
    packet.heater = 3456
    source = str(packet)
    print(source)
    target = "Packet(command='55', device_id='1111', device_type='9999', calibration='4567', correction='5678', level_grn='123', level_yel='234', level_red='345', output='1234', sensor='2345', heater='3456', )"
    assert source == target


def test_device_ketonix():
    print()
    invoker_ketonix_usb(verify_device_modes)
    invoker_ketonix_usb(verify_device_packet)
    invoker_ketonix_usb(verify_device_stream)
    invoker_ketonix_usb(verify_device_update)
#     invoker_ketonix_usb(verify_device_color)
#     invoker_ketonix_usb(verify_device_level)


def verify_device_level(device:DeviceKetonixUSB):
    print()

    for level in range(2000, 2050, 10):
        print(f"level={level}")
        device.update_data(level_grn=level)


def verify_device_color(device:DeviceKetonixUSB):
    print()

    MIN = 0
    MAX = 1000

    device.mode_continous()

    def color_off():
        device.update_data(level_grn=MAX, level_yel=MAX, level_red=MAX)

    def color_grn():
        device.update_data(level_grn=MIN, level_yel=MAX, level_red=MAX)

    def color_yel():
        device.update_data(level_grn=MAX, level_yel=MIN, level_red=MAX)

    def color_red():
        device.update_data(level_grn=MAX, level_yel=MAX, level_red=MIN)

    color_off()

    event = threading.Event()

    def read_task():
        while not event.is_set():
            print(f"TASK")
            device.read_data()

    thread = threading.Thread(target=read_task, daemon=True)
    thread.start()

    for _ in range(10):
        color_grn()
        time.sleep(0.1)
        color_yel()
        time.sleep(0.1)
        color_red()
        time.sleep(0.1)

    event.set()


def verify_device_modes(device:DeviceKetonixUSB):
    print()
    device.mode_classic()
    device.mode_continous()
    device.mode_classic()
    device.mode_continous()


def verify_device_stream(device:DeviceKetonixUSB):
    print()
    for _ in range(5):
        device.read_data()


def verify_device_update(device:DeviceKetonixUSB):
    print()

    device.mode_continous()

    source = device.read_data()
    print(f"source: {source}")

    device.update_data(
        device_id=1234,
        device_type=23,
        correction=40,
        calibration=60,
        level_grn=450,
        level_yel=650,
        level_red=850,
    )

    result = device.read_data()
    print(f"result: {result}")

    device.write_data(source)

    device.mode_continous()

    target = device.read_data()
    print(f"target: {target}")

    assert source.device_id == target.device_id
    assert source.device_type == target.device_type
    assert source.correction == target.correction
    assert source.calibration == target.calibration
    assert source.level_grn == target.level_grn
    assert source.level_yel == target.level_yel
    assert source.level_grn == target.level_grn
    assert source.level_red == target.level_red

    # force levels
    device.update_data(
        device_id=1,
        device_type=1,  # 2 ???
        level_grn=1000,
        level_yel=1000,
        level_red=1000,
        correction=0,  # 0 ???
        calibration=0,  # 100 offset
    )

    result = device.read_data()
    print(f"result: {result}")


def verify_device_packet(device:DeviceKetonixUSB):
    print()
    print(device.device_identity())
