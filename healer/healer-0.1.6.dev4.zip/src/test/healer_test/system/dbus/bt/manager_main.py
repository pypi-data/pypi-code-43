import time

from healer.system.dbus.bt.manager import *


def manager_main():
    print()
    manager = BluetoothManager()

    manager.observer_start()

    time.sleep(30000)

    manager.observer_stop()

manager_main()
