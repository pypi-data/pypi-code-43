"""
Copyright (c) 2019, TransChain.

This source code is licensed under the Apache 2.0 license found in the
LICENSE file in the root directory of this source tree.
"""

from katena_chain_sdk_py.crypto.base_key import BaseKey


class PublicKey(BaseKey):
    """ PublicKey is an X25519 public key wrapper (32 bytes). """

    def __init__(self, key: bytes):
        """ PublicKey constructor. """
        super().__init__(key)
