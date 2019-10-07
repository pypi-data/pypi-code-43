import time

from healer.device.actor.easyhome_cf350bt import *


def test_device_actor():
    print()


def verify_machine(device:DeviceEasyHomeCF350BT):
    print()

    actor_ref = ActorEasyHomeCF350BT.start(device=device)
    time.sleep(1)

    actor_ref.stop()
    time.sleep(1)
