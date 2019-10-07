"""
"""

import time

from healer.device.actor.bayer_contour_next_usb import *
from healer_test.device.invoker import invoker_bayer_contour_next


def test_device_actor():
    print()
    invoker_bayer_contour_next(verify_machine, use_with=False)


def verify_machine(device:DeviceContourNextUSB):
    print()

    actor_ref = ActorBayerContourNextUSB.start(device=device)
    print(f"started")

    state = lambda : actor_ref.ask(Command.STATE)

    while state() == State.STOPPED:  # await start
        time.sleep(0.2)

    print(f"running")

    while state() != State.STOPPED:  # await stop
        time.sleep(0.2)

    print(f"finished")

    actor_ref.stop()
