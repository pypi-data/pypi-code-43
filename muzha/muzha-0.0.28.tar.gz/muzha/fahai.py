"""
fahai response enum:
{'code': 'e', 'msg': '姓名、身份证号不能为空'}
law list:
{'searchSeconds': 0.188, 'count': 0, 'pageNo': 1, 'range': 10, 'entryList': [], 'code': 's'}
"""

from typing import Optional, Mapping
from urllib.parse import urlencode, urljoin

import requests


def generate_url(auth_code: str, api: str, page_number: int = 0, base_url: str = 'http://api.fahaicc.com') -> str:
    args = dict(authCode=auth_code)
    page_number and args.update({'pageNo': page_number})
    return '?'.join((urljoin(base_url, api), urlencode(args)))


def default_header():
    return {
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3",
        "Accept-Encoding": "gzip, deflate",
        "Accept-Language": "en,zh-CN;q=0.9,zh;q=0.8",
        "Cache-Control": "max-age=0",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.169 Safari/537.36"
    }


def fahai_api(key: str) -> str:
    api = {
        "law_list": "/fhfk/person",  # 法律信息列表
        "law_detail": "/fhfk/entry"  # 法律信息详情
    }
    return api.get(key, '')


def _request(url, biz_data, header):
    response = requests.get(url, params=biz_data, headers=header)
    if not response.ok:
        raise SystemError(f'fahai response, code {response.status_code}, data {response.text}')
    return response.json()



def request_law_list(pname: str, idcardNo: str, auth_code: str,
                     api: Optional[str] = None, header: Optional[Mapping] = None):
    url = generate_url(auth_code, api or fahai_api('law_list'))
    return _request(url, {'pname': pname, 'idcardNo': idcardNo}, header or default_header())


if __name__ == '__main__':
    s = request_law_list('张三丰', '230203198602011823', '')
    print(s)
