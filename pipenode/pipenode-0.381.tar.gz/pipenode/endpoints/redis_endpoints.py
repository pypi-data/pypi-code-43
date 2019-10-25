import redis
from typing import List
from ..tasks import Task
from ..clients import RedisMQClient
from . import isInputEndpoint, isOutputEndpoint, isCoroutineInputEndpoint, \
    isCoroutineOutputEndpoint, AbstractInputEndpoint, AbstractOutputEndpoint, \
    AbstractCoroutineInputEndpoint, AbstractCoroutineOutputEndpoint

try:
    from utils.logger import RotatingLogger

    logger = RotatingLogger().logger
except:
    from ..log import logger

__all__ = [
    'RedisInputEndpoint',
    'RedisOutputEndpoint'
]


class RedisInputEndpoint(RedisMQClient, AbstractInputEndpoint):
    """Redis input endpoint"""

    def __init__(self, queue_name: List, direction: str = 'right', **conf):
        if queue_name is None:
            raise ValueError("queue_name must be not None")
        if direction not in ("left", "right"):
            raise ValueError("invalid direction")
        self._queue_name = queue_name
        self._direction = direction
        super(RedisInputEndpoint, self).__init__(**conf.copy())

    def get_queue_name(self):
        return self._queue_name

    def get_direction(self):
        return self._direction

    def get(self, point_name=None):
        assert point_name in self._queue_name, "point must be in self._queue_name"
        # if point_name not in self._queue_name:
        #     raise ValueError('point must be in self._queue_name')
        point_names = self._queue_name if not point_name else [point_name]
        return Task(self._get(point_names, 20))

    def _get(self, queue_names, time_out):
        """Get a message from a list
        """
        while True:
            try:
                if self._direction == "right":
                    data = self._client.brpop(queue_names, time_out)
                else:
                    data = self._client.blpop(queue_names, time_out)
                if data is None:
                    continue
                _, raw_data = data
            except redis.ResponseError as e:
                logger.error('Redis ResponseError')
                self._client.connection_pool.disconnect()
                continue
            except redis.ConnectionError as e:
                logger.error('Redis ConnectionError')
                self._client.connection_pool.disconnect()
                continue
            except redis.TimeoutError as e:
                logger.error('Redis TimeoutError')
                self._client.connection_pool.disconnect()
                continue
            else:
                return raw_data


class RedisOutputEndpoint(RedisMQClient, AbstractOutputEndpoint):
    """Redis output endpoint"""

    def __init__(self, queue_names: List, direction: str = "left", **conf):
        """
        :param direction: left: lpush put into a list, right: rpush put into a list
        """
        if not isinstance(queue_names, (str, list)):
            raise ValueError("queue_names must be a string or a list")
        if direction not in ("left", "right"):
            raise ValueError("invalid direction")
        self._queue_name_ls = [queue_names] if isinstance(
            queue_names, str) else queue_names
        self._direction = direction
        super(RedisOutputEndpoint, self).__init__(**conf.copy())

    def get_queue_name(self):
        return self._queue_name

    def get_direction(self):
        return self._direction

    def put(self, tasks):
        msg_dct = {}
        for queue_name, task in tasks:
            assert queue_name in self._queue_name_ls, "queue_name must be in self._queue_name"
            queue_name = queue_name or self._queue_name_ls[0]
            task_ls = msg_dct.setdefault(queue_name, [])
            task_ls.append(task)
        for queue_name in msg_dct:
            # logger.debug('redis output endpoints que_name:%s, msg:%s' % (queue_name, msg_dct[queue_name]))
            self._put(queue_name, msg_dct[queue_name])
        return True

    def _put(self, queue_name, tasks):
        """Put a message into a list

        Use lpush
        """
        while True:
            try:
                if self._direction == "left":
                    # logger.info('left put: %s, %s'% (queue_name,  [task.get_raw_data() for task in tasks]))
                    self._client.lpush(
                        queue_name, *[task.get_raw_data() for task in tasks])
                else:
                    # logger.info('right put: %s, %s '%(queue_name,  [task.get_raw_data() for task in tasks]))
                    self._client.rpush(
                        queue_name, *[task.get_raw_data() for task in tasks])
            except redis.ResponseError as e:
                logger.error('Redis ResponseError')
                self._client.connection_pool.disconnect()
                continue
                # raise error.MQClientConnectionError()
            except redis.ConnectionError as exc:
                logger.error('Redis ConnectionError')
                self._client.connection_pool.disconnect()
                continue
                # raise error.MQClientConnectionError()
            except redis.TimeoutError as exc:
                logger.error('Redis TimeoutError')
                self._client.connection_pool.disconnect()
                continue
                # raise error.MQClientTimeoutError()
            else:
                return True
