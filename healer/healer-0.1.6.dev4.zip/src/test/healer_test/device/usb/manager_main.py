import time

from healer.device.usb.arkon import *


def manager_main():
    print(f"manager_main")
    manager_usb = ManagerUSB()
    manager_usb.observer_start()
    time.sleep(30000)
    manager_usb.observer_stop()

manager_main()
