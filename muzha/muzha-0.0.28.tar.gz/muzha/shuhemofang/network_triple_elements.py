from typing import Mapping, Dict, Union

from .base import _request, encrypt


def request(mobile: str,
            idNo: str,
            name: str,
            app_key: str,
            app_secret: str,
            url: str = 'https://api.soohaid.com:8211/api/mobile/factor3_high'
            ) -> Dict:
    """
    >>>s = request('1874******520', '230203******11823', '白*', 'lP5*****','1c8e0f24**********57ada4e13')
    >>>print(s)
    :param mobile: phone
    :param idNo: idcard
    :param name: name
    :param app_key: ask for supplier
    :param app_secret: ask for supplier
    :param url: default
    :return:
     {'result': {'identical': True, 'provider': 1}, 'msg': '请求成功', 'code': '0', 'fee': 1}

    """
    req_data = encrypt(locals(), app_key, app_secret)
    return _request(url, req_data)


def should_pay(response: Mapping) -> bool:
    """
    0 不收费 1 收费
    :param response:
    :return:
    """
    not_pay_flag = "0"
    pay_flag = "1"
    fee = str(response.get('fee', 'not exited'))
    if fee == pay_flag:
        return True
    elif fee == not_pay_flag:
        return False
    else:
        print(f'the value of field fee in response {response} is unexpetd')
        return False


def how_much_should_pay(response: Mapping) -> Union[float, int]:
    """

    filed provider: 1--移动 2--电信 3--联通

    price table
    数盒魔方	运营商3要素	移动0.17元/次
                        联通0.2元/次
                        电信0.13元/次
            银行卡三要素	0.1元/次
            银行卡四要素	0.1元/次
    :param response:
    :return:
    """
    if not should_pay(response):
        return 0
    provider = str(response.get('result', {}).get('provider', 'not existed'))
    price_table = {
        '1': 0.17,
        '2': 0.13,
        '3': 0.2
    }
    try:
        return price_table[provider]
    except KeyError as e:
        raise ValueError(
            f'shuhemofang network_triple_elements response {response} can not count how much should pay. the provider is unexpected')
