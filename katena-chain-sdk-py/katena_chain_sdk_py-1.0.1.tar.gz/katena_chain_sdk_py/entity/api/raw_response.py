"""
Copyright (c) 2019, TransChain.

This source code is licensed under the Apache 2.0 license found in the
LICENSE file in the root directory of this source tree.
"""


class RawResponse:
    """ Response is a requests response wrapper. """

    def __init__(self, status_code: int, body: bytes):
        """ RawResponse constructor. """
        self.status_code = status_code
        self.body = body

    def get_status_code(self) -> int:
        return self.status_code

    def get_body(self) -> bytes:
        return self.body
