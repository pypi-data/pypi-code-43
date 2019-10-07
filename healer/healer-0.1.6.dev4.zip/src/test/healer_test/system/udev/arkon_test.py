
import time
from healer.wrapper.sudo import SUDO
from healer.system.udev.arkon import *


class ManagerExample(ManagerUDEV):
    """
    """

    action = None
    device = None

    def react_event(self, action:str, pyudev_device:pyudev.Device) -> None:
        super().react_event(action, pyudev_device)
        self.action = action
        self.device = pyudev_device


def test_monitor_module():
    print()

    SUDO.execute_unit(['rmmod', 'dummy'])

    manager = ManagerExample()
    print(manager)

    manager.observer_start()
    manager.observer_start()

    SUDO.execute_unit(['modprobe', 'dummy'])

    for _ in range(10):
        if manager.action:
            break
        else:
            time.sleep(0.5)

    manager.observer_stop()
    manager.observer_stop()

    assert manager.action == 'add'
    assert manager.device.subsystem == 'module'
    assert manager.device.device_path == '/module/dummy'


def test_monitor_trigger():
    print()
    monitor = ManagerExample()
    command = [
        'udevadm', 'trigger',
        '--settle',
        '--action=bind',
        '--subsystem-match=usb',
        '--attr-match=idVendor=1a79',
        '--attr-match=idProduct=7410',
    ]
    monitor.observer_start()
    SUDO.execute_unit(command)
    time.sleep(1)
    monitor.observer_stop()
