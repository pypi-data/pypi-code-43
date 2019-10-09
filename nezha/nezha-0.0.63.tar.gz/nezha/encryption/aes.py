# -*- coding: utf-8 -*-
import base64
import random
import re
import string
from typing import ClassVar
from typing import Pattern

from Crypto.Cipher import AES
from nezha.ustring import to_str, to_bytes


# 参考链接：https://blog.csdn.net/wang_hugh/article/details/83994750

class AESCrypt(object):
    """
    AES/MODE_ECB/pkcs5padding
    :param key: string: aes密钥
    """
    pattern_decrypt: ClassVar[Pattern] = re.compile('[\\x00-\\x08\\x0b-\\x0c\\x0e-\\x1f\n\r\t]')

    def __init__(self, aes_key: str, mode: int = AES.MODE_ECB):
        if not aes_key:
            raise ValueError('Missing `aes_key`.')
        self.aes_key: bytes = to_bytes(aes_key)
        self.mode: int = mode
        self.bs: int = 16

    def padding(self, s: str) -> str:
        return (lambda s: s + (self.bs - len(s) % self.bs) * chr(self.bs - len(s) % self.bs))(s)

    def encrypt(self, data: str) -> str:
        """
        :param data: string: 加密原串
        :return: 加密数据
        """
        padding = self.padding(data)
        cipher = AES.new(self.aes_key, self.mode)
        s = cipher.encrypt(to_bytes(padding))
        base64_encoded = base64.b64encode(s)
        return to_str(base64_encoded)

    def decrypt(self, encrypt_data: str) -> str:
        """
        :param encrypt_data: string: 加密数据
        :return: 加密原串
        """
        cipher = AES.new(self.aes_key, self.mode)
        encrypt_data += (len(encrypt_data) % 4) * '='
        decrypt_data = cipher.decrypt(base64.b64decode(encrypt_data))
        decrypt_data = self.pattern_decrypt.sub('', to_str(decrypt_data))
        return to_str(decrypt_data)

    @staticmethod
    def generate_key() -> str:
        """
        :return: 长度为16的aes_key
        """
        return ''.join(random.sample(string.ascii_letters + string.digits, 16))
