import json
import os

import adapay
from adapay.utils import param_handler
from adapay.utils.log_util import log_error

config_path = None
api_key = None
private_key = None
public_key = None
"""
全局的配置字典
{"member_id1":{},
 "member_id2":{},
 "member_id3":{},
   ···
}
"""
global_config_dict = None

from fishbase.fish_logger import set_log_file, set_log_stdout
import logging

log_level = logging.INFO
log_tag = '{adapay}'

base_url = 'https://api.adapay.tech'
connect_timeout = 30


def init_log(console_enable=False, log_file_path=''):
    """
    :param console_enable: 是否在控台输出日志
    :param log_file_path:
    :return:
    """
    if console_enable:
        set_log_stdout()
    if log_file_path:
        set_log_file(log_file_path)


def init_config(member_id, is_prod):
    if not config_path:
        log_error('config_path is empty')
        return

    if not member_id:
        log_error('member_id is empty')
        return

    total_config_dict = adapay.global_config_dict
    if not total_config_dict:
        total_config_dict = dict()

    single_config_dict = total_config_dict.get(member_id)

    if not single_config_dict:
        config_json = param_handler.read_file(config_path + os.sep + member_id + ".json")
        single_config_dict = json.loads(config_json)
        total_config_dict.update({member_id: single_config_dict})

    if is_prod:
        adapay.api_key = single_config_dict.get("api_key_live")
    else:
        adapay.api_key = single_config_dict.get("api_key_test")

    adapay.private_key = single_config_dict.get("rsa_private_key")
    adapay.public_key = single_config_dict.get("rsa_public_key")


__version__ = '1.0.5'

from adapay.api import *
