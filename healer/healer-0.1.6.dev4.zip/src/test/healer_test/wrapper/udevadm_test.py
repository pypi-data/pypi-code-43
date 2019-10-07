
from healer.wrapper.udevadm import *


def test_apply():
    print()
    result = UDEVADM.rules_reload()
    print(result)
    result = UDEVADM.events_trigger()
    print(result)
