import os
import time
import usb.core
from types import FunctionType

from healer.device.usb.arkon import IdentityUSB
from healer.device.usb.innovo_cms50f import DeviceInnovoCMS50F
from healer.device.usb.bayer_contour_next_usb import DeviceContourNextUSB
from healer.device.usb.ketonix_usb import DeviceKetonixUSB
from healer.device.usb.ionhealth_ih02 import DeviceIonHealthIH02

os.environ['PYUSB_DEBUG'] = 'debug'

print(f"HOME={os.environ.get('HOME')}")
print(f"PYUSB_DEBUG={os.environ.get('PYUSB_DEBUG')}")


def check_pyusb_device(identity:IdentityUSB) -> usb.core.Device:
    pyusb_device = usb.core.find(idVendor=identity.idVendor(), idProduct=identity.idProduct())
    if pyusb_device:
        print(f"Device present, continue")
        print(pyusb_device)
    else:
        print(f"Device missing, skipping")
    return pyusb_device


def invoker_innovo_cmd50f(testing_function:FunctionType, use_with:bool=True) -> None:
    print()

    pyusb_device = check_pyusb_device(DeviceInnovoCMS50F.identity_bucket())
    if not pyusb_device:
        return

    device = DeviceInnovoCMS50F(pyusb_device)

    with device:
        check_setup = device.check_setup()

    if check_setup:
        print(f"Device active, continue")
        print(device)
    else:
        print(f"Device sleeping, skipping")
        return

    if use_with:
        with device:
            testing_function(device)
    else:
        testing_function(device)


def invoker_bayer_contour_next(testing_function:FunctionType, use_with:bool=True) -> None:
    print()

    pyusb_device = check_pyusb_device(DeviceContourNextUSB.identity_bucket())
    if not pyusb_device:
        return

    device = DeviceContourNextUSB(pyusb_device)

    if use_with:
        with device:
            testing_function(device)
    else:
        testing_function(device)


def invoker_ketonix_usb(testing_function:FunctionType, use_with:bool=True) -> None:
    print()

    pyusb_device = check_pyusb_device(DeviceKetonixUSB.identity_bucket())
    if not pyusb_device:
        return

    device = DeviceKetonixUSB(pyusb_device)

    if use_with:
        with device:
            testing_function(device)
    else:
        testing_function(device)


def invoker_ionhealth_ih02(testing_function:FunctionType, use_with:bool=True) -> None:
    print()

    pyusb_device = check_pyusb_device(DeviceIonHealthIH02.identity_bucket())
    if not pyusb_device:
        return

    device = DeviceIonHealthIH02(pyusb_device)

    with device:
        check_setup = device.check_setup()

    if check_setup:
        print(f"Device active, continue")
        print(device)
    else:
        print(f"Device sleeping, skipping")
        return

    if use_with:
        with device:
            testing_function(device)
    else:
        testing_function(device)
