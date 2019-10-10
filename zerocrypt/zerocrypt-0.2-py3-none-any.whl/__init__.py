#!/usr/bin/env python
# -*- coding: utf-8 -*-

from ctypes import cdll, c_int, c_char_p, create_string_buffer, c_bool, sizeof, c_ulong
from sys import platform
from os import path


class Crypto(object):

    def __init__(self):
        self.library = None
        self.lib_file = None
        self.private_key = None
        self.public_key = None
        self.error = ''
        self.signature = None

    def load(self, lib_dir):
        if platform == 'darwin':
            self.lib_file = 'libcrypto.dylib'
        elif platform == 'linux':
            self.lib_file = 'libcrypto.so'
        elif platform == 'win32':
            self.lib_file = 'crypto.dll'

        lib_dir = path.join(lib_dir, self.lib_file)
        self.library = cdll.LoadLibrary(lib_dir)


    def create_keys(self) -> bool:
        func = self.library.gen_keys_pair
        func.restype = c_bool
        func.argtypes = [
            c_char_p, # unsigned char *public_key_buffer
            c_int,    # size_t public_key_sz
            c_char_p, # unsigned char *private_key_buffer
            c_int,    # size_t private_key_sz
            c_char_p, # char *Status = nullptr
            c_int     # size_t StatusSz = 0
        ]
        pub_key = create_string_buffer(32)
        pr_key = create_string_buffer(64)
        buffer_error = create_string_buffer(512)
        result = func(
            pub_key, 32,
            pr_key, 64,
            buffer_error, 512
        )
        self.public_key = pub_key.raw
        self.private_key = pr_key.raw

        self.error = buffer_error.raw.decode("utf-8").rstrip("\x00")
        return result

    def sign(self, data, data_size, pub_key, prv_key):
        func = self.library.sign

        func.restype = c_bool
        func.argtypes = [
            c_char_p, # unsigned char *data
            c_ulong,    # size_t data_sz
            c_char_p, # const unsigned char *public_key
            c_ulong,    # size_t public_key_sz
            c_char_p, # const unsigned char *private_key,
            c_ulong,    # size_t private_key_sz,
            c_char_p, # unsigned char *signature
            c_ulong,    # size_t signature_sz
            c_char_p, # char *Status = nullptr
            c_ulong     # size_t StatusSz = 0
        ]
        buffer_data = create_string_buffer(data_size)
        buffer_pub_key = create_string_buffer(32)
        buffer_prv_key = create_string_buffer(64)
        buffer_signature = create_string_buffer(64)
        buffer_error = create_string_buffer(512)

        buffer_data.value = data
        buffer_pub_key.value = pub_key
        buffer_prv_key.value = prv_key

        result = func(
            buffer_data, sizeof(buffer_data),
            buffer_pub_key, sizeof(buffer_pub_key),
            buffer_prv_key, sizeof(buffer_prv_key),
            buffer_signature, 64,
            buffer_error, sizeof(buffer_error)
        )

        self.signature = buffer_signature.raw
        self.error = buffer_error.raw.decode("utf-8").rstrip("\x00")

        return result

    def verify(self, data, data_sz, pub_key, signature):
        func = self.library.verify
        func.restype = c_bool
        func.argtypes = [
            c_char_p,  # unsigned char *data
            c_int,  # size_t data_sz
            c_char_p,  # const unsigned char *public_key
            c_int,  # size_t public_key_sz
            c_char_p,  # const unsigned char *signature
            c_int,  # size_t signature_sz
            c_char_p,  # char *Status = nullptr
            c_int  # size_t StatusSz = 0
        ]
        buffer_data = create_string_buffer(data_sz)
        buffer_pub_key = create_string_buffer(32)
        buffer_signature = create_string_buffer(64)
        buffer_error = create_string_buffer(512)

        buffer_data.value = data
        buffer_signature.value = signature
        buffer_pub_key.value = pub_key

        result = func(
            buffer_data, sizeof(buffer_data),
            buffer_pub_key, sizeof(buffer_pub_key),
            buffer_signature, sizeof(buffer_signature),
            buffer_error, sizeof(buffer_error)
        )

        self.error = buffer_error.raw.decode("utf-8").rstrip("\x00")
        return result


