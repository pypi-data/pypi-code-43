"""
Implements HID via USB control transfer
"""

from __future__ import annotations

import logging

import usb.core

logger = logging.getLogger(__name__)

"""
bmRequestType
 Request types to use in ControlTransfer().
"""
REQUEST_TYPE_STANDARD = (0x00 << 5)
REQUEST_TYPE_CLASS = (0x01 << 5)
REQUEST_TYPE_VENDOR = (0x02 << 5)
REQUEST_TYPE_RESERVED = (0x03 << 5)

"""
bmRequestType
Recipient bits for the reqType of ControlTransfer().
Values 4 - 31 are reserved.
"""
RECIPIENT_DEVICE = 0x00
RECIPIENT_INTERFACE = 0x01
RECIPIENT_ENDPOINT = 0x02
RECIPIENT_OTHER = 0x03

"""
bmRequestType
in: device-to-host
"""
ENDPOINT_IN = 0x80

"""
bmRequestType
out: host-to-device
"""
ENDPOINT_OUT = 0x00

"""
Descriptor types
"""
DT_DEVICE = 0x01
DT_CONFIG = 0x02
DT_STRING = 0x03
DT_INTERFACE = 0x04
DT_ENDPOINT = 0x05
DT_HID = 0x21
DT_REPORT = 0x22
DT_PHYSICAL = 0x23
DT_HUB = 0x29

"""
Standard request types
"""
REQUEST_GET_STATUS = 0x00
REQUEST_CLEAR_FEATURE = 0x01
REQUEST_SET_FEATURE = 0x03
REQUEST_SET_ADDRESS = 0x05
REQUEST_GET_DESCRIPTOR = 0x06
REQUEST_SET_DESCRIPTOR = 0x07
REQUEST_GET_CONFIGURATION = 0x08
REQUEST_SET_CONFIGURATION = 0x09
REQUEST_GET_INTERFACE = 0x0A
REQUEST_SET_INTERFACE = 0x0B
REQUEST_SYNCH_FRAME = 0x0C

"""
bRequest
"""
HID_GET_REPORT = 0x01
HID_GET_IDLE = 0x02
HID_GET_PROTOCOL = 0x03
HID_SET_REPORT = 0x09
HID_SET_IDLE = 0x0A
HID_SET_PROTOCOL = 0x0B
HID_REPORT_TYPE_INPUT = 0x01
HID_REPORT_TYPE_OUTPUT = 0x02
HID_REPORT_TYPE_FEATURE = 0x03


class ControlTransferTraitHID:
    """
    Trait: implement HID functions via USB control transfer
    """

    pyusb_device:usb.core.Device

    def hid_get_report(self, wIndex:int=0, wValue:int=0) -> bytes:
        """
        Implements HID GetReport via USB control transfer
        :wIndex: hid device interface number, normally 0
        """
        bmRequestType = REQUEST_TYPE_CLASS | RECIPIENT_INTERFACE | ENDPOINT_IN
        bRequest = HID_GET_REPORT
        logger.trace(
            f"bmRequestType={hex(bmRequestType)} "
            f"bRequest={hex(bRequest)} "
            f"wIndex={hex(wIndex)} "
            f"wValue={hex(wValue)} "
        )
        buffer = self.pyusb_device.ctrl_transfer(
            bmRequestType=bmRequestType,
            bRequest=bRequest,
            wIndex=wIndex,
            wValue=wValue,
            data_or_wLength=64)
        return buffer

    def hid_set_report(self, wIndex:int=0, wValue:int=0, report:bytes=None) -> None:
        """
        Implements HID SetReport via USB control transfer
        :wIndex: hid device interface number, normally 0
        """
        bmRequestType = REQUEST_TYPE_CLASS | RECIPIENT_INTERFACE | ENDPOINT_OUT
        bRequest = HID_SET_REPORT
        logger.trace(
            f"bmRequestType={hex(bmRequestType)} "
            f"bRequest={hex(bRequest)} "
            f"wIndex={hex(wIndex)} "
            f"wValue={hex(wValue)} "
        )
        self.pyusb_device.ctrl_transfer(
            bmRequestType=bmRequestType,
            bRequest=bRequest,
            wIndex=wIndex,
            wValue=wValue,
            data_or_wLength=report)
