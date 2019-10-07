"""
Device driver for
Wrist Pulse Oximeter
https://www.concordhealthsupply.com/Wrist-Oximeter-p/75006.htm
"""

from __future__ import annotations

import abc
import array
import enum
import functools
import logging
import time
from dataclasses import dataclass
from dataclasses import field
from typing import Callable
from typing import List
from typing import Mapping
from typing import Type

import usb.core
import usb.util

from healer.config import CONFIG
from healer.device.protocol.usb_CP210X import SerialCP210XTrait
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
class PacketTypeCMS(enum.Enum):
    "packet format types"

    device_id = 0x04  # user configurable device identity
    device_ready = 0x0C
    device_model = 0x02
    device_brand = 0x03
    device_notice = 0x11
    device_disconnect = 0x0D

    user_count = 0x10  # number of device users
    user_comment = 0x05  # user account comment

    segment_meta = 0x15  # TODO
    segment_count = 0x0A  # number of stored segments
    segment_date = 0x07  # stored segment start date
    segment_time = 0x12  # stored segment start time
    segment_size = 0x08  # segment record count (not packet count)

    stream_data = 0x01  # real-time data record

    stored_data = 0x09  # stored single data record
    stored_bucket = 0x0F  # stored triple data record

    response_code = 0x0B  # command success/failure status

    control_command = 0x7D  # packet with command control byte


@enum.unique
class ControlTypeCMS(enum.Enum):
    "control command types"

    query_device_id = 0xAA  # -> 0x04
    query_device_brand = 0xA9
    query_device_model = 0xA8
    query_device_notice = 0xB0

    issue_device_ping = 0xAF

    query_stream_pi_support = 0xAC

    issue_stream_start = 0xA1  # -> 0x01; start real time feed
    issue_stream_abort = 0xA2  # -> 0x0C; cancel real time feed

    query_segment_count = 0xA3  # -> 0x0A; segment count
    query_segment_meta = 0xB6  # -> 0x15; segment context # TODO
    query_segment_size = 0xA4  # -> 0x08; segment record count
    query_segment_stamp = 0xA5  # -> 0x07,0x12; segment date/time stamp

    issue_stored_start = 0xA6  # -> 0x09|0x0F; start stored data feed
    issue_stored_abort = 0xA7  # -> 0x0C; cancel stored data feed
    issue_stored_erase = 0xAE  # -> 0x0B; delete stored segment

    query_user_count = 0xAD  # -> 0x10; number of device users
    query_user_comment = 0xAB  # -> 0x05; user configurable comment

    write_device_date = 0xB2  # -> 0x0B; write device date
    wirte_device_time = 0xB1  # -> 0x0B; write device time


class RecordCMS:
    "persisted device records"

    @dataclass(frozen=True)
    class Summary(DeviceRecord):
        "segment summary"

        device_codec_guid = 301

        user:int
        segment:int
        record_count:int
        date_time:DateTime

    @dataclass(frozen=True)
    class Result(DeviceRecord):
        "stored sensor data point"

        device_codec_guid = 302

        seq:int  # entry sequence number
        O2:int  # partial oxygen pressure
        PR:int  # heart pulse rate


@enum.unique
class ResponseCode(enum.Enum):
    "command response codes"

    success = 0x00
    state_power_off = 0x01
    state_user_change = 0x02
    state_recording_mode = 0x03
    failure_store_erase = 0x04
    failure_unsupported = 0x05
    failure_unknown_reason = 0xFF


@dataclass
class PacketCMS(WithTypeName):
    "device packet base type"

    # packet meta info
    packet_size:int = field(init=False)
    packet_type:PacketTypeCMS = field(init=False)

    # uderlying device data buffer
    buffer:array

    def __str__(self) -> str:
        return f"{self.type_name()}({self.render_buffer()})"

    def render_buffer(self) -> str:
        return BufferSupportCMS.format_hex2(self.buffer)

    def control_type(self) -> ControlTypeCMS:
        return ControlTypeCMS(self.buffer[0])


class PacketSupportCMS:
    "packet factory"

    @staticmethod
    def control_packet(control_type:ControlTypeCMS, *args) -> PacketCMS:
        "produce control packet"
        buffer = BufferSupportCMS.packet_buffer(9)
        buffer[0] = PacketTypeCMS.control_command.value
        buffer[1] = 0x81  # requriered prefix
        buffer[2] = control_type.value
        assert len(args) <= 6, f"too many args: {args}"
        index = 0
        for _ in args:
            value = args[index]
            assert value & 0x7F == value, f"need value 0x7F: {value}"
            buffer[3 + index] = 0x80 | value
            index += 1
        return PacketCMS(buffer)

    @staticmethod
    def regular_packet(message_class:Type[PacketCMS]) -> PacketCMS:
        "produce payload packet"
        packet_type = message_class.packet_type
        packet_size = message_class.packet_size
        buffer = BufferSupportCMS.packet_buffer(packet_size)
        buffer[0] = packet_type.value
        packet = message_class(buffer)
        return packet

    @staticmethod
    def format_hex2(value:int) -> str:
        return '{:02x}'.format(value).upper()

    @staticmethod
    def format_int2(value:int) -> str:
        return '{:02d}'.format(value).upper()

    @staticmethod
    def mask_7bit(value:int) -> int:
        return value & 0x7F

    @staticmethod
    def string_decode(buffer:array, start:int) -> str:
        assert 0 <= start and start < len(buffer), f"Wrong start: {start}"
        bucket = bytearray()
        for entry in buffer[start:]:
            if entry == 0x80:
                continue
            bucket.append(entry & 0x7F)
        return bucket.decode().strip()

    @staticmethod
    def string_encode(buffer:array, start:int, string:str) -> None:
        assert 0 <= start and start < len(buffer), f"Wrong start: {start}"
        bucket = string.encode('ascii')
        assert len(bucket) <= len(buffer) - start, f"Too long string: {string}"
        index = 0
        for _ in range(len(bucket)):
            buffer[index + start] = bucket[index] | 0x80
            index += 1

    @dataclass
    class With_User(PacketCMS):
        "extract user index"

        def user(self) -> int:
            return PacketSupportCMS.mask_7bit(self.buffer[2])

        def render_buffer(self) -> str:
            return f"user='{self.user()}'"

    @dataclass
    class With_Comment(PacketCMS):

        def comment(self) -> str:
            return PacketSupportCMS.string_decode(self.buffer, 3)

        def render_buffer(self) -> str:
            return f"comment={repr(self.comment())}"

    @dataclass
    class With_UserSegment(With_User):
        "extract user index and segment index"

        def segment(self) -> int:
            return PacketSupportCMS.mask_7bit(self.buffer[3])

        def render_buffer(self) -> str:
            return f"{super().render_buffer()}, segment='{self.segment()}'"

    @dataclass
    class With_ValueString(PacketCMS):

        def value(self) -> str:
            return PacketSupportCMS.string_decode(self.buffer, 2)

        def value_inject(self, string:str) -> None:
            PacketSupportCMS.string_encode(self.buffer, 2, string)

        def render_buffer(self) -> str:
            return f"value={repr(self.value())}"


class BufferSupportCMS:
    "packet buffer factory"

    @staticmethod
    def packet_buffer(size:int) -> array:
        buffer = usb.util.create_buffer(size)
        for index in range(size):
            buffer[index] = 0x80
        return buffer

    @staticmethod
    def buffer_merge(*buffer_list:array) -> array:
        result = bytearray(0)
        for buffer in buffer_list:
            result.extend(buffer)
        return result

    @staticmethod
    def packet_merge(*packet_list:PacketCMS) -> array:
        result = bytearray(0)
        for packet in packet_list:
            result.extend(packet.buffer)
        return PacketCMS(result)

    @staticmethod
    def format_hex2(buffer:array) -> str:
        render = lambda byte: PacketSupportCMS.format_hex2(byte)
        return " ".join(map(render, buffer))


class ControlPacketCMS:
    "control packet factory"

    @staticmethod
    def issue_stream_start() -> PacketCMS:
        return PacketSupportCMS.control_packet(ControlTypeCMS.issue_stream_start)

    @staticmethod
    def issue_stream_abort() -> PacketCMS:
        return PacketSupportCMS.control_packet(ControlTypeCMS.issue_stream_abort)

    @staticmethod
    def query_stream_pi_support() -> PacketCMS:
        return PacketSupportCMS.control_packet(ControlTypeCMS.query_stream_pi_support)

    @staticmethod
    def issue_stored_start(user:int, segment:int) -> PacketCMS:
        return PacketSupportCMS.control_packet(ControlTypeCMS.issue_stored_start, user, segment)

    @staticmethod
    def issue_stored_abort() -> PacketCMS:
        return PacketSupportCMS.control_packet(ControlTypeCMS.issue_stored_abort)

    @staticmethod
    def issue_stored_erase(user:int, segment:int) -> PacketCMS:
        return PacketSupportCMS.control_packet(ControlTypeCMS.issue_stored_erase, user, segment)

    @staticmethod
    def query_segment_meta(user:int, segment:int) -> PacketCMS:
        return PacketSupportCMS.control_packet(ControlTypeCMS.query_segment_meta, user, segment)

    @staticmethod
    def query_segment_count(user:int, count:int=0) -> PacketCMS:
        return PacketSupportCMS.control_packet(ControlTypeCMS.query_segment_count, user, count)

    @staticmethod
    def query_segment_size(user:int, segment:int) -> PacketCMS:
        return PacketSupportCMS.control_packet(ControlTypeCMS.query_segment_size, user, segment)

    @staticmethod
    def query_segment_stamp(user:int, segment:int) -> PacketCMS:
        return PacketSupportCMS.control_packet(ControlTypeCMS.query_segment_stamp, user, segment)

    @staticmethod
    def issue_device_id(identity:str) -> PacketCMS:
        packet = PacketSupportCMS.regular_packet(RegularPacketCMS.PacketDeviceId)
        packet.value_inject(identity)
        return packet

    @staticmethod
    def query_device_id() -> PacketCMS:
        return PacketSupportCMS.control_packet(ControlTypeCMS.query_device_id)

    @staticmethod
    def issue_device_ping() -> PacketCMS:
        return PacketSupportCMS.control_packet(ControlTypeCMS.issue_device_ping)

    @staticmethod
    def query_device_brand() -> PacketCMS:
        return PacketSupportCMS.control_packet(ControlTypeCMS.query_device_brand)

    @staticmethod
    def query_device_model() -> PacketCMS:
        return PacketSupportCMS.control_packet(ControlTypeCMS.query_device_model)

    @staticmethod
    def query_user_comment(user:int) -> PacketCMS:
        return PacketSupportCMS.control_packet(ControlTypeCMS.query_user_comment, user)

    @staticmethod
    def query_user_count() -> PacketCMS:
        return PacketSupportCMS.control_packet(ControlTypeCMS.query_user_count)

    @staticmethod
    def query_device_notice() -> PacketCMS:
        return PacketSupportCMS.control_packet(ControlTypeCMS.query_device_notice)

    @staticmethod
    def write_device_date(year_hi:int, year_lo:int, month:int, day:int, week_day:int) -> PacketCMS:
        return PacketSupportCMS.control_packet(
            ControlTypeCMS.write_device_date, year_hi, year_lo, month, day, week_day,
        )

    @staticmethod
    def wirte_device_time(hour:int, minute:int, second:int) -> PacketCMS:
        return PacketSupportCMS.control_packet(
            ControlTypeCMS.wirte_device_time, hour, minute, second,
        )


class RegularPacketCMS:
    "regular packet factory"

    @dataclass
    class PacketDeviceId(PacketSupportCMS.With_ValueString):
        packet_size = 9
        packet_type = PacketTypeCMS.device_id

    @dataclass
    class PacketDeviceReady(PacketCMS):
        packet_size = 2
        packet_type = PacketTypeCMS.device_ready

        def render_buffer(self) -> str:
            return ""

    @dataclass
    class PacketDeviceDisconnect(PacketCMS):
        packet_size = 3
        packet_type = PacketTypeCMS.device_disconnect

        def response(self) -> int:
            return PacketSupportCMS.mask_7bit(self.buffer[2])

        def response_code(self) -> ResponseCode:
            return ResponseCode(self.response())

        def render_buffer(self) -> str:
            response = self.response_code().name
            return f"response='{response}'"

    @dataclass
    class PacketDeviceNotice(PacketSupportCMS.With_ValueString):
        packet_size = 9
        packet_type = PacketTypeCMS.device_notice

        def notice(self) -> int:
            return PacketSupportCMS.mask_7bit(self.buffer[1])

        def render_buffer(self) -> str:
            return f"notice='{self.notice()}', {super().render_buffer()}"

    @dataclass
    class PacketDeviceBrand(PacketSupportCMS.With_Comment):
        packet_size = 9
        packet_type = PacketTypeCMS.device_brand

    @dataclass
    class PacketDeviceModel(PacketSupportCMS.With_Comment):
        packet_size = 9
        packet_type = PacketTypeCMS.device_model

    @dataclass
    class PacketStreamData(PacketCMS):
        packet_size = 9
        packet_type = PacketTypeCMS.stream_data

    @dataclass
    class PacketStoredData(PacketCMS):
        "contains single data point"  # TODO
        packet_size = 6
        packet_type = PacketTypeCMS.stored_data

        data_size = 1  # contains single data point

    @dataclass
    class PacketStoredBucket(PacketCMS):
        "contains three data points"
        packet_size = 8
        packet_type = PacketTypeCMS.stored_bucket

        data_size = 3  # contains three data points

        def oxygen_level(self, index:int) -> int:
            assert 0 <= index and index < self.data_size, f"wrong index: {index}"
            return PacketSupportCMS.mask_7bit(self.buffer[2 + index * 2])

        def pulse_rate(self, index:int) -> int:
            assert 0 <= index and index < self.data_size, f"wrong index: {index}"
            return PacketSupportCMS.mask_7bit(self.buffer[3 + index * 2])

        def render_buffer(self) -> str:
            render = ""
            for index in range(self.data_size):
                oxygen = self.oxygen_level(index)
                pulse = self.pulse_rate(index)
                render += f"{{O2={oxygen},PR={pulse}}},"
            return render

        def data_list(self, sequence:int) -> List[RecordCMS.Result]:
            return[
                RecordCMS.Result(seq=sequence + 0, O2=self.oxygen_level(0), PR=self.pulse_rate(0)),
                RecordCMS.Result(seq=sequence + 1, O2=self.oxygen_level(1), PR=self.pulse_rate(1)),
                RecordCMS.Result(seq=sequence + 2, O2=self.oxygen_level(2), PR=self.pulse_rate(2)),
            ]

    @dataclass
    class PacketResponseCode(PacketCMS):
        packet_size = 4
        packet_type = PacketTypeCMS.response_code

        def command(self) -> int:
            return self.buffer[2]

        def command_type(self) -> ControlTypeCMS:
            return ControlTypeCMS(self.command())

        def response(self) -> int:
            return PacketSupportCMS.mask_7bit(self.buffer[3])

        def response_code(self) -> ResponseCode:
            return ResponseCode(self.response())

        def render_buffer(self) -> str:
            command = self.command_type().name
            response = self.response_code().name
            return f"command='{command}', response='{response}'"

    @dataclass
    class PacketUserCount(PacketCMS):
        packet_size = 3
        packet_type = PacketTypeCMS.user_count

        def count(self) -> int:
            return PacketSupportCMS.mask_7bit(self.buffer[2])

        def render_buffer(self) -> str:
            return f"count='{self.count()}'"

    @dataclass
    class PacketUserComment(PacketSupportCMS.With_User):
        packet_size = 9
        packet_type = PacketTypeCMS.user_comment

        def comment(self) -> str:
            return PacketSupportCMS.string_decode(self.buffer, 3)

        def render_buffer(self) -> str:
            return f"{super().render_buffer()}, comment={repr(self.comment())}"

    @dataclass
    class PacketSegmentCount(PacketSupportCMS.With_User):
        packet_size = 4
        packet_type = PacketTypeCMS.segment_count

        def count(self) -> int:
            return PacketSupportCMS.mask_7bit(self.buffer[3])

        def render_buffer(self) -> str:
            return f"{super().render_buffer()}, count='{self.count()}'"

    @dataclass
    class PacketSegmentMeta(PacketSupportCMS.With_UserSegment):
        packet_size = 9
        packet_type = PacketTypeCMS.segment_meta

        def pi_id(self) -> int:
            return PacketSupportCMS.mask_7bit(self.buffer[3])

        def reten(self) -> int:
            return PacketSupportCMS.mask_7bit(self.buffer[4])

        def render_buffer(self) -> str:
            return f"{super().render_buffer()}, pi_id='{self.pi_id()}', reten='{self.reten()}'"

    @dataclass
    class PacketSegmentDate(PacketSupportCMS.With_UserSegment):
        packet_size = 8
        packet_type = PacketTypeCMS.segment_date

        def segment_date(self) -> str:
            year_hi = PacketSupportCMS.mask_7bit(self.buffer[4])
            year_lo = PacketSupportCMS.mask_7bit(self.buffer[5])
            year = (year_hi * 100) + year_lo
            month = PacketSupportCMS.format_int2(PacketSupportCMS.mask_7bit(self.buffer[6]))
            day = PacketSupportCMS.format_int2(PacketSupportCMS.mask_7bit(self.buffer[7]))
            return f"{year}-{month}-{day}"

        def render_buffer(self) -> str:
            return f"{super().render_buffer()}, date='{self.segment_date()}'"

    @dataclass
    class PacketSegmentTime(PacketSupportCMS.With_UserSegment):
        packet_size = 8
        packet_type = PacketTypeCMS.segment_time

        def segment_time(self) -> str:
            hour = PacketSupportCMS.format_int2(PacketSupportCMS.mask_7bit(self.buffer[4]))
            minute = PacketSupportCMS.format_int2(PacketSupportCMS.mask_7bit(self.buffer[5]))
            second = PacketSupportCMS.format_int2(PacketSupportCMS.mask_7bit(self.buffer[6]))
            return f"{hour}:{minute}:{second}"

        def render_buffer(self) -> str:
            return f"{super().render_buffer()}, time='{self.segment_time()}'"

    @dataclass
    class PacketSegmentSize(PacketSupportCMS.With_UserSegment):
        packet_size = 8
        packet_type = PacketTypeCMS.segment_size

        def entry_count(self) -> int:  # note: subject to factor adjustment
            buffer = bytes(map(PacketSupportCMS.mask_7bit, self.buffer))
            upper = buffer[1]  # upper bits for each data byte
            byte0 = ((upper & 0x04) << 5) | buffer[4]
            byte1 = ((upper & 0x08) << 4) | buffer[5]
            byte2 = ((upper & 0x10) << 3) | buffer[6]
            byte3 = ((upper & 0x20) << 2) | buffer[7]
            value = (byte3 << 24) | (byte2 << 16) | (byte1 << 8) | (byte0 << 0)
            return value

        def render_buffer(self) -> str:
            return f"{super().render_buffer()}, length='{self.entry_count()}'"

    @staticmethod
    @functools.lru_cache(maxsize=1)
    def packet_mapper() -> Mapping[PacketTypeCMS, Type[PacketCMS]]:
        class_list = bucket_class_list(RegularPacketCMS, PacketCMS)
        select_list = map(lambda message_class: (message_class.packet_type, message_class), class_list)
        return dict(select_list)

    @staticmethod
    def packet_class_from(typer:int) -> Type[PacketCMS]:
        packet_type = PacketTypeCMS(typer)
        message_class = RegularPacketCMS.packet_mapper().get(packet_type)
        return message_class


class CommandCMS50F(abc.ABC):
    "high level device commands"

    @abc.abstractmethod
    def packet_read(self) -> PacketCMS:
        "receive packet from device"

    @abc.abstractmethod
    def packet_write(self, packet:PacketCMS, use_flush:bool=False, delay:float=0.2) -> None:
        "transmit packet into device"

    def check_setup(self) -> bool:
        "verify device is powered up"
        try:
            self.perform_setup()
            return True
        except usb.core.USBError as error:
            if error.errno == 110:
                "[Errno 110] Operation timed out"
                return False
            else:
                raise error

    def perform_setup(self) -> None:
        "reset the device; fails when device is connected but is powered down"
        self.packet_write(ControlPacketCMS.issue_stream_abort())
        self.packet_read()
        self.packet_write(ControlPacketCMS.issue_stored_abort())
        self.packet_read()

    def issue_stream_abort(self) -> None:
        "terminate streaming real time data, if active"
        self.packet_write(ControlPacketCMS.issue_stream_abort(), use_flush=True, delay=0.5)
        self.serial_clear_pending_input()

    def issue_stored_abort(self) -> None:
        "terminate streaming stored data, if active"
        self.packet_write(ControlPacketCMS.issue_stored_abort(), use_flush=True, delay=0.5)
        self.serial_clear_pending_input()

    def issue_device_ping(self) -> None:
        "verify device is powerd up and responding"
        self.packet_write(ControlPacketCMS.issue_device_ping())

    def query_device_id(self) -> str:
        "extract user configurable device identity"
        self.packet_write(ControlPacketCMS.query_device_id())
        packet = self.packet_read()
        assert packet.packet_type == PacketTypeCMS.device_id
        return packet.value()

    def issue_device_id(self, identity:str) -> None:
        "persist user configurable device identity"
        self.packet_write(ControlPacketCMS.issue_device_id(identity=identity))
        packet = self.packet_read()
        assert packet.packet_type == PacketTypeCMS.device_id
        assert packet.value() == identity

    def query_device_notice(self) -> int:
        self.packet_write(ControlPacketCMS.query_device_notice())
        packet = self.packet_read()
        assert packet.packet_type == PacketTypeCMS.device_notice
        return packet.notice()

    def query_user_count(self) -> int:
        self.packet_write(ControlPacketCMS.query_user_count())
        packet = self.packet_read()
        assert packet.packet_type == PacketTypeCMS.user_count
        return packet.count()

    def query_user_comment(self, user:int) -> str:
        self.packet_write(ControlPacketCMS.query_user_comment(user=user))
        packet = self.packet_read()
        assert packet.packet_type == PacketTypeCMS.user_comment
        assert packet.user() == user
        return packet.comment()

    def query_segment_count(self, user:int) -> int:
        self.packet_write(ControlPacketCMS.query_segment_count(user=user))
        packet = self.packet_read()
        assert packet.packet_type == PacketTypeCMS.segment_count
        assert packet.user() == user
        return packet.count()

    def query_segment_meta(self, user:int, segment:int) -> RegularPacketCMS.PacketSegmentMeta:
        raise RuntimeError(f"TODO")
        self.packet_write(ControlPacketCMS.query_segment_meta(user=user, segment=segment))
        return self.packet_read()

    @classmethod
    def segment_length_factor(cls) -> float:
        "adjustment for segment entry count"
        return float(CONFIG[cls.config_entry]['segment_length_factor'])

    def query_segment_size(self, user:int, segment:int) -> int:
        "extract number of stored records or number of per-second data smples"
        self.packet_write(ControlPacketCMS.query_segment_size(user=user, segment=segment))
        packet = self.packet_read()
        assert packet.packet_type == PacketTypeCMS.segment_size
        assert packet.user() == user
        assert packet.segment() == segment
        return int(packet.entry_count() * self.segment_length_factor())

    def write_device_clock(self, instant:DateTime) -> None:
        "setup device date and time"
        year_hi = int(instant.year / 100)
        year_lo = int(instant.year % 100)
        week_day = instant.isoweekday()  # Monday is 1 and Sunday is 7
        if week_day == 7:
            week_day = 0  # device week day sequence
        self.packet_write(ControlPacketCMS.write_device_date(year_hi, year_lo, instant.month, instant.day, week_day))
        packet = self.packet_read()
        assert packet.packet_type == PacketTypeCMS.response_code
        assert packet.response_code() == ResponseCode.success
        self.packet_write(ControlPacketCMS.wirte_device_time(instant.hour, instant.minute, instant.second))
        packet = self.packet_read()
        assert packet.packet_type == PacketTypeCMS.response_code
        assert packet.response_code() == ResponseCode.success

    def query_segment_stamp(self, user:int, segment:int) -> DateTime:
        "extract date/time of user/segment recording"
        self.packet_write(ControlPacketCMS.query_segment_stamp(user=user, segment=segment))
        packet_date:PacketSegmentDate = self.packet_read()
        packet_time:PacketSegmentTime = self.packet_read()
        assert packet_date.packet_type == PacketTypeCMS.segment_date
        assert packet_date.user() == user
        assert packet_date.segment() == segment
        assert packet_time.packet_type == PacketTypeCMS.segment_time
        assert packet_time.user() == user
        assert packet_time.segment() == segment
        segment_date = packet_date.segment_date()
        segment_time = packet_time.segment_time()
        return DateTime.strptime(f'{segment_date} {segment_time}', '%Y-%m-%d %H:%M:%S')

    def query_device_brand(self) -> str:
        self.packet_write(ControlPacketCMS.query_device_brand())
        packet = self.packet_read()
        assert packet.packet_type == PacketTypeCMS.device_brand
        return packet.comment()

    def query_device_model(self) -> str:
        self.packet_write(ControlPacketCMS.query_device_model())
        packet_one = self.packet_read()
        packet_two = self.packet_read()
        assert packet_one.packet_type == PacketTypeCMS.device_model
        assert packet_two.packet_type == PacketTypeCMS.device_model
        return f"{packet_one.comment()}{packet_two.comment()}"

    def visit_stored_record(self,
            user:int, segment:int,
            react_record:Callable[RecordCMS.Result, None],
        ) -> None:
        "iterate over stored user/segment records"
        record_count = self.query_segment_size(user=user, segment=segment)
        packet_count = int(record_count / RegularPacketCMS.PacketStoredBucket.data_size)
        self.packet_write(ControlPacketCMS.issue_stored_start(user=user, segment=segment))
        sequence = 1
        for _ in range(packet_count):
            packet = self.packet_read()
            assert packet.packet_type == PacketTypeCMS.stored_bucket, f"wrong packet: {packet}"
            record_list = packet.data_list(sequence)
            sequence += packet.data_size
            for record in record_list:
                react_record(record)


@dataclass
class DeviceInnovoCMS50F(SerialCP210XTrait, CommandCMS50F, DeviceUSB):
    """
    Wrist Pulse Oximeter
    https://innovo-medical.com/products/innovo-cms-50f-plus
    """

    config_entry = 'device/usb/innovo_cms50f'

    # buffer for input stream
    input_stream:bytearray = field(init=False, repr=False, default_factory=bytearray)

    @override
    def start(self) -> None:
        super().start()
        self.serial_start()
        self.input_stream = bytearray()

    @override
    def stop(self) -> None:
        self.serial_stop()
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
        logger.trace(f"buffer: {BufferSupportCMS.format_hex2(buffer)}")
        return buffer

    def hid_put(self, buffer:array) -> None:
        "transmit byte array into hid device"
        point = self.point_hid_output()
        logger.trace(f"buffer: {BufferSupportCMS.format_hex2(buffer)}")
        assert len(buffer) <= point.wMaxPacketSize
        self.pyusb_device.write(
            point.bEndpointAddress, buffer, self.timeout()
        )

    @override
    def serial_clear_pending_input(self):
        "clear previous broken segment stream"
        self.packet_write(ControlPacketCMS.issue_stream_abort())
        self.packet_write(ControlPacketCMS.issue_stored_abort())
        super().serial_clear_pending_input()
        try:
            "remove possible stray bytes from usb serial buffer"
            self.hid_get()
        except:
            "ignore error when device is connected but powerded down"
            pass

    @override
    def serial_clear_pending_ouput(self):
        super().serial_clear_pending_output()

    def serial_start(self) -> None:
        "configure serial device"  # TODO expose config
        self.serial_IFC_ENABLE(state=True)
        self.serial_SET_BAUDRATE(baudrate=115200)
        self.serial_SET_LINE_CTL(word_length=8, stop_bits=0, parity_setting=0)
        self.serial_SET_XON()
        self.serial_SET_MHS(0x0303)
        self.serial_SET_MHS(0x0101)
        self.serial_SET_MHS(0x0202)
        self.serial_clear_pending_input()

    def serial_stop(self) -> None:
        "unconfigure serial device"
        self.packet_write(ControlPacketCMS.issue_stream_abort(), use_flush=True)
        self.packet_write(ControlPacketCMS.issue_stored_abort(), use_flush=True)
        self.serial_IFC_ENABLE(state=False)

    def packet_read(self) -> PacketCMS:
        "receive packet while buffering input stream"
        while not self.input_stream:
            self.input_stream += self.hid_get()  # ensure packet head
        typer = self.input_stream[0]  # extract message type
        assert typer & 0x80 == 0, f"wrong typer: {hex(typer)} stream: {self.input_stream}"
        packet_class = RegularPacketCMS.packet_class_from(typer)
        packet_size = packet_class.packet_size
        while len(self.input_stream) < packet_size:
            self.input_stream += self.hid_get()  # ensure complete packet
        buffer = self.input_stream[0:packet_size]  # extract packet bytes
        self.input_stream = self.input_stream[packet_size:]  # consume stream
        packet = packet_class(buffer)  # produce device packet
        return packet

    def packet_write(self, packet:PacketCMS, use_flush:bool=False, delay:float=0.2) -> None:
        "transmit packet via hid, optionally confirm via serial"
        self.hid_put(packet.buffer)
        while use_flush and self.serial_has_pending_output():
            time.sleep(delay)

    @override
    def device_identity(self) -> str:
        "CMS uses fixed serial number and user congurable device id"
        super_id = super().device_identity()
        instance_id = self.query_device_id()
        return f"{super_id}/{instance_id}"

    @override
    def device_description(self) -> str:
        return "Wrist Pulse Oximeter CMS50F"
