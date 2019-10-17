# !/usr/bin/python
# -*- coding: UTF-8 -*-
"""
Created on MAY 21, 2018
@author: zlh
"""
from rediscluster import StrictRedisCluster
import redis

class RedisClient(object):
    def __init__(self, config):
        if config["mode"] == "cluster":
            self.redis_client = StrictRedisCluster(**config["redis_cluster"])
        elif config["mode"] == "standalone":
            self.redis_client = redis.Redis(**config["redis_standalone"])
        else:
            exit("mode必须为cluster或standalone")
