from __future__ import annotations

import io
import struct
import zipfile
from dataclasses import dataclass
from typing import Optional


@dataclass()
class SimpleLauncher:
    launcher: Optional[bytes]
    shebang: Optional[bytes]
    data: bytes # Note: zip


def parse_simple_launcher(all_data: bytes, verbose: bool=False) -> SimpleLauncher:
    """
    Parse binary data of simple_launcher to SimpleLauncher dataclass.

    The simple_launcer is used in 'pip' to make console_script in Windows and the
    project is developped on https://bitbucket.org/vinay.sajip/simple_launcher

    The 'launcher' and 'shebang' attribute of the result may be None, indicating that
    the given data is not a valid simple_launcher binary.

    Note that most of code in this function has forked from pyzzer via Vinay Sajip.
    https://bitbucket.org/vinay.sajip/pyzzer/src/5d5740cb04308f067d5844a56fbe91e7a27efccc/pyzzer/__init__.py?at=default&fileviewer=file-view-default#__init__.py-112
    """
    # The MIT License (MIT)
    #
    # Copyright (c) 2013 Vinay Sajip.
    #
    # Permission is hereby granted, free of charge, to any person obtaining a copy
    # of this software and associated documentation files (the "Software"), to deal
    # in the Software without restriction, including without limitation the rights
    # to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
    # copies of the Software, and to permit persons to whom the Software is
    # furnished to do so, subject to the following conditions:
    #
    # The above copyright notice and this permission notice shall be included in
    # all copies or substantial portions of the Software.
    #
    # THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
    # IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
    # FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
    # AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
    # LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
    # OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
    # THE SOFTWARE.
    #
    # https://bitbucket.org/vinay.sajip/simple_launcher/issues/3/relocatability-of-launchers
    launcher = shebang = data = None
    pos = all_data.rfind(b'PK\x05\x06')
    if pos == -1:
        return SimpleLauncher(None, None, all_data)
    launcher = shebang = None
    try:
        end_cdr = all_data[pos + 12:pos + 20]
        cdr_size, cdr_offset = struct.unpack('<LL', end_cdr)
        arc_pos = pos - cdr_size - cdr_offset
        data = all_data[arc_pos:]
        if arc_pos > 0:
            pos = all_data.rfind(b'#!', 0, arc_pos)
            if pos >= 0:
                shebang = all_data[pos:arc_pos]
                if pos > 0:
                    launcher = all_data[:pos]
    except Exception as e:
        if verbose:
            print(e)
    return SimpleLauncher(launcher, shebang, data)
