"""
Copyright (c) 2019, TransChain.

This source code is licensed under the Apache 2.0 license found in the
LICENSE file in the root directory of this source tree.
"""

from nacl.signing import SigningKey
from katena_chain_sdk_py.crypto.base_key import BaseKey
from katena_chain_sdk_py.crypto.ed25519.public_key import PublicKey


class PrivateKey(BaseKey):
    """ PrivateKey is an Ed25519 private key wrapper (64 bytes). """

    def __init__(self, key: bytes):
        """ PrivateKey constructor. """
        super().__init__(key)
        self.public_key = PublicKey(self.get_key()[32:])

    def get_public_key(self) -> PublicKey:
        return self.public_key

    def sign(self, message: bytes) -> bytes:
        """ Accepts a message and returns its corresponding Ed25519 signature. """
        return SigningKey(self.get_key()[:32]).sign(message).signature

