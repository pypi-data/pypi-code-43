import redis

from com.fw.base.base_exception import BaseException
from com.fw.base.base_log import logger
from com.fw.system.red_conf import system_conf


class RedisDB(object):

    def __init__(self):
        self.init_pool()

    def init_pool(self):
        if not system_conf.has_group('environment'):
            raise BaseException("没有配置数据库环境...")
        version = system_conf.get_value('environment', 'version')

        key = 'redis' + "_" + version

        if not system_conf.has_group(key):
            logger.warn("-----WARN：没有配置redis -------")
            return

        self.redis_db = redis.Redis(host=system_conf.get_value(key, 'host'), port=system_conf.get_value(key, 'port'),
                                    max_connections=300)
        self.redis_db.get_str = self.get_str
        logger.info("------ redis 初始化成功 ------")

    def get_str(self, name):
        return str(self.redis_db.get(name), encoding="utf8")

redis_db = RedisDB().redis_db
