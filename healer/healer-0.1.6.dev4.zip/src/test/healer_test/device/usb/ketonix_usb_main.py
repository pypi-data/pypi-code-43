import time

from healer.device.usb.ketonix_usb import *
from healer_test.device.invoker import invoker_ketonix_usb


def main_device_ketonix():
    print()
    invoker_ketonix_usb(verify_device_stream)


def verify_device_stream(device:DeviceKetonixUSB):
    print()
    device.mode_continous()
    while True:
        packet = device.read_data()
        print(packet)
        time.sleep(2)


main_device_ketonix()
