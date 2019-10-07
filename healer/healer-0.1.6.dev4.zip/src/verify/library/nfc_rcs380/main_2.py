"""
Bus 001 Device 096: ID 054c:06c1 Sony Corp. RC-S380/S
"""

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


def on_startup(target_list:List[nfc.clf.RemoteTarget]) -> Any:
    ""


def on_connect(value):
    ""
    print(f"on_connect: {value}")


nfc_clf = nfc.ContactlessFrontend('usb:054c:06c1')

llcp = {
    'on-connect': on_connect,
}

if not nfc_clf.connect(llcp={}):
    raise RuntimeError("Failed to connect NFC device.")

print(f"nfc_clf: {nfc_clf}")

nfc_clf.close()
