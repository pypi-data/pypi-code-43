"""
Bus 001 Device 096: ID 054c:06c1 Sony Corp. RC-S380/S
"""

import nfc
import ndef
from nfc.clf import RemoteTarget

import time

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

control = nfc.ContactlessFrontend('usb:054c:06c1')

print(f"control: {control}")

while True:
    target = control.sense(RemoteTarget('106A'), RemoteTarget('106B'), RemoteTarget('212F'))
    print(f"target: {target}")
    time.sleep(1)

