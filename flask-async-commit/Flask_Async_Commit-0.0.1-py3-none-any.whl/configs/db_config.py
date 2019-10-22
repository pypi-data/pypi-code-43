# -*- coding: UTF-8 -*-
from redis import Redis, ConnectionPool, StrictRedis
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import os
import yaml
import base64
from rediscluster import StrictRedisCluster


basedir = os.path.abspath(os.path.dirname(__file__)).split('/')[:-1]
basedir = '/'.join(basedir)


"""
set GLOBAL sql_mode ='STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_AUTO_CREATE_USER,NO_ENGINE_SUBSTITUTION '
# """
with open("config.yaml", "r") as f:
    conf = yaml.safe_load(f.read())
# with open("../config.yaml", "r") as f:
#     conf = yaml.safe_load(f.read())

class DB_Config:
    """通用配置"""
    SQLALCHEMY_TRACK_MODIFICATIONS = False  # 是否追踪数据库的修改
    SQLALCHEMY_COMMIT_ON_TEARDOWN = True
    SQLALCHEMY_POOL_SIZE = 150
    SQLALCHEMY_MAX_OVERFLOW = 20
    SQLALCHEMY_POOL_RECYCLE = 180
    SQLALCHEMY_POOL_TIMEOUT = 180
    SQLALCHEMY_DATABASE_URI = 'mysql://root:sxwldba@192.168.199.208:3800/shopping_mall_test'

    MAX_STAY_TIME = 240  # 最长停留时间, 单位分钟
    REDIS_PARAMS_DICT = dict(host='192.168.199.107', port=20000, db=1)


# # 单节点
# rc = redis.Redis(host="192.168.199.107", port=20000, db=5)

db_config = DB_Config
db = SQLAlchemy()

POOL = ConnectionPool(max_connections=98000, **db_config.REDIS_PARAMS_DICT)
my_cache = StrictRedis(connection_pool=POOL)


if __name__ == '__main__':
    print(db_config.SQLALCHEMY_DATABASE_URI)