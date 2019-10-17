"""
Copyright (c) 2019, TransChain.

This source code is licensed under the Apache 2.0 license found in the
LICENSE file in the root directory of this source tree.
"""

import base64
from katena_chain_sdk_py.crypto.ed25519.private_key import PrivateKey as PrivateKeyEd25519
from katena_chain_sdk_py.crypto.nacl.private_key import PrivateKey as PrivateKeyX25519, PublicKey as PublicKeyX25519


def create_private_key_ed25519_from_base64(private_key_base64: str) -> PrivateKeyEd25519:
    """ Accepts a base64 encoded Ed25519 private key (88 chars) and returns an Ed25519 private key. """
    private_key_bytes = base64.b64decode(private_key_base64)
    return PrivateKeyEd25519(private_key_bytes)


def create_private_key_x25519_from_base64(private_key_base64: str) -> PrivateKeyX25519:
    """ Accepts a base64 encoded X25519 private key (88 chars) and returns an X25519 private key. """
    private_key_bytes = base64.b64decode(private_key_base64)
    return PrivateKeyX25519(private_key_bytes)


def create_public_key_x25519_from_base64(public_key_base64: str) -> PublicKeyX25519:
    """ Accepts a base64 encoded X25519 public key (44 chars) and returns an X25519 public key. """
    public_key_bytes = base64.b64decode(public_key_base64)
    return PublicKeyX25519(public_key_bytes)
