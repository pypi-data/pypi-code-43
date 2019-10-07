import time

from healer.system.dbus.arkon import *


def test_manager():
    print()

    agent_manager = ManagerDBUS()

    agent_manager.observer_start()

    time.sleep(1)

    agent_manager.observer_stop()
