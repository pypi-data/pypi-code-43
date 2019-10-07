import time

from healer.system.dbus.bt.manager import *


def test_manager():
    print()
    manager = BluetoothManager()
    manager.observer_start()
    time.sleep(1)
    manager.observer_stop()
