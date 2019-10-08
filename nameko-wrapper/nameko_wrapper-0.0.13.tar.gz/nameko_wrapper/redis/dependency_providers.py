"""
Nameko Redis Dependency Provider
"""
import inspect

import redis

from nameko.extensions import DependencyProvider
from nameko_wrapper.exceptions import SettingMissError
from nameko_wrapper.config import Config


# YAML Setting Name
SETTING_NAME = 'REDIS'


def get_redis_connection(setting=None):
    """获取redis连接"""
    setting = setting if setting else Config()[SETTING_NAME]
    if not setting:
        raise SettingMissError(
            'Redis yaml setting does not exist. Please set right `{}` setting.'.format(SETTING_NAME)
        )

    # 添加响应编码参数
    # setting.update({'decode_responses': True})
    pool = redis.ConnectionPool(**setting)
    # 判断参数非法
    sign = inspect.signature(redis.Redis)
    if sign.parameters.keys() > setting.keys():
        return redis.Redis(connection_pool=pool)
    else:
        raise TypeError(
            '>>> redis setting exists not illegal setting parameters. '
            '{}'.format(setting.keys() - sign.parameters.keys())
        )


class Redis(DependencyProvider):
    """Redis 依赖注入"""
    __setting_name = SETTING_NAME
    __instance = None

    def _setup(self):
        """设置依赖"""
        setting = self.container.config.get(self.__setting_name)
        self.__instance = get_redis_connection(setting)

    def setup(self):
        """设置依赖"""
        self._setup()

    def get_dependency(self, worker_ctx):
        """获取依赖"""
        if self.__instance is None:
            self._setup()

        return self.__instance
