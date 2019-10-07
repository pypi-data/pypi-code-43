"""
Serialization support with special types
"""

from __future__ import annotations

import copy
import math
import uuid
from typing import Mapping
from typing import Type


# immutable
class WiredBytes(bytes):
    """
    serializable identity
    """

    def __init__(self, value:bytes):
        self = value

    def __str__(self) -> str:
        return self.to_hex()

    def __repr__(self) -> str:
        return f"⟪{self.to_hex()}⟫"

    def copy(self):
        return WiredBytes(copy.copy(self))

    def to_hex(self) -> str:
        return self.hex()

    def to_int(self) -> int:
        return int.from_bytes(self, "big")

    def to_urn(self) -> str:
        return 'urn:uuid:' + self.to_hex()

    @staticmethod
    def empty() -> 'WiredBytes':
        return WiredSupport.wired_bytes_empty

    @staticmethod
    def generate() -> 'WiredBytes':
        return WiredBytes(uuid.uuid4().bytes)

    @staticmethod
    def from_int(value:int) -> 'WiredBytes':
        size = int(math.ceil(value.bit_length() / 8))
        return WiredBytes(int.to_bytes(value, size, "big"))

    @staticmethod
    def from_hex(value:str) -> 'WiredBytes':
        value = value.replace('-', '')
        return WiredBytes(bytes.fromhex(value))


class WiredSupport:

    wired_bytes_empty:WiredBytes = WiredBytes(bytes())

    @staticmethod
    def binary_dict(string_dict:Mapping) -> Mapping:
        result = dict()
        for str_key, str_value in string_dict.items():
            bin_key = str_key.encode()
            bin_value = str_value.encode()
            result[bin_key] = bin_value
        return result

    @staticmethod
    def string_dict(binary_dict:Mapping) -> Mapping:
        result = dict()
        for bin_key, bin_value in binary_dict.items():
            str_key = bin_key.decode()
            str_value = bin_value.decode()
            result[str_key] = str_value
        return result
