import json
from typing import Dict, Any, Optional, List, Union, Tuple

import pandas as pd
import requests
from nezha import udict
from nezha.encryption.aes import AESCrypt
from nezha.encryption.rsa2 import RSAEncryption


class BoolDataBase:
    """
    BoolDataBase params frame:
    sign
    biz_data
    institution_id

    BoolDataBase result frame:
    {
        'resp_code':'',
        'resp_data': {},
        "resp_msg": "认证成功",
        "resp_order": "018011562838612454492953",
        "timestamp": "20190711175017"
    }
    """
    urls = {
        'local': 'http://localhost:8000/api/lightning/product/query',
        'sit': 'http://guard.shouxin168.net/api/lightning/product/query',
        'prod': 'https://guard.shouxin168.com/api/lightning/product/query'
    }
    resp_code_biz_data_error = ('SW0017',
                                'SW0018',
                                'SW0019',
                                'SW0020',
                                'SW1009',
                                'SW1010',
                                'SW1011',
                                'SW1012'
                                )
    df_default_header: Tuple[str, ...] = tuple()

    def __init__(self, rsa_prv_key: str, aes_key: str, company_uuid: str, url: str = ''):
        """

        :param rsa_prv_key:
        :param aes_key:
        :param company_uuid:
        :param url:

        self.resp_data is BoolDataBase resp result

        """
        self.url: str = url or self.urls['prod']
        self.rsa_prv_key: str = rsa_prv_key
        self.aes_key: str = aes_key
        self.company_uuid: str = company_uuid
        self.response: Dict = dict()
        self.biz_data: Dict = dict()


    # fix bugs:
    # the code is actually unsafe, please read about Liskov substitution principle for methods.
    # refer url:
    # + https://github.com/python/mypy/issues/1237
    # + https://github.com/python/mypy/issues/6248
    # @classmethod
    # def generate_biz_data(cls, *args: str) -> Dict[str, Any]:
    #     raise NotImplementedError()
    #
    # @property
    # def default_resp_data(self) -> Dict[str, Any]:
    #     raise NotImplementedError()

    # def set_biz_data(self, *args: str) -> 'BoolDataBase':
    #     self.biz_data = self.generate_biz_data(*args)
    #     return self

    def encrypt_biz_data(self, biz_data: Dict[str, str]) -> str:
        sorted_str = json.dumps(biz_data, sort_keys=True)
        return AESCrypt(self.aes_key).encrypt(sorted_str)

    def generate_sign(self, biz_data: Dict[str, str]) -> str:
        sorted_str = udict.Dict(biz_data).sort_keys()
        print('sorted_str ++++++++++', sorted_str)
        sign = RSAEncryption.generate_signature(sorted_str, self.rsa_prv_key)
        if not isinstance(sign, str):
            raise TypeError(f'unexpected {sign} type {type(sign)}')
        return sign

    def request(self, biz_data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        biz_data = biz_data or self.biz_data
        data = {
            'sign': self.generate_sign(biz_data),
            'biz_data': self.encrypt_biz_data(biz_data),
            'institution_id': self.company_uuid,
        }
        resp = requests.post(self.url, data=data)
        if resp.ok:
            self.response = resp.json()
            return self.response
        else:
            raise ValueError(resp.text)

    @staticmethod
    def is_success_request(resp: Dict[str, Any]) -> bool:
        if isinstance(resp, dict) and resp.get('resp_code') == 'SW0000':
            return True
        else:
            print(resp)
            return False
    @classmethod
    def is_incoming_data_resp(cls, resp: Dict[str, Any]) -> bool:
        if isinstance(resp, dict) and resp.get('resp_code') in cls.resp_code_biz_data_error:
            return True
        else:
            return False

    def is_succeed(self, resp: Dict[str, Any] = None) -> bool:
        """
        the function is same to is_success_request,
        but support to chain operate
        :param resp:
        :return:
        """
        response = self.response if resp is None else resp
        return self.is_success_request(response)

    def is_incoming_data_error(self, resp: Dict[str, Any] = None) -> bool:
        response = self.response if resp is None else resp
        return self.is_incoming_data_resp(response)

    def result_as_df(self, valuable_part: Union[List, Dict, None],
                     default_part: Union[List, Dict, None],
                     append_biz_data: bool = True) -> pd.DataFrame:
        """
        transfer booldata result(type dict) to pandas.dataframe
        this method often is used to generate excel.

        :param valuable_part: valuable part of booldata.resp_data
            example: self.response.get('resp_data', {}).get('data_list')
        :param default_part: return default part when valuable_part is empty,
            default value refer to person_law.
        :param append_biz_data: append biz_data to return value
        if data_list is empty, return default_data_list
        if append_biz_data, append biz_data to return value
        :return:
        """
        # valuable = valuable_part or self.response.get('resp_data', {})
        # interface personal_law valuable_part is {'data_list': [], 'total': 0}
        valuable = valuable_part
        valuable = valuable or default_part
        if append_biz_data:
            biz_data = udict.Dict(self.biz_data).remove(('service', 'mode'))
            if isinstance(valuable, list):
                new_valuable = []
                for val_data in valuable:
                    val_data.update(biz_data)
                    new_valuable.append(val_data)
                valuable = new_valuable
            elif isinstance(valuable, dict):
                valuable.update(biz_data)
        try:
            return pd.DataFrame(valuable)
        except ValueError as e:
            return pd.DataFrame(valuable, index=[0])

    # ValueError: If using all scalar values, you must pass an index

    def result_as_df_partial(self, append_biz_data: bool = True) -> pd.DataFrame:
        """
        subclass wrap method result_as_df partially
        :param append_biz_data:
        :return:
        """
        raise NotImplementedError()
