import time

from healer.device.usb.arkon import *
from healer.wrapper.sudo import SUDO


def test_address():
    print()
    addr1 = AddrBusDev(1, 2)
    addr2 = AddrBusDev(1, 2)
    assert addr1 == addr2


def test_device_arkon():
    print()
    pyusb_device = usb.core.find()
    print(pyusb_device)
    device = DeviceUSB(pyusb_device)
    print(device)
    print(device.device_address())
    print(device.udev_file())
    print(device.identity_token())


def select_tester_module():
    return 'dummy_hcd'


def test_manager_usb():
    print()
    manager_usb = ManagerUSB()
    tester_module = select_tester_module()
    try:
        SUDO.execute_unit(['rmmod', tester_module])
        time.sleep(0.5)
        manager_usb.observer_start()
        time.sleep(0.5)
        SUDO.execute_unit(['modprobe', tester_module])
        time.sleep(0.5)
    finally:
        SUDO.execute_unit(['rmmod', tester_module])
        time.sleep(0.5)
        manager_usb.observer_stop()
