import time

from healer.device.bt.arkon import *


def test_identity():
    print()
    address = "5E:7B:05:1D:45:BB"
    identity = IdentityBT.from_address(address)
    print(identity)
    assert identity == IdentityBT(vendor='5E:7B:05')


def test_manager():
    print()
    manager = ManagerBT()
    manager.observer_start()
    time.sleep(1)
    manager.observer_stop()
