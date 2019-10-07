import time

import usb.core

from healer.device.actor.innovo_cms50f import *

from healer_test.device.invoker import invoker_innovo_cmd50f


def test_device_actor():
    print()
    invoker_innovo_cmd50f(verify_machine, use_with=False)


def verify_machine(device:DeviceInnovoCMS50F):
    print()

    actor_ref = ActorInnovoCMS50F.start(device=device)
    time.sleep(1)

    actor_ref.stop()
    time.sleep(1)
