"""
Standard Specification for Low-Level Protocol
to Transfer Messages Between Clinical Laboratory Instruments and Computer Systems
https://www.astm.org/Standards/E1381.htm
"""

from __future__ import annotations

import enum
import re
from dataclasses import dataclass
from dataclasses import field

from healer.device.protocol.token import AsciiToken


class ErrorASTM(ValueError): pass


class FormatErrorASTM(ErrorASTM): pass


class ChecksumErrorASTM(ErrorASTM): pass


@enum.unique
class TypeE1381(enum.Enum):
    """
    E1381 frame type
    """
    more = AsciiToken.ETB
    stop = AsciiToken.ETX


@dataclass(frozen=True)
class FrameE1381:
    """
    E1381 frame representation
    """

    # underlying frame text content
    frame:str = field()

    @property
    def match(self) -> re.Match:
        if not hasattr(self, '_match_'):
            object.__setattr__(self, '_match_', FrameE1381Support.frame_regex.match(self.frame))
        return self._match_

    def __post_init__(self):
        if not self.match:
            raise FormatErrorASTM(
                f"wrong frame: {self.frame}"
            )
        if self.packet_checksum() != self.payload_checksum():
            raise ChecksumErrorASTM(
                f"wrong checksum: actual={self.checksum()} computed={self.payload_checksum()}"
            )

    def __repr__(self):
        ubox = '\u25A1'
        type = self.type().name
        seq = self.seq()
        data = self.data().replace('\n', ubox).replace('\r', ubox)
        checksum = self.packet_checksum()
        return f"Frame(type='{type}', seq='{seq}', data='{data}', checksum='{checksum}')"

    def __getstate__(self):
        state = self.__dict__.copy()
        del state["_match_"]
        return state

    def __setstate__(self, state):
        self.__dict__.update(state)

    def seq(self) -> str:
        "frame sequence number"
        return self.match.group('seq')

    def data(self) -> str:
        "frame payload data"
        return self.match.group('data')

    def type(self) -> TypeE1381:
        "frame continuation type"
        return TypeE1381(self.match.group('type'))

    def packet_checksum(self) -> str:
        "frame payload actual checksum"
        return self.match.group('checksum')

    def payload(self) -> str:
        "frame payload subject to checksum"
        return self.frame[self.match.start('seq'):self.match.end('type')]

    def payload_checksum(self) -> str:
        "frame payload computed checksum"
        return FrameE1381Support.compute_checksum_text(self.payload())

    def trailer(self) -> str:
        "frame non-mathed trailer text"
        return self.frame[self.match.end(0):]

    def has_final(self):
        "detect frame type"
        return self.type() == TypeE1381.stop


class FrameE1381Support:
    """
    Utility functions
    """

    # The structure of an E-1381 frame is illustrated as follows:
    # <STX> FN text <ETB> C1 C2 <CR> <LF>
    # or
    # <STX> FN text <ETX> C1 C2 <CR> <LF>
    frame_regex = re.compile(
        "\x02"  # start marker: STX
        "(?P<seq>[0-7])"  # frame number: starts at 1, wraps to 0 after 7
        "(?P<data>[^\x03\x17]*?)"  # data, (non ETX, non ETB)
        "[\r]*"  # optional CR separator
        "(?P<type>[\x03\x17])"  # frame type: ETX = end now, ETB = more follows
        "(?P<checksum>[0-9A-Fa-f]{2})"  # 8-bit checksum in hex
        "\r\n"  # stop marker: CRLF
        ,
        re.RegexFlag.DOTALL,
    )

    @staticmethod
    def compute_checksum(data:str) -> int:
        return sum([ord(c) for c in data]) & 0xff

    @staticmethod
    def compute_checksum_text(data:str) -> str:
        checksum = FrameE1381Support.compute_checksum(data)
        return "{:02X}".format(checksum)
