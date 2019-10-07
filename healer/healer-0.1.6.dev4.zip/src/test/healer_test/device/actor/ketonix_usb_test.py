"""
"""

import time

from healer.device.actor.ketonix_usb import *
from healer_test.device.invoker import invoker_ketonix_usb


def test_device_actor():
    print()
    invoker_ketonix_usb(verify_machine, use_with=False)


def verify_machine(device:DeviceKetonixUSB):
    print()

    actor_ref = ActorKetonixUSB.start(device=device)
    print(f"started")

    state = lambda : actor_ref.ask(Command.STATE)

    while state() == State.STOPPED:  # await start
        time.sleep(0.2)

    print(f"running")

    while state() != State.STOPPED:  # await stop
        time.sleep(0.2)

    print(f"finished")

    actor_ref.stop()
