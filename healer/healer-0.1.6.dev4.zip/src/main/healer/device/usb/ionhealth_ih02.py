"""
Device driver for
ION IH02 USB WRIST BLOOD PRESSURE MONITOR
https://www.amazon.ca/IH02-WRIST-BLOOD-PRESSURE-MONITOR/dp/B0057WWZMM
"""

from __future__ import annotations

import enum
import functools
import logging
import struct
from dataclasses import dataclass
from dataclasses import field
from typing import Any
from typing import Callable
from typing import List
from typing import Mapping
from typing import Type

import usb.core
import usb.util

from healer.device.protocol.usb_hid import ControlTransferTraitHID
from healer.device.record import DeviceRecord
from healer.device.usb.arkon import DeviceUSB
from healer.support.hronos import DateTime
from healer.support.typing import WithTypeName
from healer.support.typing import bucket_class_list
from healer.support.typing import cached_method
from healer.support.typing import override

logger = logging.getLogger(__name__)


@enum.unique
class FaceNum(enum.Enum):
    "device usb interfaces"
    hid = 0


@enum.unique
class HidPointAddr(enum.Enum):
    "HID device end point addresses"
    input = 0x83
    output = 0x3


@enum.unique
class PacketGroupIH02(enum.Enum):
    "packet format categories"

    default = 0x51


@enum.unique
class PacketTypeIH02(enum.Enum):
    "packet format layouts"

    device_info = 0x24
    device_date_time = 0x33

    record_date_time = 0x25
    record_measurement = 0x26

    storage_info = 0x2b
    storage_reset = 0x52


class IndexBaseIH02:
    "packet field offset"

    packet_length = 0  # size=1 payload + checksum length
    packet_group = 1  # size=1 packet category
    packet_typer = 2  # size=1 packet type value
    packet_unknown = 7  # size=1 TODO unknonwn
    packet_checksum = 8  # size=1 linear sum of payload

    # payload included in checksum, size=7
    checksum_start = 1  #
    checksum_finish = 8  #


@dataclass
class PacketBaseIH02(WithTypeName):
    "device packet base type"

    # packet meta info
    packet_size:int = field(init=False, repr=False, default=9)  # prefix plus payload size
    packet_type:PacketTypeIH02 = field(init=False, repr=False, default=None)

    # underlying wire buffer
    buffer:bytearray

    def render_buffer(self) -> str:
        return PacketSupportIH02.render_buffer(self.buffer)

    def __str__(self):
        return (
            f"{self.type_name()}("
            f"buffer='{self.render_buffer()}', "
            f"checksum='{self.checksum_hex}', "
            f")"
        )

    @property
    def size(self) -> int:
        return self.buffer[IndexBaseIH02.packet_length]

    @size.setter
    def size(self, length:int) -> int:
        self.buffer[IndexBaseIH02.packet_length] = length

    @property
    def group(self) -> int:
        return self.buffer[IndexBaseIH02.packet_group]

    @group.setter
    def group(self, group:int) -> int:
        self.buffer[IndexBaseIH02.packet_group] = group

    @property
    def typer(self) -> int:
        return self.buffer[IndexBaseIH02.packet_typer]

    @typer.setter
    def typer(self, header:int) -> int:
        self.buffer[IndexBaseIH02.packet_typer] = header

    @property
    def unknown(self) -> int:
        return self.buffer[IndexBaseIH02.packet_unknown]

    @unknown.setter
    def unknown(self, mistery:int) -> int:
        self.buffer[IndexBaseIH02.packet_unknown] = mistery

    @property
    def checksum(self) -> int:  # stored check sum
        return self.buffer[IndexBaseIH02.packet_checksum]

    @checksum.setter
    def checksum(self, checksum:int) -> int:
        self.buffer[IndexBaseIH02.packet_checksum] = checksum

    @property
    def checksum_hex(self) -> str:
        return format(self.checksum, '02x')

    @property
    def payload_checksum(self) -> int:  # stream check sum
        return 0xFF & sum([
            0xFF & item for item in
            self.buffer[IndexDateTimeH02.checksum_start:IndexDateTimeH02.checksum_finish]
        ])

    def assert_length(self) -> None:
        assert len(self.buffer) == self.size + 1, f"invalid buffer length"

    def assert_checksum(self) -> None:
        assert self.checksum == self.payload_checksum, f"invalid buffer checksum"

    def update_checksum(self) -> None:  # set stored check sum to the stream sheck sum
        self.checksum = self.payload_checksum


class IndexDateTimeH02(IndexBaseIH02):
    "field offset for date/time packets"

    clock_moon_diem = 3  # size=1 joint month and day
    clock_year_moon = 4  # size=1 joint year and month
    clock_minute_some = 5  # size=1 joint minute and some
    clock_hour_some = 6  # size=1 joint hour and some


class IndexSensorRequestH02(IndexBaseIH02):
    "field offset for device record packets"

    record_index = 3  # size=2


class IndexStorageStatusIH02(IndexBaseIH02):
    "field offset for storage status packets"

    record_count = 3  # size=2


class IndexSensorMeasurementH02(IndexBaseIH02):
    "field offset for record data packets"

    pressure_systolic = 3  # size=1
    unknown_field = 4  # size=1 unknown field
    pressure_diastolic = 5  # size=1
    heart_rate = 6  # size=1


class PacketTraitIH02:
    "shared packet traits"

    @dataclass
    class WithRequestIndexIH02(PacketBaseIH02):
        "device record request by storage index"

        def with_index(self, index:int) -> None:
            struct.pack_into("<H", self.buffer, IndexSensorRequestH02.record_index, index)

    @dataclass
    class WithDateTimeIH02(PacketBaseIH02):
        "device record with date/time stamp"

        def __str__(self):
            return (
                f"{self.type_name()}("
                f"year='{self.year}', "
                f"moon='{self.moon}', "
                f"diem='{self.diem}', "
                f"hour='{self.hour}', "
                f"minute='{self.minute}', "
                f"checksum='{self.checksum_hex}', "
                f")"
            )

        @property
        def year(self) -> int:
            year_data = self.buffer[IndexDateTimeH02.clock_year_moon] & 0xFE
            year_base = year_data >> 1
            year = year_base + 2000
            assert 2000 <= year and year <= 2099, f"invalid year: {year}"
            return year

        @year.setter
        def year(self, year:int) -> None:
            assert 2000 <= year and year <= 2099, f"invalid year: {year}"
            year_base = year - 2000
            year_data = (year_base << 1)
            moon_upper = self.buffer[IndexDateTimeH02.clock_year_moon] & 0x01
            self.buffer[IndexDateTimeH02.clock_year_moon] = year_data | moon_upper

        @property
        def moon(self) -> int:
            moon_upper = self.buffer[IndexDateTimeH02.clock_year_moon] & 0x01
            moon_lower = self.buffer[IndexDateTimeH02.clock_moon_diem] & 0xE0
            return (moon_upper << 3) | (moon_lower >> 5)

        @moon.setter
        def moon(self, moon:int) -> None:
            moon_upper = (moon >> 3) & 0x01
            moon_lower = (moon << 5) & 0xE0
            year_data = self.buffer[IndexDateTimeH02.clock_year_moon] & 0xFE
            diem_data = self.buffer[IndexDateTimeH02.clock_moon_diem] & 0x1F
            self.buffer[IndexDateTimeH02.clock_year_moon] = year_data | moon_upper
            self.buffer[IndexDateTimeH02.clock_moon_diem] = moon_lower | diem_data

        @property
        def diem(self) -> int:
            diem_data = self.buffer[IndexDateTimeH02.clock_moon_diem] & 0x1F
            diem = diem_data  # no shift
            assert 1 <= diem and diem <= 31, f"wrong day: {diem}"
            return diem

        @diem.setter
        def diem(self, diem:int) -> None:
            assert 1 <= diem and diem <= 31, f"wrong day: {diem}"
            moon_lower = self.buffer[IndexDateTimeH02.clock_moon_diem] & 0xE0
            diem_data = diem  # no shift
            self.buffer[IndexDateTimeH02.clock_moon_diem] = moon_lower | diem_data

        @property
        def hour(self) -> int:
            some_data = self.buffer[IndexDateTimeH02.clock_hour_some] & 0xFE
            hour_data = self.buffer[IndexDateTimeH02.clock_hour_some] & 0x1F
            hour = hour_data  # no shift
            assert 0 <= hour and hour <= 23, f"wrong hour: {hour}"
            return hour

        @hour.setter
        def hour(self, hour:int) -> None:
            assert 0 <= hour and hour <= 23, f"wrong hour: {hour}"
            some_data = self.buffer[IndexDateTimeH02.clock_hour_some] & 0xFE
            hour_data = hour  # no shift
            self.buffer[IndexDateTimeH02.clock_hour_some] = some_data | hour_data

        @property
        def minute(self) -> int:
            some_data = self.buffer[IndexDateTimeH02.clock_minute_some] & 0x80
            minute_data = self.buffer[IndexDateTimeH02.clock_minute_some] & 0x3F
            minute = minute_data
            assert 0 <= minute and minute <= 59, f"wrong minute: {minute}"
            return minute

        @minute.setter
        def minute(self, minute:int) -> None:
            assert 0 <= minute and minute <= 59, f"wrong minute: {minute}"
            some_data = self.buffer[IndexDateTimeH02.clock_minute_some] & 0x80
            minute_data = minute
            self.buffer[IndexDateTimeH02.clock_minute_some] = some_data | minute_data

        @property
        def date_time(self) -> DateTime:
            return DateTime(
                year=self.year,
                month=self.moon,
                day=self.diem,
                hour=self.hour,
                minute=self.minute,
            )

        @date_time.setter
        def date_time(self, instant:DateTime) -> None:
            self.year = instant.year
            self.moon = instant.month
            self.diem = instant.day
            self.hour = instant.hour
            self.minute = instant.minute


class BucketIH02:
    "device packet collection"

    @dataclass
    class PacketDeviceInfoIH02(PacketBaseIH02):
        "device status packet"
        packet_type = PacketTypeIH02.device_info

    @dataclass
    class PacketStorageInfoIH02(PacketBaseIH02):
        "storage status packet"
        packet_type = PacketTypeIH02.storage_info

        @property
        def record_count(self) -> int:
            record_count = self.buffer[IndexStorageStatusIH02.record_count]
            assert record_count >= 0, f"wrong record count: {record_count}"
            return record_count

        def __str__(self):
            return (
                f"{self.type_name()}("
                f"count='{self.record_count}', "
                f")"
            )

    @dataclass
    class PacketStorageResetIH02(PacketBaseIH02):
        "storage wipeout packet"
        packet_type = PacketTypeIH02.storage_reset

    @dataclass
    class PacketDateTimeIH02(PacketTraitIH02.WithDateTimeIH02):
        "device clock sync packet"
        packet_type = PacketTypeIH02.device_date_time

    @dataclass
    class PacketRecordDateTimeIH02(PacketTraitIH02.WithRequestIndexIH02, PacketTraitIH02.WithDateTimeIH02):
        "device record time stamp packet"
        packet_type = PacketTypeIH02.record_date_time

    @dataclass
    class PacketRecordMeasurementIH02(PacketTraitIH02.WithRequestIndexIH02):
        "device record blood pressure and hear rate packet"
        packet_type = PacketTypeIH02.record_measurement

        @property
        def pressure_systolic(self) -> int:
            return self.buffer[IndexSensorMeasurementH02.pressure_systolic]

        @property
        def pressure_diastolic(self) -> int:
            return self.buffer[IndexSensorMeasurementH02.pressure_diastolic]

        @property
        def heart_rate(self) -> int:
            return self.buffer[IndexSensorMeasurementH02.heart_rate]

        def __str__(self):
            return (
                f"{self.type_name()}("
                f"systolic='{self.pressure_systolic}', "
                f"diastolic='{self.pressure_diastolic}', "
                f"pulse='{self.heart_rate}', "
                f")"
            )


class PacketSupportIH02:
    "device packet factory"

    @staticmethod
    def render_buffer(buffer:bytearray) -> str:
        return ' '.join(format(x, '02x') for x in buffer)

    @staticmethod
    @functools.lru_cache(maxsize=1)
    def packet_mapper() -> Mapping[PacketTypeIH02, Type[PacketBaseIH02]]:
        class_list = bucket_class_list(BucketIH02, PacketBaseIH02)
        select_list = map(lambda message_class: (message_class.packet_type, message_class), class_list)
        return dict(select_list)

    @staticmethod
    def packet_class_from(packet_type:PacketTypeIH02) -> Type[PacketBaseIH02]:
        message_class = PacketSupportIH02.packet_mapper().get(packet_type)
        return message_class

    @staticmethod
    def packet_from_type(packet_type:PacketTypeIH02) -> PacketBaseIH02:
        message_class = PacketSupportIH02.packet_class_from(packet_type)
        packet_size = message_class.packet_size
        buffer = bytearray(packet_size)
        packet = message_class(buffer)
        packet.size = packet_size - 1
        packet.group = PacketGroupIH02.default.value
        packet.typer = packet_type.value
        packet.unknown = 0xa3  # TODO unknown field
        return packet

    @staticmethod
    def packet_from_buffer(buffer:bytearray) -> PacketBaseIH02:
        assert len(buffer) == PacketBaseIH02.packet_size, f"invalid buffer size: {buffer}"
        typer = buffer[IndexBaseIH02.packet_typer]
        packet_type = PacketTypeIH02(typer)
        message_class = PacketSupportIH02.packet_class_from(packet_type)
        packet = message_class(buffer)
        packet.assert_length()
        packet.assert_checksum()
        return packet

    @staticmethod
    def produce_device_info() -> BucketIH02.PacketDeviceInfoIH02:
        return PacketSupportIH02.packet_from_type(PacketTypeIH02.device_info)

    @staticmethod
    def produce_date_time() -> BucketIH02.PacketDateTimeIH02:
        return PacketSupportIH02.packet_from_type(PacketTypeIH02.device_date_time)

    @staticmethod
    def produce_record_date_time() -> BucketIH02.PacketRecordDateTimeIH02:
        return PacketSupportIH02.packet_from_type(PacketTypeIH02.record_date_time)

    @staticmethod
    def produce_record_measurement() -> BucketIH02.PacketRecordMeasurementIH02:
        return PacketSupportIH02.packet_from_type(PacketTypeIH02.record_measurement)

    @staticmethod
    def produce_storage_info() -> BucketIH02.PacketStorageInfoIH02:
        return PacketSupportIH02.packet_from_type(PacketTypeIH02.storage_info)

    @staticmethod
    def produce_storage_reset() -> BucketIH02.PacketStorageResetIH02:
        return PacketSupportIH02.packet_from_type(PacketTypeIH02.storage_reset)


class RecordIH02:

    @dataclass(frozen=True)
    class Summary(DeviceRecord):
        "persisted device record"

        device_codec_guid = 401

        record_count:int

    @dataclass(frozen=True)
    class Result(DeviceRecord):
        "persisted device record"

        device_codec_guid = 402

        date_time:DateTime
        pressure_systolic:int
        pressure_diastolic:int
        heart_rate:int

        pressure_unit:str = "mmHg"
        heart_rate_unit:str = "beat/min"


class SensorSupportIH02:
    """
    """

    @staticmethod
    def defaut_react_record(record: RecordIH02.Result) -> None:
        print(record)


@dataclass
class DeviceIonHealthIH02(ControlTransferTraitHID, DeviceUSB):
    """
    Wrist Blood Pressure Monitor
    https://www.amazon.ca/IH02-WRIST-BLOOD-PRESSURE-MONITOR/dp/B0057WWZMM
    """
    config_entry = 'device/usb/ionhealth_ih02'

    # buffer for input stream
    input_stream:bytearray = field(repr=False, default=None)

    @override
    def start(self) -> None:
        super().start()
        self.input_stream = bytearray()
        self.hid_start()

    @override
    def stop(self) -> None:
        self.hid_stop()
        super().stop()

    def hid_start(self) -> None:
        "magic setup sequence"
        self.hid_get_report(wIndex=0, wValue=0x0346,)
        self.hid_set_report(wIndex=0, wValue=0x0341, report=bytearray([0x41, 0x01]))

    def hid_stop(self) -> None:
        pass

    @cached_method
    def face_hid(self) -> usb.core.Interface:
        return self.select_face(FaceNum.hid)

    @cached_method
    def point_hid_input(self) -> usb.core.Endpoint:
        return self.select_point(self.face_hid(), HidPointAddr.input)

    @cached_method
    def point_hid_output(self) -> usb.core.Endpoint:
        return self.select_point(self.face_hid(), HidPointAddr.output)

    def hid_get(self) -> None:
        "receive input into hid stream, build incoming packet"
        point = self.point_hid_input()
        buffer = self.pyusb_device.read(
            point.bEndpointAddress, point.wMaxPacketSize, self.timeout()
        )
        assert len(buffer) > 0, f"hid_get empty buffer"
        size = buffer[0]  # get chunk size
        data = buffer[1:size + 1]  # split chunk data
        if not self.input_stream:  # ensure byte array of size=1
            self.input_stream = bytearray(1)
        self.input_stream[0] += size  # first byte is packet size collector
        self.input_stream += data  # input stream is packet bytes collector
        render = PacketSupportIH02.render_buffer(buffer)
        logger.trace(f"hid_get: {render}")

    def hid_put(self, buffer:bytearray) -> None:
        "transmit output into hid device"
        point = self.point_hid_output()
        assert len(buffer) > 0, f"hid_put empty buffer"
        size = buffer[0]  # get payload size
        assert len(buffer) == size + 1  , f"wrong packet format"
        render = PacketSupportIH02.render_buffer(buffer)
        logger.trace(f"hid_put: {render}")
        assert len(buffer) <= point.wMaxPacketSize, f"wrong buffer: {buffer}"
        self.pyusb_device.write(
            point.bEndpointAddress, buffer, self.timeout()
        )

    def packet_read(self) -> PacketBaseIH02:
        "extract packet from the stream"
        size = PacketBaseIH02.packet_size  # expect payload size
        while len(self.input_stream) < size:
            self.hid_get()
        buffer = self.input_stream[0:size]  # split packet
        self.input_stream = self.input_stream[size:]  # consume stream
        packet = PacketSupportIH02.packet_from_buffer(buffer)
        return packet

    def packet_write(self, packet: PacketBaseIH02):
        "transmit packet to device"
        packet.update_checksum()
        self.hid_put(packet.buffer)

    def read_device_status(self) -> BucketIH02.PacketDeviceInfoIH02:
        "extract TODO"
        request_packet = PacketSupportIH02.produce_device_info()
        self.packet_write(request_packet)
        response_packet = self.packet_read()
        assert isinstance(response_packet, BucketIH02.PacketDeviceInfoIH02), f"wrong packet type"
        return response_packet

    def read_storage_status(self) -> BucketIH02.PacketStorageInfoIH02:
        "extract record count"
        request_packet = PacketSupportIH02.produce_storage_info()
        self.packet_write(request_packet)
        response_packet = self.packet_read()
        assert isinstance(response_packet, BucketIH02.PacketStorageInfoIH02), f"wrong packet type"
        return response_packet

    def read_record_date_time(self, index:int) -> BucketIH02.PacketRecordDateTimeIH02:
        "extract date/time at the index"
        request_date_time = PacketSupportIH02.produce_record_date_time()
        request_date_time.with_index(index)
        self.packet_write(request_date_time)
        response_date_time = self.packet_read()
        assert isinstance(response_date_time, BucketIH02.PacketRecordDateTimeIH02), f"wrong packet type"
        return response_date_time

    def read_record_measurement(self, index:int) -> BucketIH02.PacketRecordMeasurementIH02:
        "extract pressure/rate at the index"
        request_measurement = PacketSupportIH02.produce_record_measurement()
        request_measurement.with_index(index)
        self.packet_write(request_measurement)
        response_measurement = self.packet_read()
        assert isinstance(response_measurement, BucketIH02.PacketRecordMeasurementIH02), f"wrong packet type"
        return response_measurement

    def read_device_record(self, index:int) -> RecordIH02.Result:
        "produce single record from several packets"
        record_date_time = self.read_record_date_time(index)
        record_measurement = self.read_record_measurement(index)
        device_record = RecordIH02.Result(
            date_time=record_date_time.date_time,
            pressure_systolic=record_measurement.pressure_systolic,
            pressure_diastolic=record_measurement.pressure_diastolic,
            heart_rate=record_measurement.heart_rate,
        )
        return device_record

    def read_record_stream(self,
            react_record:Callable[[RecordIH02.Result], Any]=SensorSupportIH02.defaut_react_record,
        ) -> None:
        "iterate all stored device records"
        storage_status = self.read_storage_status()
        record_count = storage_status.record_count
        for index in reversed(range(record_count)):  # reversed to restore date/time sort
            device_record = self.read_device_record(index)
            react_record(device_record)

    def write_device_clock(self, instant:DateTime) -> BucketIH02.PacketDateTimeIH02:
        "ensure device timer"
        request_date_time = PacketSupportIH02.produce_date_time()
        request_date_time.date_time = instant
        self.packet_write(request_date_time)
        response_date_time = self.packet_read()
        assert isinstance(response_date_time, BucketIH02.PacketDateTimeIH02), f"wrong packet type"
        return response_date_time

    def issue_storage_reset(self) -> BucketIH02.PacketStorageResetIH02:
        "remove device records"
        request_packet = PacketSupportIH02.produce_storage_reset()
        self.packet_write(request_packet)
        response_packet = self.packet_read()
        assert isinstance(response_packet, BucketIH02.PacketStorageResetIH02), f"wrong packet type"
        return response_packet

    def check_setup(self) -> bool:
        "verify device is powered up"
        try:
            self.read_device_status()
            return True
        except usb.core.USBError as error:
            if error.errno == 110:
                "[Errno 110] Operation timed out"
                return False
            else:
                raise error

    @override
    def device_identity(self) -> str:
        "ion health uses running serial number, and no user configurable device id"
        return super().device_identity()

    @override
    def device_description(self) -> str:
        return "Ion Health IH02 USB Wrist Blood Pressure Monitor"
