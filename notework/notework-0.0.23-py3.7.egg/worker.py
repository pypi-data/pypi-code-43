#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2019/05/08 18:56
# @Author  : niuliangtao
# @Site    :
# @File    : ItemUtils.py
# @Software: PyCharm

import logging

from cryptography.fernet import Fernet

# default_key = Fernet.generate_key()
default_key = b'V3UGi6PXuTcbADXlU1Q2D5rFb8R7J-xr1K_xysew6vU='

logger = logging.getLogger('worker')

__all__ = ['encrypt', 'decrypt']


def encrypt(text, cipher_key=default_key):
    text = text.encode()
    cipher = Fernet(cipher_key)
    encrypted_text = cipher.encrypt(text)

    return encrypted_text


def decrypt(encrypted_text, cipher_key=default_key):
    cipher = Fernet(cipher_key)
    decrypted_text = cipher.decrypt(encrypted_text)

    return decrypted_text.decode()


def test():
    text = 'My super secret message'
    print(encrypt(text))
    print(encrypt(text))
    print(encrypt(text))

    print(decrypt(encrypt(text)))
