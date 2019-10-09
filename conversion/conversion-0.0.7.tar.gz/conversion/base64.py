"""
Base64 encoded string to a string
"""
import base64
import binascii

from typing import Union

STR_BYTES = Union[str, bytes]

__all__ = ["convert_base64"]


def convert_base64(
    value: STR_BYTES, convert_string: bool = True, raise_exceptions: bool = False
) -> STR_BYTES:
    """
    Returns a base64 encoded string as a decoded string

    Args:
        value: the value to convert
        convert_string: whether to decode a string, defaults to True
        raise_exceptions: whether to raise decoding errors, or return the default string
    """
    converted = value

    try:
        converted = base64.b64decode(value)
    except binascii.Error:
        if raise_exceptions:
            raise
    else:
        if convert_string:
            converted = converted.decode("utf8")

    return converted
