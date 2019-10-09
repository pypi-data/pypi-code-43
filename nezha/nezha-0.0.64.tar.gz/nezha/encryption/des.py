import base64
from typing import Union

from pyDes import des, PAD_PKCS5


class DES:

    @staticmethod
    def encrypt(plaintext: str, secret_key: str, to_base64: bool = True) -> Union[str, bytes]:
        """
        DES 加密
        :param plaintext: 原始字符串
        :return: 加密后字符串，16进制
        """
        if len(secret_key) > 8:
            secret_key = secret_key[0:8]
        k = des(secret_key, padmode=PAD_PKCS5)
        en = k.encrypt(plaintext)
        return base64.b64encode(en) if to_base64 else en
