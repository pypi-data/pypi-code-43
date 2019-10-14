#!/usr/bin/env python3
"""
URL Encode/Decode *(urlende)*
=============================
"""

# This module %-encodes and decodes parts of URIs

SAFE_CHARS = "ABCDEFGHIJKLMNOPQRSTUVWSYZ" \
    + "abcdefghijklmnopqrstuvwxyz0192837465-._~"
"""Characters that are always URI-safe."""


def encode(part, safe="/"):
    """Percent-encode a component of a URI.
    Params:

    - part (str): component of the URI.
    - safe (str, put together if more than 1 char):
        Optional. Char(s) not to encode along with SAFE_CHARS.
        Reserved chars, for example.
    """
    if type(part) is int:  # for port
        return part
    part = part.replace("%", "%25")  # so nothing gets encoded twice
    total_safe = safe + SAFE_CHARS + "%"
    for i in range(256):
        c = chr(i)
        if c not in total_safe and c in part:
            code = "%%%02X" % i
            part = part.replace(c, code)
    return part


def encode_query(part, plus=True, safe=""):
    """Encode something that is part of a query (key, or value).
    Params:

    - part (str): key or value.
    - plus (bool): Optional.
        True: if space should be encoded as + instead of %20.
    - safe (str): Optional. Char(s) not to encode.
    """
    # Plus = True when space = + rather than '%20'
    part = encode(part, safe=safe + " ")
    spaceReplace = "+" if plus else "%20"
    part = part.replace(" ", spaceReplace)
    return part


def decode(part):
    """Decode a part of a URI which has already been percent-encoded.
    Params:

    - part (str): percent-encoded URI component.
    """
    if type(part) is int:  # for port
        return part
    all_parts = part.split("%")
    part_list = all_parts[1:]
    res = [all_parts[0]]
    for piece in part_list:
        possible_code = piece[:2]
        rest = piece[2:]
        i = int(possible_code, 16)
        add = chr(i) if i >= 0 and i < 256 else "%" + possible_code
        res.append(add + rest)
    return "".join(res)


def decode_query(part, plus=True):
    """Decode something that is part of a query (key, or value) or path.
    Params:

    - part (str): part to be decoded.
    - plus (bool): Optional. True if space is + instead of %20.
    """
    if plus:
        part = part.replace("+", " ")
    part = decode(part)
    return part


def isEncoded(part, plus=False, safe="/"):
    if type(part) is not int:
        safe += SAFE_CHARS + "%"
        for ch in part:
            if ch not in safe:
                return False
    return True
