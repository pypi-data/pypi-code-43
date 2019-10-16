import json
from typing import Dict, Any
from urllib.parse import quote

import requests
from nezha.encryption.aes import AESCrypt
from nezha.encryption.rsa2 import RSAEncryption


class ShenxinBase:

    def __init__(self, rsa_prv_key: str, aes_key: str, company_uuid: str, url: str):
        self.rsa_prv_key: str = rsa_prv_key
        self.aes_key: str = aes_key
        self.company_uuid: str = company_uuid
        self.url: str = url

    @staticmethod
    def sort_dict_value(data_dict: Dict[str, Any]) -> str:
        """
        sort dict value by dict key's order in ascii.
        :param data_dict:
        :return:
        """
        sign_data = ''
        for key in sorted(data_dict.keys()):
            value = data_dict[key]
            if isinstance(value, (dict, list)):
                sign_data += json.dumps(data_dict[key], ensure_ascii=False, sort_keys=True)
            else:
                sign_data += value
        return sign_data

    @property
    def cls_name(self) -> str:
        return ShenxinBase.__name__

    def generate_request_body(self, send_data: Dict[str, Any]) -> str:
        aes_cipher = AESCrypt(self.aes_key)
        s1 = json.dumps(send_data)
        encrypt_biz_data = aes_cipher.encrypt(s1)
        return quote(encrypt_biz_data, safe='')

    def generate_sign(self, send_data: Dict[str, Any]) -> str:
        sorted_biz_data = self.sort_dict_value(send_data)
        sign = RSAEncryption.generate_signature(sorted_biz_data, self.rsa_prv_key)
        return quote(sign, safe='')

    def request(self, send_data: Dict[str, Any]) -> Dict[str, Any]:
        res = requests.post(self.url, json=send_data)
        if not res.ok:
            raise ValueError(f'res.text {res.text} res.status_code {res.status_code} is invalid')
        return res.json()
