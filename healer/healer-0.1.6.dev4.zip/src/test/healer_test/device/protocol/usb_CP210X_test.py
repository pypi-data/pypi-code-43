
from healer.config import CONFIG
from healer.device.protocol.usb_CP210X import *


class SerialDevice(
        SerialCP210XTrait,
    ):

    pyusb_device:usb.core.Device

    def __init__(self, pyusb_device):
        super().__init__()
        self.pyusb_device = pyusb_device


def test_serial():
    print()

    pyusb_device = usb.core.find(idVendor=0x10c4, idProduct=0xea60)
    if pyusb_device:
        print(f"Device present, testing")
    else:
        print(f"Device missing, skipping")
        return
    print(pyusb_device)

    device = SerialDevice(pyusb_device)

    device.serial_IFC_ENABLE(False)
    device.serial_IFC_ENABLE(True)
    device.serial_PURGE()
    device.serial_SET_BAUDRATE()
    device.serial_SET_LINE_CTL()
    device.serial_SET_MHS()

    print(device.serial_GET_PROPS())

    print(device.serial_GET_MDMSTS())

    print(device.serial_GET_COMM_STATUS())

    device.serial_SET_XOFF()

    print(device.serial_GET_COMM_STATUS())

    device.serial_SET_XON()

    print(device.serial_GET_FLOW())
