"""
Device driver for
Easy@Home CF350BT bluetooth body fat scale
https://www.manualslib.com/manual/1035854/Easy-Home-Cf350bt.html
"""

from __future__ import annotations

import logging
import struct
from dataclasses import dataclass
from dataclasses import field

from healer.device.bt.arkon import DeviceBT
from healer.device.record import DeviceRecord
from healer.support.hronos import DateTime
from healer.support.typing import override

logger = logging.getLogger(__name__)


@dataclass
class BasePacketCF350():
    "base type for device packets"

    # must override
    packet_size:int = field(init=False, repr=False)

    # underlying transport buffer
    buffer:bytearray


@dataclass
class RequestPacketCF350(BasePacketCF350):
    "session request packet"

    packet_size = 8


class ResponseIndexCF350:
    "response packet fields offset"

    total_mass = 4  # size=2
    body_fat_pc = 6  # size=2
    skeleton_mass = 8  # size=1
    muscle_mass = 9  # size=2
    viceral_fat = 11  # size=1
    body_water_pc = 12  # size=2
    basal_rate = 14  # size=2
    # conductivity dependent data range
    conductive_start = body_fat_pc
    conductive_finish = 16


@dataclass
class ResponsePacketCF350(BasePacketCF350):
    """
    Session response packet
    """
    packet_size = 16

    @property
    def total_mass(self) -> float:
        "kilogram"
        return struct.unpack_from('>H', self.buffer, ResponseIndexCF350.total_mass)[0] / 10

    @property
    def muscle_mass(self) -> float:
        "kilogram"
        return struct.unpack_from('>H', self.buffer, ResponseIndexCF350.muscle_mass)[0] / 10

    @property
    def skeleton_mass(self) -> float:
        "kilogram"
        return struct.unpack_from('>B', self.buffer, ResponseIndexCF350.skeleton_mass)[0] / 10

    @property
    def body_fat_pc(self) -> float:
        "percent"
        return struct.unpack_from('>H', self.buffer, ResponseIndexCF350.body_fat_pc)[0] / 10

    @property
    def body_water_pc(self) -> float:
        "percent"
        return struct.unpack_from('>H', self.buffer, ResponseIndexCF350.body_water_pc)[0] / 10

    @property
    def basal_rate(self) -> float:
        "kcal"
        return struct.unpack_from('>H', self.buffer, ResponseIndexCF350.basal_rate)[0]

    @property
    def viceral_fat(self) -> float:
        "number 1...60"
        return struct.unpack_from('>B', self.buffer, ResponseIndexCF350.viceral_fat)[0]

    @property
    def has_insulation(self) -> bool:
        "detect bare feet"
        conductive_value_slice = self.buffer[ResponseIndexCF350.conductive_start:ResponseIndexCF350.conductive_finish]
        return all([value_byte == 0 for value_byte in conductive_value_slice])

    def __str__(self):
        return (
            f"ResponsePacket("
            f"total='{self.total_mass}', "
            f"muscle='{self.muscle_mass}', "
            f"skeleton='{self.skeleton_mass}', "
            f"water%='{self.body_water_pc}', "
            f"fat%='{self.body_fat_pc}', "
            f"rate='{self.basal_rate}', "
            f"vfat='{self.viceral_fat}', "
            f")"
        )


class PacketSupportCF350:
    "device packet factory"

    @staticmethod
    def request_packet() -> RequestPacketCF350:
        "fe 02 01 00 b9 35 01 8e"

        # TODO packet format
        buffer = bytearray(RequestPacketCF350.packet_size)

        # magic bytes
        buffer[0] = 0xfe
        buffer[1] = 0x02
        buffer[2] = 0x01
        buffer[3] = 0x00
        buffer[4] = 0xb9
        buffer[5] = 0x35
        buffer[6] = 0x01
        buffer[7] = 0x8e

        packet = RequestPacketCF350(buffer)

        return packet

    @staticmethod
    def response_packet(buffer:bytearray) -> ResponsePacketCF350:
        return ResponsePacketCF350(buffer)


class RecordCF350BT:
    "persisted records"

    @dataclass(frozen=True)
    class Summary(DeviceRecord):
        "measured session data"
        device_codec_guid = 601

        date_time:DateTime

        total_mass:float
        body_fat_pc:float
        skeleton_mass:float
        muscle_mass:float
        viceral_fat:float
        body_water_pc:float
        basal_rate:float

        has_insulation:bool

        mass_unit:str = "kg"
        rate_unit:str = "kcal"

    @dataclass(frozen=True)
    class Buffer(DeviceRecord):
        "measured session data"
        device_codec_guid = 602

        buffer:bytes

    @staticmethod
    def produce_summary(
            packet:ResponsePacketCF350,
            date_time:DateTime=None,
        ) -> RecordCF350BT.Summary:
        date_time = date_time or DateTime.now()
        return RecordCF350BT.Summary(
            date_time=date_time,
            total_mass=packet.total_mass,
            body_fat_pc=packet.body_fat_pc,
            skeleton_mass=packet.skeleton_mass,
            muscle_mass=packet.muscle_mass,
            viceral_fat=packet.viceral_fat,
            body_water_pc=packet.body_water_pc,
            basal_rate=packet.basal_rate,
            has_insulation=packet.has_insulation,
        )

    @staticmethod
    def produce_buffer(
            packet:BasePacketCF350,
    ) -> RecordCF350BT.Buffer:
        return RecordCF350BT.Buffer(
            buffer=bytes(packet.buffer),
        )


@dataclass
class DeviceEasyHomeCF350BT(DeviceBT):
    """
    Easy@Home CF350BT bluetooth body fat scale
    """

    config_entry = 'device/bt/easyhome_cf350bt'

    @override
    def device_description(self) -> str:
        return "Easy@Home CF350BT Bluetooth Body Fat Scale"
