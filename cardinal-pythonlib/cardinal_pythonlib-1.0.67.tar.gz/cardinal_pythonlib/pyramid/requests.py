#!/usr/bin/env python
# cardinal_pythonlib/pyramid/requests.py

"""
===============================================================================

    Copyright (C) 2015-2019 Rudolf Cardinal (rudolf@pobox.com).

    This file is part of CRATE.

    CRATE is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    CRATE is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with CRATE. If not, see <http://www.gnu.org/licenses/>.

===============================================================================

Functions to operate on Pyramid requests.

"""

import gzip
import logging
from typing import Generator
import zlib

from pyramid.request import Request
from webob.headers import EnvironHeaders

try:
    # noinspection PyPackageRequirements
    import brotli  # pip install brotlipy
except ImportError:
    brotli = None

log = logging.getLogger(__name__)


# =============================================================================
# Encoding checks
# =============================================================================

HTTP_ACCEPT_ENCODING = "Accept-Encoding"
HTTP_CONTENT_ENCODING = "Content-Encoding"

# https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/Content-Encoding
BR_ENCODING = "br"
COMPRESS_ENCODING = "compress"
DEFLATE_ENCODING = "deflate"
GZIP_ENCODING = "gzip"
X_GZIP_ENCODING = "x-gzip"
IDENTITY_ENCODING = "identity"


def gen_accept_encoding_definitions(accept_encoding: str) \
        -> Generator[str, None, None]:
    """
    For a given HTTP ``Accept-Encoding`` field value, generate encoding
    definitions. An example might be:

    .. code-block:: python

        from cardinal_pythonlib.pyramid.compression import *
        accept_encoding = "br;q=1.0, gzip;q=0.8, *;q=0.1"
        print(list(gen_encoding_definitions(accept_encoding)))

    which gives

    .. code-block:: none

        ['br;q=1.0', 'gzip;q=0.8', '*;q=0.1']

    """
    for definition in accept_encoding.split(","):
        yield definition.strip()


def gen_accept_encodings(accept_encoding: str) \
        -> Generator[str, None, None]:
    """
    For a given HTTP ``Accept-Encoding`` field value, generate encodings.
    An example might be:

    .. code-block:: python

        from cardinal_pythonlib.pyramid.compression import *
        accept_encoding = "br;q=1.0, gzip;q=0.8, *;q=0.1"
        print(list(gen_encodings(accept_encoding)))

    which gives

    .. code-block:: none

        ['br', 'gzip', '*']
    """
    for definition in gen_accept_encoding_definitions(accept_encoding):
        yield definition.split(";")[0].strip()


def request_accepts_gzip(request: Request) -> bool:
    """
    Does the request specify an ``Accept-Encoding`` header that includes
    ``gzip``?

    Note:

    - Field names in HTTP headers are case-insensitive (e.g. "accept-encoding"
      is fine).
    - WebOb request headers are in a case-insensitive dictionary; see
      https://docs.pylonsproject.org/projects/webob/en/stable/. (Easily
      verified by altering the key being checked; it works.)
    - However, the value is a Python string so is case-sensitive.
    - But the HTTP standard doesn't say that field values are case-insensitive;
      see https://www.w3.org/Protocols/rfc2616/rfc2616-sec4.html#sec4.2.
    - So we'll do a case-sensitive check for "gzip".
    - But there is also a bit of other syntax possible; see
      https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/Accept-Encoding.
    """  # noqa
    headers = request.headers  # type: EnvironHeaders
    if HTTP_ACCEPT_ENCODING not in headers:
        return False
    accepted_encodings = headers[HTTP_ACCEPT_ENCODING]
    for encoding in gen_accept_encodings(accepted_encodings):
        if encoding == GZIP_ENCODING:
            return True
    return False


def gen_content_encodings(request: Request) -> Generator[str, None, None]:
    """
    Generates content encodings in the order they are specified -- that is, the
    order in which they were applied.
    """
    headers = request.headers  # type: EnvironHeaders
    if HTTP_CONTENT_ENCODING not in headers:
        return
    content_encoding = headers[HTTP_CONTENT_ENCODING]
    for encoding in content_encoding.split(","):
        yield encoding.strip()


def gen_content_encodings_reversed(request: Request) \
        -> Generator[str, None, None]:
    """
    Generates content encodings in reverse order -- that is, in the order
    required to reverse them.
    """
    for encoding in reversed(list(gen_content_encodings(request))):
        yield encoding


def decompress_request(request: Request) -> None:
    """
    Reverses anything specified in ``Content-Encoding``, modifying the request
    in place.
    """
    for encoding in gen_content_encodings_reversed(request):
        if encoding in [GZIP_ENCODING, X_GZIP_ENCODING]:
            request.body = gzip.decompress(request.body)
        elif encoding == IDENTITY_ENCODING:
            pass
        elif encoding == DEFLATE_ENCODING:
            request.body = zlib.decompress(request.body)
        elif encoding == BR_ENCODING:
            if brotli:
                # https://python-hyper.org/projects/brotlipy/en/latest/
                request.body = brotli.decompress(request.body)
            else:
                raise NotImplementedError(
                    "Content-Encoding {} not supported (brotlipy package not "
                    "installed)".format(encoding))
        else:
            raise ValueError("Unknown Content-Encoding: {}".format(encoding))
            # ... e.g. "compress"; LZW; patent expired; see
            # https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/Content-Encoding  # noqa
