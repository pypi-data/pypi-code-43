from typing import Mapping, Dict

import requests
from nezha.errors import RequestFailed
from nezha.hash import hash_md5
from nezha.utime import timestamp


def encrypt(biz_data: Mapping, app_key: str, app_secret: str) -> Dict:
    time_str = timestamp(precision='ms', returned_str=True)
    req_data = {
        "appkey": app_key,
        "timestamp": time_str,
        "sign": hash_md5("".join((app_key, app_secret, time_str)))
    }
    req_data.update(biz_data)
    return req_data


def _request(url: str, encrypted_biz_data: Mapping) -> Dict:
    response = requests.post(url, json=encrypted_biz_data)
    if not response.ok:
        raise RequestFailed(f'shuhemofang response status_code {response.status_code}, text is {response.text}')
    return response.json()
