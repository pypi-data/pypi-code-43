"""
Device driver for
KETONIX
Breath Ketone Analyzer
https://www.ketonix.com/webshop/ketonix-usb-no-battery-2018

Modes: classic vs continous:

classic:
* indicate mode by 5 seconds of multicolor blinking delay
* keep track of maximum output value
* display maximum output value until mode change or reset

continous:
* do not indicate mode change, no 5 second delay
* do not keep track of maximum output value
* display current maximum output value without mode chage
"""

from __future__ import annotations

import array
import copy
import enum
import logging
import struct
import time
from array import ArrayType
from dataclasses import dataclass

import usb.core
import usb.util

from healer.device.record import DeviceRecord
from healer.device.usb.arkon import DeviceUSB
from healer.support.hronos import DateTime
from healer.support.typing import cached_method
from healer.support.typing import override

logger = logging.getLogger(__name__)


@enum.unique
class FaceNum(enum.Enum):
    """
    Device usb interfaces
    """
    hid = 0


@enum.unique
class HidPointAddr(enum.Enum):
    """
    HID device end point addresses
    """
    input = 0x81
    output = 0x1


@enum.unique
class KetonixCommand(enum.Enum):
    """
    Ketonix device commands
    """

    # send configuration
    send_data = 0x36  # 54

    # read measured data
    read_data = 0x37  # 55

    # measure with max memo
    mode_classic = 0x42  # 66

    # measure without max memo
    mode_continous = 0x43  # 67


class KetonixIndex:
    """
    KetonixPacket field offset
    """
    command = 0
    output = 1
    sensor = 3
    heater = 5
    level_grn = 7
    level_yel = 9
    level_red = 11
    calibration = 13
    device_type = 15
    device_id = 17
    correction = 19


@dataclass
class KetonixPacket:
    """
    Ketonix device packet
    """

    # uderlying device data
    buffer:ArrayType

    def __str__(self):
        return (
            f"Packet("
            f"command='{self.command}', "
            f"device_id='{self.device_id}', "
            f"device_type='{self.device_type}', "
            f"calibration='{self.calibration}', "
            f"correction='{self.correction}', "
            f"level_grn='{self.level_grn}', "
            f"level_yel='{self.level_yel}', "
            f"level_red='{self.level_red}', "
            f"output='{self.output}', "
            f"sensor='{self.sensor}', "
            f"heater='{self.heater}', "
            f")"
        )

    @property
    def command(self) -> int:
        "R/W device command"
        return struct.unpack_from('<B', self.buffer, KetonixIndex.command)[0]

    @command.setter
    def command(self, value:int) -> None:
        struct.pack_into('<B', self.buffer, KetonixIndex.command, value)

    @property
    def device_id(self) -> int:
        "R/W configurable device identity"
        return struct.unpack_from('<H', self.buffer, KetonixIndex.device_id)[0]

    @device_id.setter
    def device_id(self, value:int) -> None:
        struct.pack_into('<H', self.buffer, KetonixIndex.device_id, value)

    @property
    def device_type(self) -> int:
        "R/W configurable device identity"
        return struct.unpack_from('<H', self.buffer, KetonixIndex.device_type)[0]

    @device_type.setter
    def device_type(self, value:int) -> None:
        struct.pack_into('<H', self.buffer, KetonixIndex.device_type, value)

    @property
    def level_grn(self) -> int:
        "R/W trigger level for green led, compared to output"
        return struct.unpack_from('<H', self.buffer, KetonixIndex.level_grn)[0]

    @level_grn.setter
    def level_grn(self, value:int) -> None:
        struct.pack_into('<H', self.buffer, KetonixIndex.level_grn, value)

    @property
    def level_yel(self) -> int:
        "R/W trigger level for yellow led, compared to output"
        return struct.unpack_from('<H', self.buffer, KetonixIndex.level_yel)[0]

    @level_yel.setter
    def level_yel(self, value:int) -> None:
        struct.pack_into('<H', self.buffer, KetonixIndex.level_yel, value)

    @property
    def level_red(self) -> int:
        "R/W trigger level for red led, compared to output"
        return struct.unpack_from('<H', self.buffer, KetonixIndex.level_red)[0]

    @level_red.setter
    def level_red(self, value:int) -> None:
        struct.pack_into('<H', self.buffer, KetonixIndex.level_red, value)

    @property
    def calibration(self) -> int:
        "R/W calibration setting: shift of 'sensor' to produce 'output'"
        return struct.unpack_from('<H', self.buffer, KetonixIndex.calibration)[0]

    @calibration.setter
    def calibration(self, value:int) -> None:
        struct.pack_into('<H', self.buffer, KetonixIndex.calibration, value)

    @property
    def correction(self) -> int:
        "R/W correction setting; purpose:???"
        return struct.unpack_from('<H', self.buffer, KetonixIndex.correction)[0]

    @correction.setter
    def correction(self, value:int) -> None:
        struct.pack_into('<H', self.buffer, KetonixIndex.correction, value)

    @property
    def output(self) -> int:
        "R/O reported/calculated sensor value"
        return struct.unpack_from('<H', self.buffer, KetonixIndex.output)[0]

    @output.setter
    def output(self, value:int) -> None:
        struct.pack_into('<H', self.buffer, KetonixIndex.output, value)

    @property
    def sensor(self) -> int:
        "R/O measured/internal sensor value"
        return struct.unpack_from('<H', self.buffer, KetonixIndex.sensor)[0]

    @sensor.setter
    def sensor(self, value:int) -> None:
        struct.pack_into('<H', self.buffer, KetonixIndex.sensor, value)

    @property
    def heater(self) -> int:
        "R/O sensor heater element temperature level: 0...100; 100 means ready"
        return struct.unpack_from('<H', self.buffer, KetonixIndex.heater)[0]

    @heater.setter
    def heater(self, value:int) -> None:
        struct.pack_into('<H', self.buffer, KetonixIndex.heater, value)


class RecordKetonixUSB:
    "persistent device records"

    @dataclass(frozen=True)
    class Header(DeviceRecord):
        "static session header"
        device_codec_guid = 501

        device_id:int
        device_type:int
        level_grn:int
        level_yel:int
        level_red:int
        calibration:int
        correction:int
        heater:int

    @dataclass(frozen=True)
    class Result(DeviceRecord):
        "streaming session data"
        device_codec_guid = 502

        stamp:DateTime  # record stamp
        sensor:int  # device sensor value

    @dataclass(frozen=True)
    class Summary(DeviceRecord):
        "measured session data"
        device_codec_guid = 503

        stamp:DateTime  # session start stamp
        timer:float  # session duration, second
        value:int  # measured session value (max-min)

    @staticmethod
    def produce_header(packet:KetonixPacket) -> RecordKetonixUSB.Header:
        "extract summary record"
        return RecordKetonixUSB.Summary(
            device_id=packet.device_id,
            device_type=packet.device_type,
            level_grn=packet.level_grn,
            level_yel=packet.level_yel,
            level_red=packet.level_red,
            calibration=packet.calibration,
            correction=packet.correction,
            heater=packet.heater,
        )

#     @staticmethod
#     def produce_result(packet:KetonixPacket) -> RecordKetonixUSB.Result:
#         "extract result record"
#         return RecordKetonixUSB.Result(
#             output=packet.output,
#             sensor=packet.sensor,
#         )


@dataclass
class DeviceKetonixUSB(DeviceUSB):
    """
    Breath Ketone Analyzer
    https://www.ketonix.com/
    https://www.ketonix.com/webshop/ketonix-usb-no-battery-2018
    """

    config_entry = 'device/usb/ketonix_usb'

    @override
    def start(self) -> None:
        super().start()

    @override
    def stop(self) -> None:
        super().stop()

    @cached_method
    def face_hid(self) -> usb.core.Interface:
        return self.select_face(FaceNum.hid)

    @cached_method
    def point_hid_input(self) -> usb.core.Endpoint:
        return self.select_point(self.face_hid(), HidPointAddr.input)

    @cached_method
    def point_hid_output(self) -> usb.core.Endpoint:
        return self.select_point(self.face_hid(), HidPointAddr.output)

    def hid_get(self) -> array:
        "receive device input as byte array"
        point = self.point_hid_input()
        buffer = self.pyusb_device.read(
            point.bEndpointAddress, point.wMaxPacketSize, self.timeout()
        )
        # logger.trace(f"hid_get: {repr(buffer)}")
        time.sleep(0.1)  # pause for device stability
        return buffer

    def hid_put(self, buffer:array) -> None:
        "transmit byte array into hid device"
        point = self.point_hid_output()
        # logger.trace(f"hid_put: {repr(buffer)}")
        assert len(buffer) <= point.wMaxPacketSize
        self.pyusb_device.write(
            point.bEndpointAddress, buffer, self.timeout()
        )
        time.sleep(0.1)  # pause for device stability

    def issue_command(self, command:KetonixCommand) -> None:
        "transmit simple command to the device"
        buffer = usb.util.create_buffer(1)
        buffer[0] = command.value
        self.hid_put(buffer)

    def mode_classic(self) -> None:
        "switch device to classic mode (remember output max); followed by device delay"
        with self.device_lock:
            self.issue_command(KetonixCommand.mode_classic)
            time.sleep(5.0)  # wait while device is non-responsive

    def mode_continous(self) -> None:
        "switch device to continous mode (stream output value); not followd by device delay"
        with self.device_lock:
            self.issue_command(KetonixCommand.mode_continous)
            time.sleep(0.5)  # wait while device is non-responsive

    def read_data(self) -> KetonixPacket:
        "read device measurement packet"
        with self.device_lock:
            self.issue_command(KetonixCommand.read_data)
            buffer = self.hid_get()
        packet = KetonixPacket(buffer)
        logger.debug(f"packet: {packet}")
        return packet

    def write_data(self, packet:KetonixPacket) -> None:
        "transmit congiguration settings to the device; followed by busy blinking"
        logger.debug(f"packet: {packet}")
        buffer = copy.copy(packet.buffer)
        buffer[0] = KetonixCommand.send_data.value
        with self.device_lock:
            self.hid_put(buffer)
            time.sleep(3.0)  # wait while device is non-responsive

    def update_data(self,
        device_id:int=None,
        device_type:int=None,
        correction:int=None,
        calibration:int=None,
        level_grn:int=None,
        level_yel:int=None,
        level_red:int=None,
    ) -> KetonixPacket:
        "transmit congiguration settings to the device"
        packet = self.read_data()
        if device_id is not None:
            packet.device_id = device_id
        if device_type is not None:
            packet.device_type = device_type
        if correction is not None:
            packet.correction = correction
        if calibration is not None:
            packet.calibration = calibration
        if level_grn is not None:
            packet.level_grn = level_grn
        if level_yel is not None:
            packet.level_yel = level_yel
        if level_red is not None:
            packet.level_red = level_red
        self.write_data(packet)

    @override
    def device_identity(self) -> str:
        "ketonix uses fixed serial number and user configurable device id"
        packet = self.read_data()
        super_id = super().device_identity()
        instance_id = packet.device_id
        return f"{super_id}/{instance_id}"

    @override
    def device_description(self) -> str:
        return "Ketonix USB Breath Ketone Analyzer"
