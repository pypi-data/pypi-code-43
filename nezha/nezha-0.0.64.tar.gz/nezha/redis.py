import json
from typing import Any

import redis
from redis.connection import HiredisParser


class Redis:
    def __init__(self, redis_url: str):
        self.r = redis.from_url(redis_url)

    def set(self, name: str, value: Any, expired_time: int = None) -> HiredisParser:
        """
        设置redis键值对
        :param name: 键名
        :param value: 值
        :param expired_time: 有效期
        """
        if not isinstance(value, str):
            value = json.dumps(value)
        return self.r.set(name, value, expired_time)

    def get(self, name: str) -> Any:
        """
        获取redis键值对
        :param name: 键名
        """
        return self.r.get(name)

    def ttl(self, name: str) -> Any:
        """
        获取redis有效期
        :param name: 键名
        :return: 有效期
        """
        return self.r.ttl(name)

    def delete(self, *name: str) -> HiredisParser:
        """
        删除redis键值对
        :param name: 键名
        """
        return self.r.delete(*name)
