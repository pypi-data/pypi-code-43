"""
Bus 001 Device 096: ID 054c:06c1 Sony Corp. RC-S380/S
"""

import time

import nfc
import ndef
from nfc.clf import RemoteTarget

import usb.core
import usb.util
from typing import List, Any

device = usb.core.find(idVendor=0x054c, idProduct=0x06c1)

for conf in device:
    for face in conf:
        face_num = face.bInterfaceNumber
        if device.is_kernel_driver_active(face_num):
            device.detach_kernel_driver(face_num)

device.reset()
device.set_configuration()

print(f"device: {device}")

nfc_clf = nfc.ContactlessFrontend()

if not nfc_clf.open(path='usb:054c:06c1'):
    raise RuntimeError("Failed to open NFC device.")

print(f"nfc_clf: {nfc_clf}")

# target = nfc_clf.sense(
#     RemoteTarget('106A'),
#     RemoteTarget('106B'),
#     RemoteTarget('212F'),
# )
# print(f"target: {target}")


def on_startup(target_list:List[nfc.clf.RemoteTarget]) -> Any:
    for target in target_list:
        print(f"on_startup: target: {target}")
    return target_list


def on_discover(target:nfc.clf.RemoteTarget) -> bool:
    print(f"on_discover: target: {target}")
    return True


def on_connect(tag:nfc.tag.Tag) -> bool:
    print(f"on_connect: tag: {tag}")
    return True


def on_release(tag:nfc.tag.Tag) -> bool:
    print(f"on_release: tag: {tag}")
    return True


config = {
    'interval': 5,
    'iterations': 1,
    'on-startup': on_startup,
    'on-discover': on_discover,
    'on-connect': on_connect,
    'on-release': on_release,
    'targets': ['106B'],
}

while True:

    result = nfc_clf.connect(rdwr=config)
    print(f"result: {result}")
    time.sleep(1)

nfc_clf.close()

"""
on_startup: target: 106A
on_startup: target: 106B
on_startup: target: 212F
on_discover: target: 212F sensf_res=0101FE6A55C116AADD00000000000000000FAB
on_discover: target: 106A sdd_res=085BC61F sel_res=60 sens_res=0400
on_connect: tag: Type4ATag MIU=255 FWT=0.038664
on_release: tag: Type4ATag MIU=255 FWT=0.038664
result: True
3.
"""
