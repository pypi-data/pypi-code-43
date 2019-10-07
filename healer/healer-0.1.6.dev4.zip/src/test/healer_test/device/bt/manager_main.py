import time

from healer.device.bt.arkon import *


def manager_main():
    print(f"manager_main")
    manager = ManagerBT()
    manager.observer_start()
    time.sleep(30000)
    manager.observer_stop()


manager_main()
