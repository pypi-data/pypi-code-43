import json
import os
import csv
import boto3
import requests
import base64
import hashlib
from boto3.s3.transfer import TransferConfig
from Crypto.Cipher import AES
from base64 import b64encode, b64decode
from typing import Union, Optional, List

from django.conf import settings

BUCKET_NAME = settings.BUCKET_NAME
if settings.DASHBOARD_URL.endswith("/"):
    DASHBOARD_URL = settings.DASHBOARD_URL
else:
    DASHBOARD_URL = settings.DASHBOARD_URL + "/"


def get_smart_token(platform: str) -> str:
    """
    :param platform: str (prod or dev)
    :return: str
    """
    url = f'{DASHBOARD_URL}api/smart_tokens/?platform_id={platform}'
    token = settings.EXECUTE_TOKEN
    try:
        r = requests.get(url, headers={"executetoken": token}).json()
    except (requests.ConnectionError, json.JSONDecodeError):
        return 'error'
    return r['token']


def delete_file(filename):
    os.remove(filename)


def write_tsv(filename: str, data: Union[list, dict], fieldnames: Optional[List[str]] = None) -> bool:
    """
    :param filename: str (path to local file)
    :param data: any (serialized data)
    :param fieldnames: list or None (list of fieldsnames)
    :return: bool
    """
    with open(f"{filename}.tsv", 'a') as f:
        if not fieldnames:
            try:
                fieldnames = list(data[0].keys())
            except (ValueError, TypeError, IndexError):
                return False
        writer = csv.DictWriter(f, delimiter='\t', fieldnames=fieldnames)
        writer.writeheader()
        for row in data:
            writer.writerow(row)

    return True


def upload_to_s3(filename: str, folder: str = "stats/") -> dict:
    """
    :param filename: str (path to local file)
    :param folder: str (folder from s3)
    :return: dict
    """
    print(f"=== IN BOTO3 {filename}")
    s3 = boto3.resource('s3')
    GB = 1024 ** 3
    config = TransferConfig(multipart_threshold=int(GB / 3))
    if filename.startswith('/tmp/'):
        s3_filename = filename[5:]
    else:
        s3_filename = filename
    s3.meta.client.upload_file(filename, BUCKET_NAME, f"{folder}{s3_filename}", ExtraArgs={'ACL': 'public-read'},
                               Config=config)

    return {
        "status": "success",
        "s3_filename": s3_filename,
        "s3_folder": folder
    }


def check_file_exist(filename: str, folder: str = "stats/") -> bool:
    """
    :param filename: str
    :param folder: str
    :return: bool
    """
    s3 = boto3.resource('s3')
    bucket = s3.Bucket(BUCKET_NAME)
    if filename.startswith('/tmp/'):
        filename = filename[5:]
    key = folder + filename
    objs = list(bucket.objects.filter(Prefix=key))
    if len(objs) > 0 and objs[0].key == key:
        return True
    else:
        return False


def get_file_link(filename: str, folder: str = 'stats/') -> str:
    """
    :param filename: str
    :param folder: str
    :return: str
    """
    client = boto3.client('s3')
    if filename.startswith('/tmp/'):
        filename = filename[5:]
    filename = f"{folder}{filename}.tsv"
    content = client.head_object(Bucket=BUCKET_NAME, Key=filename)
    bucket_location = client.get_bucket_location(Bucket=BUCKET_NAME)
    filepath = f"https://s3-{bucket_location['LocationConstraint']}.amazonaws.com/{BUCKET_NAME}/{filename}"

    return filepath


def chunks(items: list, step: int):
    """Yield successive n-sized chunks from l."""
    for i in range(0, len(items), step):
        yield items[i: i + step]


def get_full_integrations(platform: str, service_code: str) -> list:
    """
    :param platform: str (prod or dev)
    :param service_code: str (code from integration config)
    :return: list (list of integrations)
    """
    token = get_smart_token(platform)
    url = f'{DASHBOARD_URL}api/get_config_url/'
    dash_response = requests.get(f'{url}?platform_id={platform}').json()
    headers = {"Authorization": token}

    config_url = f'{dash_response["config_url"]}?type__code={service_code}&all=1'
    # print(config_url)

    configs = requests.get(config_url, headers=headers).json()
    results = configs["results"]
    while configs["next"]:
        configs = requests.get(configs["next"], headers=headers).json()
        results.extend(configs["results"])
    return results


def check_entities_equal(db_deal: any, new_deal: any) -> bool:
    """
    :param db_deal: any
    :param new_deal: any
    :return: bool
    """
    db_deal = db_deal.__dict__
    new_deal = new_deal.__dict__
    exclude_fields = ['_state', 'date_time', 'sc_date_time', 'funnel_stage_duration', 'id']
    return all((field, new_deal[field]) in db_deal.items() for field in db_deal if field not in exclude_fields)


def chunk_parts(seq: list, parts: int) -> list:
    """
    :param seq: list
    :param parts: int
    :return: list
    """
    if len(seq) < parts:
        return [seq]
    avg = len(seq) / float(parts)
    out = []
    last = 0.0
    while last < len(seq):
        out.append(seq[int(last):int(last + avg)])
        last += avg
    return out


def delete_s3_file(filename: str, folder: str, suffix: str) -> str:
    """
    :param filename: str
    :param folder: str
    :param suffix: str
    :return: str
    """
    if filename.startswith('/tmp/'):
        filename = filename[5:]
    client = boto3.client('s3')
    content = client.delete_object(Bucket=BUCKET_NAME, Key=f"{folder}{filename}{suffix}")
    return f"{filename} - deleted!"


class Crypt(object):
    def __init__(self, salt='SlTKeYOpHygTYkP3'):
        self.salt = salt
        self.enc_dec_method = 'utf-8'

    def encrypt(self, str_to_enc, str_key=settings.SECRET_KEY):
        try:
            aes_obj = AES.new(hashlib.sha256(str_key.encode()).digest(), AES.MODE_CFB, self.salt)
            hx_enc = aes_obj.encrypt(str_to_enc)
            mret = b64encode(hx_enc).decode(self.enc_dec_method)
            mret = mret.replace('/', '-_-')
            return mret
        except ValueError as value_error:
            if value_error.args[0] == 'IV must be 16 bytes long':
                raise ValueError('Encryption Error: SALT must be 16 characters long')
            elif value_error.args[0] == 'AES key must be either 16, 24, or 32 bytes long':
                raise ValueError('Encryption Error: Encryption key must be either 16, 24, or 32 characters long')
            else:
                raise ValueError(value_error)

    def decrypt(self, enc_str, str_key=settings.SECRET_KEY):
        try:
            enc_str = enc_str.replace('-_-', '/')
            aes_obj = AES.new(hashlib.sha256(str_key.encode()).digest(), AES.MODE_CFB, self.salt)
            str_tmp = b64decode(enc_str.encode(self.enc_dec_method))
            str_dec = aes_obj.decrypt(str_tmp)
            mret = str_dec.decode(self.enc_dec_method)
            return mret
        except ValueError as value_error:
            if value_error.args[0] == 'IV must be 16 bytes long':
                raise ValueError('Decryption Error: SALT must be 16 characters long')
            elif value_error.args[0] == 'AES key must be either 16, 24, or 32 bytes long':
                raise ValueError('Decryption Error: Encryption key must be either 16, 24, or 32 characters long')
            else:
                raise ValueError(value_error)


def encode(string, secret=None):
    if not secret:
        secret = settings.SECRET_KEY
    c = Crypt()
    return c.encrypt(string, secret)


def decode(enc, secret=None):
    if not secret:
        secret = settings.SECRET_KEY
    c = Crypt()
    return c.decrypt(enc, secret)
