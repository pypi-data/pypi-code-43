#  -*- Mode: Python; -*-                                                   
#  -*- coding: utf-8; -*-
# 
#  decode.py
# 
#  © Copyright Jamie A. Jennings 2019.
#  LICENSE: MIT License (https://opensource.org/licenses/mit-license.html)
#  AUTHOR: Jamie A. Jennings

from __future__ import unicode_literals, print_function
import sys
assert( sys.version_info.major == 3 )


def decode_short(b, i):
    n = b[i] + (b[i+1]<<8)
    if n > 32767:
        n = n - 65536
    return n, i+2

def decode_int(b, i):
    n = b[i] + (b[i+1]<<8) + (b[i+2]<<16) + (b[i+3]<<24)
    if n > 2147483647:
        n = n - 4294967296
    return n, i+4

def decode(bytestring, i=0, start_position=None):
    if start_position is None:
        start_position, i = decode_int(bytestring, i)
    if start_position > 0:
        raise ValueError("Invalid capture start at position {}".format(i-4))
    else:
        start_position = - start_position
    typelen, i = decode_short(bytestring, i)
    data = None
    after_typename = i + (typelen if typelen >= 0 else -typelen)
    typename = bytestring[i:after_typename]
    i = after_typename
    if typelen < 0:
        # constant capture (user-provided string)
        typelen = - typelen
        datalen, i = decode_short(bytestring, i)
        assert( datalen >= 0 )
        data = bytestring[i:i+datalen]
        i = i + datalen
    # else: a regular capture, so the data is a substring of the input
    # and is not included here.
    # next, we peek ahead to see if there is a sub-match
    subs = list()
    next_position, _ = decode_int(bytestring, i) # peek
    while next_position < 0:
        # it's the start position of a nested capture
        sub, i = decode(bytestring, i+4, next_position)
        subs.append(sub)
        next_position, _ = decode_int(bytestring, i) # peek
    i = i + 4
    match = {'type': typename,
             'data': data,
             'subs': subs,
             's': start_position,
             'e': next_position} 
    return match, i

