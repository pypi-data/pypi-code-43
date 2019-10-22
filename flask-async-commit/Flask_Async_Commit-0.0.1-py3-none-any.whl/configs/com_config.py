# -*- coding:utf-8 -*-
# powered by Carlos
# September 5, 2018
import os
import yaml

basedir = os.path.abspath(os.path.dirname(__file__)).split('/')[:-1]
basedir = '/'.join(basedir)
with open("config.yaml", "r") as f:
    conf = yaml.safe_load(f.read())


class ComConfig:
    DEBUG = conf.get('debug', True)
    SECRET_KEY = '\xc7\xab\x94VV\xa4\r\xed\xac\x94u\xfd\xfaTU\x15&\xcc\x80\xc20\xees\xf4'
    MAX_STAY_TIME = 240  # 最长停留时间, 单位分钟
    SCHEDULER_TIMEZONE = 'Asia/Shanghai'



env = os.environ.get('T99ENV') or 'development'
com_config = ComConfig
