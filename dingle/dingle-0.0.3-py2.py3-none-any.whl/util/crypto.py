# -*- coding: utf-8 -*-
pythoimport os
import base64
import hashlib
import struct
import random
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
from .decr import all_bytes_parameters


@all_bytes_parameters
def encrypt(encoding_aes_key, msg, key):
    aes_key = base64.b64decode(encoding_aes_key + b'=')
    iv = aes_key[:16]
    cipher = Cipher(algorithms.AES(aes_key),
                    modes.CBC(iv),
                    backend=default_backend())
    encryptor = cipher.encryptor()
    msg_len = struct.pack('>i', len(msg))
    msg_encrypt = base64.b64encode(encryptor.update(os.urandom(16) + msg_len + msg + key))
    return msg_encrypt


@all_bytes_parameters
def decrypt(encoding_aes_key, msg_encrypt):
    aes_key = base64.b64decode(encoding_aes_key + b'=')
    iv = aes_key[:16]
    cipher = Cipher(algorithms.AES(aes_key),
                    modes.CBC(iv),
                    backend=default_backend())
    decryptor = cipher.decryptor()
    decrypted = decryptor.update(base64.b64decode(msg_encrypt))
    msg_len = struct.unpack('>i', decrypted[16:20])[0]
    msg = decrypted[20:20 + msg_len]
    return msg


@all_bytes_parameters
def get_callback_signature(token, timestamp, nonce, msg_encrypt):
    data = b''.join(sorted([token, timestamp, nonce, msg_encrypt]))
    signature = hashlib.sha1(data).hexdigest()
    return signature
