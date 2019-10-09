# -*- coding: utf-8 -*-
import base64
import json
from typing import Any
from typing import Tuple
from typing import Union

from Crypto.Hash import SHA256
from Crypto.PublicKey import RSA
from Crypto.PublicKey.RSA import RsaKey
from Crypto.Signature import pkcs1_15
from nezha.ustring import to_str, to_bytes


class TypeConvertedError(Exception):
    pass


class RSAEncryption(object):
    """
    RSA/SHA256（摘要）
    """

    @staticmethod
    def import_key(rsa_key: str) -> RsaKey:
        return RSA.import_key(rsa_key) if rsa_key.startswith('---') else RSA.importKey(base64.b64decode(rsa_key))

    @staticmethod
    def data2bytes(data: Any) -> bytes:
        try:
            if isinstance(data, (bytes, bytearray)):
                return data
            if isinstance(data, str):
                return to_bytes(data)
            else:
                return to_bytes(json.dumps(data, sort_keys=True))
        except Exception as e:
            raise TypeConvertedError(e)

    @staticmethod
    def generate_pair_keys(length: int = 2048) -> Tuple[str, str]:
        print(f'private key length is {length}')
        p = RSA.generate(bits=length)
        return to_str(p.publickey().export_key()), to_str(p.export_key())

    @classmethod
    def generate_signature(cls, data: Any,
                           raw_private_key: str,
                           hash_type: Any = SHA256,
                           returned_base64: bool = True) -> Union[
        str, bytes]:
        private_key = cls.import_key(raw_private_key)
        data = cls.data2bytes(data)
        msg_hash = hash_type.new(data)
        signature = pkcs1_15.new(private_key).sign(msg_hash)
        return to_str(base64.b64encode(signature)) if returned_base64 else signature

    @classmethod
    def verify_signature(cls, raw_data: str, signature: str, raw_public_key: str) -> bool:
        try:
            public_key = cls.import_key(raw_public_key)
            h = SHA256.new(cls.data2bytes(raw_data))
            # error: error: Argument 1 to "verify" of "PKCS115_SigScheme"
            # has incompatible type "SHA256Hash"; expected Module
            pkcs1_15.new(public_key).verify(h, base64.b64decode(signature))  # type: ignore
            return True
        except (ValueError, TypeError) as e:
            import traceback
            traceback.print_exc()
            return False


if __name__ == '__main__':
    RSAEncryption.generate_pair_keys()
