"""
逾期接口，document：https://docs.xinyan.com/docs/fxda-overdue?token=C4GkV156z48h
申请雷达：https://docs.xinyan.com/docs/credit-apply?token=qTb2s8VArJ20

resp
{
    "success": false,
    "data":null,
    "errorCode":"S1000",
    "errorMsg":"请求参数有误"
}

"""
import base64
import json
from typing import Dict

import M2Crypto
import requests
from nezha.errors import IncomingDataError,RequestFailed
from nezha.file import File
from nezha.hash import hash_md5
from nezha.ustring import random_key, is_invalid_str
from nezha.utime import strftime

THIS_DIR = File.this_dir(__file__)


class RsaUtil:

    def __init__(self, private_key: str, current_path: bool = False):
        self.private_key_full_path = File.join_path(THIS_DIR, private_key) if current_path else private_key
        self.private_key = M2Crypto.RSA.load_key(self.private_key_full_path)

    def encrypt(self, digest: str):
        digest = base64.b64encode(digest.encode('utf-8'))
        result = ""
        while (len(digest) > 117):
            some = digest[0:117]
            digest = digest[117:]
            result += self.private_key.private_encrypt(some, M2Crypto.RSA.pkcs1_padding).hex()

        result += self.private_key.private_encrypt(digest, M2Crypto.RSA.pkcs1_padding).hex()

        return result


def xinyan_base(form: Dict,
                url: str,
                private_key_path: str) -> Dict:
    print('原始入参:', locals())
    try:
        form = form.copy()
        form['data_content'] = RsaUtil(private_key_path).encrypt(json.dumps(form['data_content']))
    except IncomingDataError as e:
        return {
            "success": False,
            "data": str(e),
            "errorCode": "S1000",
            "errorMsg": "请求参数有误"
        }
    print('request xinyan_overdue form data', form)
    response = requests.post(url, data=form)
    if not response.ok:
        raise RequestFailed(f'response.status_code {response.status_code} text {response.text}')
    else:
        return response.json()


def xy_overdue_incoming_data(idcard: str, id_name: str, phone_no: str, bankcard_no: str,
                             member_id: str, terminal_id: str) -> Dict:
    for k, v in dict(idcard=idcard, id_name=id_name).items():
        if is_invalid_str(v):
            raise IncomingDataError(f'param {k} value={v} is invalid')
    incoming_data = {
        'member_id': member_id,
        'terminal_id': terminal_id,
        'data_type': 'json',
        'data_content': {
            'member_id': member_id,
            'terminal_id': terminal_id,
            'trans_id': random_key(50),
            'trade_date': strftime(fmt='%Y%m%d%H%M%S'),
            # MD5(MD5为32位小写)
            'id_no': hash_md5(str(idcard)),
            'id_name': hash_md5(str(id_name)),
            # 'phone_no': phone_no, # may empty
            # 'bankcard_no': bankcard_no, # may empty
            'encrypt_type': 'MD5',
            'versions': '1.3.0'
        }
    }
    if not is_invalid_str(phone_no):
        incoming_data['data_content']['phone_no'] = hash_md5(str(phone_no))
    if not is_invalid_str(bankcard_no):
        incoming_data['data_content']['bankcard_no'] = hash_md5(str(bankcard_no))
    return incoming_data


def xy_radar_incoming_data(idcard: str, id_name: str, phone_no: str, bankcard_no: str,
                           member_id: str, terminal_id: str) -> Dict:
    for k, v in dict(idcard=idcard, id_name=id_name).items():
        if is_invalid_str(v):
            raise IncomingDataError(f'param {k} value={v} is invalid')
    incoming_data = {
        'member_id': member_id,
        'terminal_id': terminal_id,
        'data_type': 'json',
        'data_content': {
            'member_id': member_id,
            'terminal_id': terminal_id,
            'trans_id': random_key(50),
            'trade_date': strftime(fmt='%Y%m%d%H%M%S'),
            # MD5(MD5为32位小写)
            'id_no': hash_md5(str(idcard)),
            'id_name': hash_md5(str(id_name)),
            # 'phone_no': phone_no, # may empty
            # 'bankcard_no': bankcard_no, # may empty
            'encrypt_type': 'MD5',
            'versions': '1.3.0'
        }
    }
    if not is_invalid_str(phone_no):
        incoming_data['data_content']['phone_no'] = hash_md5(str(phone_no))
    if not is_invalid_str(bankcard_no):
        incoming_data['data_content']['bankcard_no'] = hash_md5(str(bankcard_no))
    incoming_data['data_content'] = RsaUtil.encrypt(json.dumps(incoming_data['data_content']))
    return incoming_data


def xinyan_overdue_main(idcard: str,
                        id_name: str,
                        private_key_path: str,
                        url: str = 'https://api.xinyan.com/product/archive/v3/overdue',
                        phone_no: str = '',
                        bankcard_no: str = '',
                        member_id: str = '',
                        terminal_id: str = '') -> Dict:
    form = xy_overdue_incoming_data(idcard=idcard,
                                    id_name=id_name,
                                    phone_no=phone_no,
                                    bankcard_no=bankcard_no,
                                    member_id=member_id,
                                    terminal_id=terminal_id)
    return xinyan_base(form, url, private_key_path)


def xinyan_radar_main(idcard: str,
                      id_name: str,
                      private_key_path: str,
                      url: str = 'https://api.xinyan.com/product/radar/v3/apply',
                      phone_no: str = '',
                      bankcard_no: str = '',
                      member_id: str = '',
                      terminal_id: str = '') -> Dict:
    form = xy_overdue_incoming_data(idcard=idcard,
                                    id_name=id_name,
                                    phone_no=phone_no,
                                    bankcard_no=bankcard_no,
                                    member_id=member_id,
                                    terminal_id=terminal_id)

    return xinyan_base(form, url, private_key_path)
