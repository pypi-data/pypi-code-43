"""
Device driver for
Bayer Contour Next USB
Blood Glucose Monitoring System
https://www.contournext.com/products/contour-next-usb/
"""

from __future__ import annotations

import logging
import re
from collections import namedtuple
from dataclasses import dataclass
from dataclasses import field
from enum import Enum
from typing import Any
from typing import Callable
from typing import List

import usb.core

from healer.device.protocol.ASTM_E1381 import FrameE1381
from healer.device.protocol.token import AsciiToken
from healer.device.record import DeviceRecord
from healer.device.usb.arkon import DeviceUSB
from healer.support.hronos import DateTime
from healer.support.typing import cached_method
from healer.support.typing import override
from healer.support.wired.base import WiredDatum

logger = logging.getLogger(__name__)


class FaceNum(Enum):
    """
    Device usb interfaces
    """
    hid = 0
    disk = 1


class HidPointAddr(Enum):
    """
    HID device end point addresses
    """
    input = 0x83
    output = 0x4


@dataclass(frozen=True)
class InvokeResultCN:
    """
    Command response representation
    """
    header_frame:FrameE1381 = field(repr=False)
    result_list:List[str] = field()


class InvokeSupportCN:

    # pattern: D|YYMMDD|CRLF
    regex_date = re.compile("D[|]([0-9]{6})[|]\r\n")

    # pattern: D|HHMM|CRLF
    regex_time = re.compile("D[|]([0-9]{4})[|]\r\n")

    @staticmethod
    def extract_clock(invoke_result:InvokeResultCN):
        return InvokeSupportCN.parse_clock(invoke_result.result_list)

    @staticmethod
    def parse_clock(result_list:List[str]) -> DateTime:
        date_text = None
        time_text = None
        for result in result_list:
            match_date = InvokeSupportCN.regex_date.match(result)
            if match_date:
                date_text = match_date.group(1)
            match_time = InvokeSupportCN.regex_time.match(result)
            if match_time:
                time_text = match_time.group(1)
        assert date_text, f"no date_text: {result_list}"
        assert time_text, f"no time_text: {result_list}"
        instant = DateTime.strptime(f'{date_text}{time_text}', '%y%m%d%H%M')
        return instant

    @staticmethod
    def make_clock_date(instant:DateTime) -> str:
        return instant.strftime("%y%m%d")

    @staticmethod
    def make_clock_time(instant:DateTime) -> str:
        return instant.strftime("%H%M")


class RecordCN:
    "device persitent record components"

    @dataclass(frozen=True)
    class Version(WiredDatum):
        "device firmware"

        engine_version:str
        algo_version:str
        agp_version:str

    @dataclass(frozen=True)
    class SenderId(WiredDatum):
        "device identity"

        product:str  # product name
        version:RecordCN.Version  # product version
        serial_number:str  # see usb/iSerialNumber
        tracking_number:str  # SKU, not used

    class InfoKey:  # keys for DeviceInfo
        auto_mark = 'A'  # enable auto-mark logging
        conf_bits = 'C'  # configuration bits mask
        user_lang = 'G'  # meter user language
        test_time = 'I'  # test reminder time interval
        reference = 'R'  # reference method
        internal = 'S'  # reserved / internal value
        user_unit = 'U'  # unit of measure
        gluco_range = 'V'  # glucose hi/lo range
        user_gluco_range = 'X'  # personal glucose hi/lo range
        limit_gluco_range = 'Y'  # glucose hi/lo range limits
        trend_display = 'Z'  # mode of trend display

    @dataclass(frozen=True)
    class DeviceInfo(WiredDatum):
        "device settings"

        auto_mark:str
        conf_bits:str
        user_lang:str
        test_time:str
        reference:str
        internal:str
        user_unit:str
        gluco_range:str
        user_gluco_range:str
        limit_gluco_range:str
        trend_display:str

        def conf_bit(self, num:int) -> bool:
            "extract config bit"
            bits = int(self.conf_bits)
            mask = 1 << num
            return bits & mask != 0

        def conf_buzzer_enbale(self) -> bool:
            "0 = disabled, 1 = enabled"
            return self.conf_bit(1)

        def conf_time_format(self) -> bool:
            "0 = 12 hr, 1 = 24 hr"
            return self.conf_bit(2)

        def conf_time_reminder(self) -> bool:
            "0 = disable, 1 = enable"
            return self.conf_bit(8)

        def conf_date_format(self) -> bool:
            "0 = m/d/y 1 = d.m.y"
            return self.conf_bit(32)

        def gluco_cut_lo(self) -> int:
            "LLHHH (values in mg/dL); LL = Low cut off; HHH = High cut off"
            assert len(self.gluco_range) == 5
            LL = self.gluco_range[0:1]
            return int(LL)

        def gluco_cut_hi(self) -> int:
            "LLHHH (values in mg/dL); LL = Low cut off; HHH = High cut off"
            assert len(self.gluco_range) == 5
            HHH = self.gluco_range[2:4]
            return int(HHH)

    @dataclass(frozen=True)
    class Header(DeviceRecord):
        "device header record"

        device_codec_guid = 101

        sender_id:RecordCN.SenderId
        device_info:RecordCN.DeviceInfo
        record_count:int
        processing_id:str
        specific_version:str
        session_stamp:DateTime

    @dataclass(frozen=True)
    class Patient(DeviceRecord):
        "device patient profile record"

        device_codec_guid = 102

        practice_id:str
        laboratory_id:str

    @dataclass(frozen=True)
    class Result(DeviceRecord):
        "device measurement record"

        device_codec_guid = 103

        seq:int  # sequence number
        mode:str  # aka record id aka record type: glucose|carb|insulin
        data:float  # measured value
        unit:str  # measurement unit
        refs:str  # measurement reference method
        stamp:DateTime  # measurement date/time

    @dataclass(frozen=True)
    class Trailer(DeviceRecord):
        "device session trailer record"

        device_codec_guid = 104

        cookie:str  # partial retrieve marker
        status:str  # session termination status code

    @dataclass(frozen=True)
    class Summary(DeviceRecord):
        "device session summary record"

        device_codec_guid = 105

        header:RecordCN.Header
        patient:RecordCN.Patient
        trailer:RecordCN.Trailer


class RecordSupportCN:
    "persistent record provider"

    @staticmethod
    def parse_instant_YMD_HM(date_time_line:str) -> DateTime:
        "extract device record date/time stamp: 201801121314"
        return DateTime.strptime(date_time_line, '%Y%m%d%H%M')

    @staticmethod
    def parse_instant_YMD_HMS(date_time_line:str) -> DateTime:
        "extract device record date/time stamp: 20180112131415"
        return DateTime.strptime(date_time_line, '%Y%m%d%H%M%S')

    @staticmethod
    def parse_frame_data(data_line:str) -> DeviceRecord:
        "persistent device record provider"
        type_char = data_line[0]
        if type_char == 'R':
            return RecordSupportCN.parse_result_data(data_line)
        if type_char == 'H':
            return RecordSupportCN.parse_header_data(data_line)
        if type_char == 'P':
            return RecordSupportCN.parse_patient_data(data_line)
        if type_char == 'L':
            return RecordSupportCN.parse_trailer_data(data_line)
        raise RuntimeError(f"wrong data: {data_line}")

    @staticmethod
    def parse_header_data(data_line:str) -> RecordCN.Header:
        "produce device header record"
        data_term = data_line.split('|')
        # extract device identity
        sender_line = data_term[4]
        sender_term = sender_line.split('^')
        version_line = sender_term[1]
        version_term = version_line.split("\\")
        sender_id = RecordCN.SenderId(
            product=sender_term[0],
            version=RecordCN.Version(
                engine_version=version_term[0],
                algo_version=version_term[1],
                agp_version=version_term[2],
            ),
            serial_number=sender_term[2],
            tracking_number=sender_term[3],
        )
        # extract device settings
        device_line = data_term[5]
        device_term = device_line.split("^")
        device_dict = {
            key:value for key, value in (entry.split('=') for entry in device_term)
        }
        user_lang_line = device_dict[RecordCN.InfoKey.user_lang]
        user_lang_term = user_lang_line.split(',')
        device_info = RecordCN.DeviceInfo(
            auto_mark=device_dict[RecordCN.InfoKey.auto_mark],
            conf_bits=device_dict[RecordCN.InfoKey.conf_bits],
            user_lang=user_lang_term[0],
            test_time=device_dict[RecordCN.InfoKey.test_time],
            reference=device_dict[RecordCN.InfoKey.reference],
            internal=device_dict[RecordCN.InfoKey.internal],
            user_unit=device_dict[RecordCN.InfoKey.user_unit],
            gluco_range=device_dict[RecordCN.InfoKey.gluco_range],
            user_gluco_range=device_dict[RecordCN.InfoKey.user_gluco_range],
            limit_gluco_range=device_dict[RecordCN.InfoKey.limit_gluco_range],
            trend_display=device_dict[RecordCN.InfoKey.trend_display],
        )
        # extract summary
        record_count = data_term[6]
        processing_id = data_term[11]
        specific_version = data_term[12]
        stamp_line = data_term[13]
        stamp_instant = RecordSupportCN.parse_instant_YMD_HMS(stamp_line)
        #
        return RecordCN.Header(
            sender_id=sender_id,
            device_info=device_info,
            record_count=int(record_count),
            processing_id=processing_id,
            specific_version=specific_version,
            session_stamp=stamp_instant,
        )

    @staticmethod
    def parse_patient_data(data_line:str) -> RecordCN.Patient:
        "produce device patient record"
        data_term = data_line.split('|')
        practice_id = data_term[2] if len(data_term) > 2 else None
        laboratory_id = data_term[3]if len(data_term) > 3 else None
        #
        return RecordCN.Patient(
            practice_id=practice_id,
            laboratory_id=laboratory_id,
        )

    @staticmethod
    def parse_result_data(data_line:str) -> RecordCN.Result:
        "produce device result data record"
        data_term = data_line.split('|')
        # record sequence
        sequence = data_term[1]
        # measurement type: sugar vs insulin
        type_line = data_term[2]
        type_term = type_line.split('^')
        type_mode = type_term[3].lower()  # erase case sensitivity
        # record data and unit
        data_item = data_term[3]
        unit_line = data_term[4]
        unit_term = unit_line.split('^')
        data_unit = unit_term[0]
        data_refs = unit_term[1]
        # record date/time stamp
        stamp_line = data_term[8]
        stamp_instant = RecordSupportCN.parse_instant_YMD_HM(stamp_line)
        #
        return RecordCN.Result(
            seq=int(sequence),
            mode=type_mode,
            data=float(data_item),
            unit=data_unit,
            refs=data_refs,
            stamp=stamp_instant,
        )

    @staticmethod
    def parse_trailer_data(data_line:str) -> RecordCN.Trailer:
        "produce device session trailer record"
        #
        data_term = data_line.split('|')
        cookie_line = data_term[2] if len(data_term) > 2 else None
        status_line = data_term[3] if len(data_term) > 3 else None
        #
        return RecordCN.Trailer(
            cookie=cookie_line,
            status=status_line,
        )

    # TODO remove
    record_map = {
        'H': namedtuple(
            "HeaderRecord",
            """
            type delimiters
            unknown_3 unknown_4
            sender_id device_info record_count
            unknown_8 unknown_9 unknown_10 unknown_11
            processing_id spec_version date_time
            """.split()
        ),
        'P': namedtuple(
            "PatientRecord",
            """
            type sequence
            practice_id laboratory_id
            """.split()
        ),
        'R': namedtuple(
            "ResultRecord",
            """
            type sequence record_id
            data_value unit_mode
            unknown_6
            markers
            unknown_8
            date_time
            """.split()
        ),
        'L': namedtuple(
            "TrailerRecord",
            """
            type sequence read_key termination_code
            """.split()
        ),
    }


@dataclass
class DeviceRecordCN:
    """
    Contour Next USB astm frame parser
    """

    def __init__(self, data:str):
        type_char = data[0]
        record_class = RecordSupportCN.record_map[type_char]
        data_args = data.split("|")
        self.field_list = record_class(*data_args)

    def field_dict(self) -> dict:
        return self.field_list._asdict()

    def format(self, template:str):
        return template.format(**self.field_dict())


class DeviceSupportCN:
    """
    Utility functions
    """

    @staticmethod
    def defaut_react_frame(frame:FrameE1381) -> None:
        logger.debug(f"frame: {frame}")


@dataclass
class DeviceContourNextUSB(DeviceUSB):
    """
    Blood glucose tester:
    https://www.contournext.com/
    """

    config_entry = 'device/usb/bayer_contour_next_usb'

    # device hid input stream collector
    input_stream:str = ''

    @override
    def start(self) -> None:
        super().start()
        self.input_stream = ''

    @override
    def stop(self) -> None:
        super().stop()
        self.input_stream = ''

    @cached_method
    def face_hid(self) -> usb.core.Interface:
        return self.select_face(FaceNum.hid)

    @cached_method
    def face_disk(self) -> usb.core.Interface:
        return self.select_face(FaceNum.disk)

    @cached_method
    def point_hid_input(self) -> usb.core.Endpoint:
        return self.select_point(self.face_hid(), HidPointAddr.input)

    @cached_method
    def point_hid_output(self) -> usb.core.Endpoint:
        return self.select_point(self.face_hid(), HidPointAddr.output)

    def hid_get(self) -> None:
        "receive input into hid stream"
        point = self.point_hid_input()
        buffer = self.pyusb_device.read(
            point.bEndpointAddress, point.wMaxPacketSize, self.timeout()
        )
        packet = ''.join([chr(c) for c in buffer])
        assert packet.startswith("ABC"), f"wrong packet: {packet}"
        size = buffer[3]
        data = packet[4:size + 4]
        self.input_stream = self.input_stream + data
        logger.trace(f"data: {repr(data)}")

    def hid_put(self, data:str) -> None:
        "transmit output into hid device"
        point = self.point_hid_output()
        logger.trace(f"data: {repr(data)}")
        size = chr(len(data))
        packet = f"ABC{size}{data}"  # device convention
        assert len(packet) <= point.wMaxPacketSize, f"wrong packet: {packet}"
        self.pyusb_device.write(
            point.bEndpointAddress, packet, self.timeout()
        )

    def hid_read_scan(self, finish_token:str) -> str:
        """
        extract hid input stream section delimited by finish token
        * constume input stream upto the 'finish_token'
        """
        finish_index = self.input_stream.find(finish_token)
        if finish_index >= 0:
            finish_index = finish_index + len(finish_token)
            result = self.input_stream[0:finish_index]
            self.input_stream = self.input_stream[finish_index:]
            logger.trace(f"result: {repr(result)}")
            return result
        else:
            self.hid_get()  # missing finish_token: advace input stream
            return self.hid_read_scan(finish_token)

    def hid_read_slice(self, begin_token:str, finish_token:str) -> str:
        """
        extract hid input stream section delimited by begin/finish tokens
        * discard input stream before 'begin_token'
        * constume input stream between 'begin_token' and 'finish_token'
        """
        begin_index = self.input_stream.find(begin_token)
        if begin_index >= 0:
            self.input_stream = self.input_stream[begin_index:]
        else:
            self.hid_get()  # missing begin_token: advace input stream
            return self.hid_read_slice(begin_token, finish_token)
        finish_index = self.input_stream.find(finish_token)
        if finish_index >= 0:
            finish_index = finish_index + len(finish_token)
            result = self.input_stream[0:finish_index]
            self.input_stream = self.input_stream[finish_index:]
            logger.trace(f"result: {repr(result)}")
            return result
        else:
            self.hid_get()  # missing finish_token: advace input stream
            return self.hid_read_slice(begin_token, finish_token)

    def hid_write(self, data:str) -> None:
        "package outgoing data into packets"
        self.hid_put(data)  # TODO

    def read_solo(self, token:str) -> str:
        "extract single token from input stream"
        return self.hid_read_slice(token, token)

    def read_frame(self, use_ack:bool=False) -> FrameE1381:
        "extract astm frame from input stream"
        frame = self.hid_read_slice(AsciiToken.STX, AsciiToken.CRLF)
        if use_ack:
            self.hid_write(AsciiToken.ACK)
        return FrameE1381(frame)

    def read_frame_stream(self,
            react_record:Callable[[FrameE1381], Any]=DeviceSupportCN.defaut_react_frame,
        ) -> None:
        "retrieve list of stored device frames"
        # wakeup device
        self.hid_write('X')
        # consume response header
        self.read_solo(AsciiToken.EOT)
        self.read_frame(use_ack=False)
        self.read_solo(AsciiToken.ENQ)
        # request frame stream
        self.hid_write(AsciiToken.ACK)
        # react to response frame stream
        while True:
            frame = self.read_frame(use_ack=True)
            react_record(frame)
            if frame.has_final():
                break
        # consume stream end marker
        self.read_solo(AsciiToken.EOT)

    def read_clock(self) -> DateTime:
        "get device real time clock"
        invoke_result = self.invoke_request(
            ['R|', 'D|\r', 'R|', 'T|\r']
        )
        return InvokeSupportCN.extract_clock(invoke_result)

    def write_clock(self, instant:DateTime) -> None:
        "set device real time clock"
        date_text = InvokeSupportCN.make_clock_date(instant)
        time_text = InvokeSupportCN.make_clock_time(instant)
        invoke_result = self.invoke_request(
            ['W|', 'D|\r', f'{date_text}|\r', 'W|', 'T|\r', f'{time_text}|\r']
        )
        assert all([
            result == AsciiToken.ACK
            for result in invoke_result.result_list
        ]), f"wrong result_list: {invoke_result.result_list}"

    def power_on(self) -> InvokeResultCN:
        "perform optional default device setup"
        invoke_result = self.invoke_request(
            ['R|', 'D|\r', 'R|', 'T|\r']
        )
        return invoke_result

    def power_off(self) -> InvokeResultCN:
        "disconnect device from usb bus; note: device will be gone"
        invoke_result = self.invoke_request(
            ['W|', 'E|\r']
        )
        return invoke_result

    def invoke_request(self, command_list: List[str]) -> InvokeResultCN:
        """
        send command request and read command response
        1) send “X” to the meter.
        2) meter responds with <EOT> HEADER <ENQ> within 2 seconds.
        3) send <NAK> to reject data transfer from the meter.
        4) meter responds with <EOT> to indicate it is exiting the transfer phase.
        5) send <ENQ> to the meter to initiate sending remote commands.
        6) meter responds with <ACK> to indicate it is ready to receive remote commands.
        7) send remote commands.
        8) send <EOT> to the meter to indicate remote commands are complete
        9) meter responds with <ENQ> to query host readiness
        """
        # 1) wakeup device
        self.hid_write('X')
        # 2) consume response header
        self.read_solo(AsciiToken.EOT)
        frame_head = self.read_frame()
        self.read_solo(AsciiToken.ENQ)
        # 3) reject frame stream
        self.hid_write(AsciiToken.NAK)
        # 4) consume ready marker
        self.read_solo(AsciiToken.EOT)
        # 5) switch to command mode
        self.hid_write(AsciiToken.ENQ)
        # 6) consume ready marker
        self.read_solo(AsciiToken.ACK)
        # 7) enter command mode
        result_list = []
        invoke_result = InvokeResultCN(frame_head, result_list)
        for command in command_list:
            self.hid_write(command)
            result = self.hid_read_scan(AsciiToken.ACK)
            result_list.append(result)
            if command.startswith('E|'):
                # device is zombie now
                return invoke_result
        # 8) exit command mode
        self.hid_write(AsciiToken.EOT)
        # 9) consume ready marker
        self.read_solo(AsciiToken.ENQ)
        # session complete
        return invoke_result

    @override
    def device_identity(self) -> str:
        "contour Next uses running serial number, and no user configurable device id"
        return super().device_identity()

    @override
    def device_description(self) -> str:
        return "Bayer Contour Next USB Blood Glucose Monitoring System"
