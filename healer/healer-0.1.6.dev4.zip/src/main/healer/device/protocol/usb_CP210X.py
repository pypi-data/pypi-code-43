"""
CP210X VIRTUAL COM PORT INTERFACE
https://www.silabs.com/documents/public/application-notes/AN571.pdf
"""

from __future__ import annotations

import array
import logging
import struct
import time
from dataclasses import dataclass
from enum import Enum

import usb.core
import usb.util

logger = logging.getLogger(__name__)


class RequestType(Enum):
    """
    CP210x Data Flow
    """
    HOST_TO_INTERFACE = 0x41
    INTERFACE_TO_HOST = 0xC1


class Request(Enum):
    """
    CP210x Control Commands
    """
    IFC_ENABLE = 0x00
    SET_BAUDDIV = 0x01
    GET_BAUDDIV = 0x02
    SET_LINE_CTL = 0x03
    GET_LINE_CTL = 0x04
    SET_BREAK = 0x05
    IMM_CHAR = 0x06
    SET_MHS = 0x07
    GET_MDMSTS = 0x08
    SET_XON = 0x09
    SET_XOFF = 0x0A
    SET_EVENTMASK = 0x0B
    GET_EVENTMASK = 0x0C
    SET_CHAR = 0x0D
    GET_CHARS = 0x0E
    GET_PROPS = 0x0F
    GET_COMM_STATUS = 0x10
    RESET = 0x11
    PURGE = 0x12
    SET_FLOW = 0x13
    GET_FLOW = 0x14
    EMBED_EVENTS = 0x15
    GET_EVENTSTATE = 0x16
    SET_CHARS = 0x19
    GET_BAUDRATE = 0x1D
    SET_BAUDRATE = 0x1E


class Support:
    """
    Utility functions
    """

    @staticmethod
    def format_hex2(value):
        return '{:02x}'.format(value).upper()


class CommIndex:
    """
    Status packet offset
    """
    ulErrors = 0
    ulHoldReasons = 4
    ulAmountInInQueue = 8
    ulAmountInOutQueue = 12
    bWaitForImmediate = 17


@dataclass
class CommStatus:
    """
    Serial Status Response
    """
    # uderlying device data
    buffer:array

    def __str__(self):
        return (
            f"CommStatus("
            f"error='{hex(self.ulErrors())}', "
            f"hold='{hex(self.ulHoldReasons())}', "
            f"input='{self.ulAmountInInQueue()}', "
            f"output='{self.ulAmountInOutQueue()}', "
            f"waitfor='{hex(self.bWaitForImmediate())}', "
            f")"
        )

    def ulErrors(self) -> int:
        return struct.unpack_from('I', self.buffer, CommIndex.ulErrors)[0]

    def ulHoldReasons(self) -> int:
        return struct.unpack_from('I', self.buffer, CommIndex.ulHoldReasons)[0]

    def ulAmountInInQueue(self) -> int:
        return struct.unpack_from('I', self.buffer, CommIndex.ulAmountInInQueue)[0]

    def ulAmountInOutQueue(self) -> int:
        return struct.unpack_from('I', self.buffer, CommIndex.ulAmountInOutQueue)[0]

    def bWaitForImmediate(self) -> int:
        return struct.unpack_from('B', self.buffer, CommIndex.bWaitForImmediate)[0]


@dataclass
class ModemStatus:
    """
    Serial Modem Status
    """
    # uderlying device data
    buffer:array

    def value(self, mask:int) -> int:
        if self.buffer[0] & mask:
            return 1
        else:
            return 0

    def DTR(self):
        return self.value(0x01)

    def RTS(self):
        return self.value(0x02)

    def CTS(self):
        return self.value(0x10)

    def DSR(self):
        return self.value(0x20)

    def RID(self):
        return self.value(0x40)

    def DCD(self):
        return self.value(0x80)

    def __str__(self):
        return (
            f"ModemStatus("
            f"DTR='{self.DTR()}', "
            f"RTS='{self.RTS()}', "
            f"CTS='{self.CTS()}', "
            f"DSR='{self.DSR()}', "
            f"RID='{self.RID()}', "
            f"DCD='{self.DCD()}', "
            f")"
        )


class PropertyIndex:
    """
    Property fields packet offset
    """
    wLength = 0  # 2
    bcdVersion = 2  # 2
    ulServiceMask = 4  # 4
    ulMaxTxQueue = 12  # 4
    ulMaxRxQueue = 16  # 4
    ulMaBaud = 20  # 4
    ulProvSubType = 24  # 4
    ulProvCapabilities = 28  # 4
    ulSettableParams = 32  # 4
    ulSettableBaud = 36  # 4


@dataclass
class PropertyFields:
    """
    Device communication properties
    """
    # uderlying device data
    buffer:array


class FlowIndex:
    """
    Flow Control packet offset
    """
    ulControlHandshake = 0
    ulFlowReplace = 4
    ulXonLimit = 8
    ulXoffLimit = 12


@dataclass
class FlowControl:
    """
    Flow Control State Setting/Response
    """
    # uderlying device data
    buffer:array

    def __str__(self):
        return (
            f"FlowControl("
            f"handshake='{hex(self.ulControlHandshake())}', "
            f"replace='{hex(self.ulFlowReplace())}', "
            f"xon_limit='{self.ulXonLimit()}', "
            f"xoff_limit='{self.ulXoffLimit()}', "
            f")"
        )

    def ulControlHandshake(self) -> int:
        return struct.unpack_from('i', self.buffer, FlowIndex.ulControlHandshake)[0]

    def ulFlowReplace(self) -> int:
        return struct.unpack_from('i', self.buffer, FlowIndex.ulFlowReplace)[0]

    def ulXonLimit(self) -> int:
        return struct.unpack_from('i', self.buffer, FlowIndex.ulXonLimit)[0]

    def ulXoffLimit(self) -> int:
        return struct.unpack_from('i', self.buffer, FlowIndex.ulXoffLimit)[0]


class SerialCP210XTrait:
    """
    Tait: CP210X virtual com port interface
    """

    pyusb_device:usb.core.Device

    def serial_get(self, request:Request, wValue:int=0, wIndex:int=0, buffer:array=None) -> bytes:
        "obtain settings via usb control transfer"
        bmRequestType = RequestType.INTERFACE_TO_HOST.value
        bRequest = request.value
        logger.trace(f"ctrl_transfer: {request.name} {hex(wValue)} {hex(wIndex)}")
        buffer = self.pyusb_device.ctrl_transfer(
            bmRequestType=bmRequestType,
            bRequest=bRequest,
            wValue=wValue,
            wIndex=wIndex,
            data_or_wLength=buffer,
        )
        return buffer

    def serial_set(self, request:Request, wValue:int=0, wIndex:int=0, buffer:array=None) -> None:
        "change settings via usb control transfer"
        bmRequestType = RequestType.HOST_TO_INTERFACE.value
        bRequest = request.value
        logger.trace(f"ctrl_transfer: {request.name} {hex(wValue)} {hex(wIndex)}")
        self.pyusb_device.ctrl_transfer(
            bmRequestType=bmRequestType,
            bRequest=bRequest,
            wValue=wValue,
            wIndex=wIndex,
            data_or_wLength=buffer,
        )

    def serial_IFC_ENABLE(self, state:bool=True) -> None:
        """
        wValue = 0: disable
        wValue = 1: enable
        """
        self.serial_set(Request.IFC_ENABLE, wValue=int(state))

    def serial_PURGE(self, clear_receive_queue:bool=True, clear_transmit_queue:bool=True) -> None:
        """
        bit 0: Clear the transmit queue.
        bit 1: Clear the receive queue.
        """
        purge = 0
        if clear_transmit_queue:
            purge = purge | 0x1
        if clear_receive_queue:
            purge = purge | 0x2
        self.serial_set(Request.PURGE, wValue=purge)

    def serial_SET_BAUDRATE(self, baudrate:int=115200) -> None:
        buffer = usb.util.create_buffer(4)
        struct.pack_into('I', buffer, 0, baudrate)
        self.serial_set(Request.SET_BAUDRATE, buffer=buffer)

    def serial_SET_LINE_CTL(self, word_length:int=8, stop_bits:int=0, parity_setting:int=0) -> None:
        """
        bits 3-0: Stop bits:
           0 = 1 stop bit
           1 = 1.5 stop bits
           2 = 2 stop bits
           other values reserved.
        bits 7-4: Parity setting:
           0 = none.
           1 = odd.
           2 = even.
           3 = mark.
           4 = space.
        bits 15-8: Word length, legal values are 5, 6, 7 and 8.
        """
        control = (word_length << 8) | (parity_setting << 4) | (stop_bits << 0)
        self.serial_set(Request.SET_LINE_CTL, wValue=control)

    def serial_SET_MHS(self, mhs_bit_mask:int=0x0303) -> None:
        """
        Set modem handshaking
            bit 0: DTR state.
            bit 1: RTS state.
            bits 2–7: reserved.
            bit 8: DTR mask, if clear, DTR will not be changed.
            bit 9: RTS mask, if clear, RTS will not be changed.
            bits 10–15: reserved.
        """
        self.serial_set(Request.SET_MHS, wValue=mhs_bit_mask)

    def serial_GET_MDMSTS(self) -> ModemStatus:
        "get modem status"
        buffer = self.serial_get(Request.GET_MDMSTS, buffer=8)
        return ModemStatus(buffer)

    def serial_GET_PROPS(self) -> PropertyFields:
        "get device properties"
        buffer = self.serial_get(Request.GET_PROPS, buffer=128)
        return PropertyFields(buffer)

    def serial_GET_COMM_STATUS(self) -> CommStatus:
        "get the serial status"
        buffer = self.serial_get(Request.GET_COMM_STATUS, buffer=32)
        return CommStatus(buffer)

    def serial_SET_XON(self) -> None:
        "emulate XON"
        self.serial_set(Request.SET_XON)

    def serial_SET_XOFF(self) -> None:
        "emulate XOFF"
        self.serial_set(Request.SET_XOFF)

    def serial_GET_FLOW(self) -> FlowControl:
        "get flow control"
        buffer = self.serial_get(Request.GET_FLOW, buffer=32)
        return FlowControl(buffer)

    def serial_has_pending_input(self) -> bool:
        "verify external device input stream"
        return self.serial_GET_COMM_STATUS().ulAmountInInQueue() > 0

    def serial_has_pending_output(self) -> bool:
        "verify internal host app device output stream"
        return self.serial_GET_COMM_STATUS().ulAmountInOutQueue() > 0

    def serial_clear_pending_input(self, delay:float=0.2) -> None:
        "discard any input stream still transmitted by external device"
        time.sleep(delay)  # settle device
        while self.serial_has_pending_input():
            self.serial_PURGE(clear_receive_queue=True, clear_transmit_queue=False)
            time.sleep(delay)

    def serial_clear_pending_output(self, delay:float=0.2) -> None:
        "discard any output stream still scheduled by internal host app"
        time.sleep(delay)  # settle device
        while self.serial_has_pending_ouput():
            self.serial_PURGE(clear_receive_queue=False, clear_transmit_queue=True)
            time.sleep(delay)
