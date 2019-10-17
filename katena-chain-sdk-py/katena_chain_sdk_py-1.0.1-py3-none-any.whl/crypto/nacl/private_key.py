"""
Copyright (c) 2019, TransChain.

This source code is licensed under the Apache 2.0 license found in the
LICENSE file in the root directory of this source tree.
"""

from nacl.exceptions import CryptoError
from nacl.public import PrivateKey as BoxPrivateKey, PublicKey as BoxPublicKey, Box
from katena_chain_sdk_py.crypto.base_key import BaseKey
from katena_chain_sdk_py.crypto.nacl.public_key import PublicKey


class PrivateKey(BaseKey):
    """ PrivateKey is an X25519 private key wrapper (64 bytes). """

    def __init__(self, key: bytes):
        """ PrivateKey constructor. """
        super().__init__(key)
        self.public_key = PublicKey(self.get_key()[32:])

    def get_public_key(self) -> PublicKey:
        return self.public_key

    def seal(self, message: bytes, recipient_public_key: PublicKey) -> (bytes, bytes):
        """ Encrypts a plain text message decipherable afterwards by the recipient private key. """
        box = Box(BoxPrivateKey(self.get_key()[:32]), BoxPublicKey(recipient_public_key.get_key()))
        sealed_box = box.encrypt(message)
        return sealed_box.ciphertext, sealed_box.nonce

    def open(self, encrypted_message: bytes, sender_public_key: PublicKey, nonce: bytes) -> bytes:
        """ Decrypts an encrypted message with the appropriate sender information. """
        box = Box(BoxPrivateKey(self.get_key()[:32]), BoxPublicKey(sender_public_key.get_key()))
        try:
            return box.decrypt(encrypted_message, nonce)
        except CryptoError:
            return bytes()
