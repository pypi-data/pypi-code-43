"""
"""

from __future__ import annotations

import re
import string


def parser_render_hex(line:bytes) -> str:
    if line:
        return line.hex()
    else:
        return ""


def parser_render_ascii(line:bytes, star:str='*') -> str:
    "extract printable text from byte array"
    if line:
        chars = [c if chr(c) in string.printable else ord(star) for c in line]
        return bytes(chars).decode()
    else:
        return ""


def parser_produce_range(range_text:str) -> range:
    "produce 'range(a:b)' from text 'a:b'"
    assert range_text, f"no text: {range_text}"
    assert ':' in range_text, f"no range: {range_text}"
    range_terms = range_text.split(':')
    range_start = int(range_terms[0])
    range_finish = int(range_terms[1])
    return range(range_start, range_finish)


regex_cap_start = re.compile('(.)([A-Z][a-z]+)')
regex_cap_sequence = re.compile('([a-z0-9])([A-Z])')


def convert_camel_under(name:str) -> str:
    "convert camel case into underscore separated"
    s1 = regex_cap_start.sub(r'\1_\2', name)
    s2 = regex_cap_sequence.sub(r'\1_\2', s1)
    return s2.lower()
