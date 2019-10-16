"""
example response:
{'seqNum': '1219082200000206', 'message': 'TokenKey验证失败', 'status': 5}
"""
import binascii
import json
from typing import Dict, Mapping

import requests
from Crypto.Cipher import AES
from nezha.encryption.aes import AESCrypt
from nezha.hash import hash_md5
from nezha.ustring import to_str, to_bytes


def encrypt(self, data: str) -> str:
    """
    :param data: string: 加密原串
    :return: 加密数据
    """
    padding = self.padding(data)
    cipher = AES.new(self.aes_key, self.mode)
    s = cipher.encrypt(to_bytes(padding))
    base64_encoded = binascii.b2a_hex(s)
    return to_str(base64_encoded)


AESCrypt.encrypt = encrypt


def generate_raw_biz_data(name: str, idCard: str, mobile: str) -> Dict:
    return locals()


def generate_param(raw_biz_data: Mapping, aes_key: str) -> str:
    print('generate_param', locals())
    return AESCrypt(aes_key).encrypt(json.dumps(raw_biz_data, sort_keys=True))


def generate_tokenKey(raw_biz_data: Mapping, url: str, token_id: str) -> str:
    param_string = ','.join(map(lambda x: '='.join(x), sorted(raw_biz_data.items(), key=lambda item: item[0])))
    return hash_md5(''.join((url, token_id, param_string)))


def generate_request_data(param: str, tokenKey: str, appId: str) -> Dict:
    return locals()


def _request(url, data):
    response = requests.post(url, data=data)
    if response.ok:
        return response.json()
    raise SystemError(f'response code {response.status_code} text {response.text}')


def request_assessment_radar(name: str, idcard: str, mobile: str,
                             app_id: str,
                             token_id: str,
                             url: str = 'http://api.tcredit.com/assessment/radar'):
    """
    free called
    :return:
    """
    raw_biz_data = generate_raw_biz_data(name, idcard, mobile)
    raw_biz_data.update(
        {
            'param': generate_param(raw_biz_data, token_id),
            'tokenKey': generate_tokenKey(raw_biz_data, url, token_id),
            'appId': app_id
        })
    return _request(url, raw_biz_data)


def request_credit_probe(name: str, idcard: str, mobile: str,
                         app_id: str,
                         token_id: str,
                         url: str = 'http://api.tcredit.com/integration/creditProbeV3_1'):
    """
    free called
    :return:
    """
    raw_biz_data = generate_raw_biz_data(name, idcard, mobile)
    raw_biz_data.update({
        'tokenKey': generate_tokenKey(raw_biz_data, url, token_id),
        'appId': app_id
    })
    return _request(url, raw_biz_data)
