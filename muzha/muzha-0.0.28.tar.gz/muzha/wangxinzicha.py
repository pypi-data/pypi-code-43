from typing import Mapping, Dict

import requests


def generate_biz_data(name: str, id_card: str, phone: str) -> Dict:
    return locals()


def request(biz_data: Mapping, url: str = 'https://credit.fanx.xin/portal/index/api_data') -> Dict:
    response = requests.post(url, data=biz_data)
    if response.ok:
        return response.json()
    raise SystemError(f'status_code is {response.status_code}, response.text {response.text}')
