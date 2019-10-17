import struct as s


def toi16(buf: bytes, invert: bool = False) -> int:
    """Decode binary buffer"""
    if invert:
        buf = buf[::-1]
    data = bytes(
        [
            ((buf[0] & 0x3) << 6) | ((buf[1] >> 1) & 0x3F),
            ((buf[1] & 0x1) << 7) | (buf[2] & 0x7F),
        ]
    )
    return s.unpack(">h", data)[0]


def toi32(buf: bytes, invert: bool = False) -> int:
    """Decode binary buffer"""
    if invert:
        buf = buf[::-1]
    data = bytes(
        [
            ((buf[0] & 0xF) << 4) | ((buf[1] >> 3) & 0x0F),
            ((buf[1] & 0x7) << 5) | ((buf[2] >> 2) & 0x1F),
            ((buf[2] & 0x3) << 6) | ((buf[3] >> 1) & 0x3F),
            ((buf[3] & 0x1) << 7) | (buf[4] & 0x7F),
        ]
    )
    return s.unpack(">i", data)[0]
