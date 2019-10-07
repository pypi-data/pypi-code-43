
import healer

# from healer.config import CONFIG

# import os
# os.environ['PYUSB_DEBUG'] = 'debug'

import usb.core
import usb.util

# device = usb.core.find(idVendor=0x10c4, idProduct=0xea60)
device = usb.core.find(idVendor=0x10c4, idProduct=0xea60)
device.reset()
device.set_configuration()

# bus = device.bus
# address = device.address
# print(f"bus={bus} address={address}")
# device = usb.core.find(bus=bus, address=address)
# print(device)

device = usb.core.find(idVendor=0x10c4, idProduct=0xea60)
device.reset()
device.set_configuration()

# for config in device:
#     print("---config---")
#     print(config)
#     for interface in config:
#         print("---interface---")
#         print(interface)

# print(f"active@0={device.is_kernel_driver_active(0)}")
# print(f"active@1={device.is_kernel_driver_active(1)}")
#
# if device.is_kernel_driver_active(0):
#     device.detach_kernel_driver(0)
#
# if device.is_kernel_driver_active(1):
#     device.detach_kernel_driver(1)
#
# print(f"active@0={device.is_kernel_driver_active(0)}")
# print(f"active@1={device.is_kernel_driver_active(1)}")

# config = device[0]
# print(config)

# usb.core.USBError: [Errno 16] Resource busy
# device.set_configuration()
# config = device.get_active_configuration()
# print(config)

# face0 = config[(0,0)]
# print(face0)

# face1 = config[(1,0)]
# print(face1)

# face_list = config.interfaces()
# print(face_list)

# config_list = device.configurations()
# print(config_list)
