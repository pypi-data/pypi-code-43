import json
import logging

import redis

from dq.config import Config
from dq.logging import error

logger = logging.getLogger(__name__)


def init_redis(key):
    """Initialize a Redis connection.

    :param string key: The config key. The entry should at least contain the
        host, port and db number of the instance.
    :returns redis: The redis instance if the config exists and is valid, and
        None otherwise.
    """
    cfg = Config.get(key)
    if not cfg:
        return None
    try:
        i = redis.Redis(**cfg)
        # This will attempt to connect to Redis and throw an error if the
        # connection is invalid.
        i.info()
        return i
    except Exception:
        error(logger, 'Unable to connect to Redis', None)
        return None


def strval(value):
    """JSON serialize value as appropriate.

    This function should only be used internally.

    :param dict|list|string|number value: An input value.
    :returns string: The output value, suitable for saving by Redis. If
        ``value`` is a ``dict`` or ``list``, it will be JSON-serialized.
        Otherwise it will be left as-is. Note that while Redis only takes
        string values, numbers have their string values be themselves in
        strings, and the conversion will be done by Redis automatically.
    """
    return json.dumps(value) if isinstance(value, (list, dict)) else value


def strvals(*values):
    """JSON serialize values as appropriate.

    This function should only be used internally.

    :param ...dict|list|string|number values: Input values.
    :returns list<string>: The output values. See docs for ``strval`` for
        more explanations.
    """
    return [strval(v) for v in values]


class Redis(object):

    _instance = init_redis('redis')

    @classmethod
    def exists(cls, key):
        """Whether the key exists in Redis.

        :param string key: The Redis key.
        :returns boolean: ``True`` if the key exists, and ``False`` otherwise.
        """
        return cls._instance.exists(key)

    @classmethod
    def get(cls, key):
        """Get the value stored at the key.

        :param string key: The Redis key.
        :returns string: The value of the key. If the key does not exist,
            ``None`` will be returned.
        """
        return cls._instance.get(key)

    @classmethod
    def get_json(cls, key):
        """Get the value stored at the key as JSON.

        :param string key: The Redis key.
        :returns object: The value of the key as an unserialized JSON object.
            If the key does not exist, ``None`` will be returned.
        """
        resp = cls.get(key)
        return json.loads(resp) if resp else None

    @classmethod
    def set(cls, key, value):
        """Set the key to the specified value.

        :param string key: The Redis key.
        :param string value: The value to set. If this is not a string, it will
            be casted to a string.
        :returns boolean: ``True`` if the operation is successful.
        """
        return cls._instance.set(key, strval(value))

    @classmethod
    def setex(cls, key, value, second):
        """Set the key to the specified value, with an expiration time.

        :param string key: The Redis key.
        :param string value: The value to set.
        :param int second: The TTL in second.
        :returns boolean: ``True`` if the operation is successful.
        """
        return cls._instance.setex(key, second, strval(value))

    @classmethod
    def expire(cls, key, second):
        """Set the key to expire in specified second.

        :param string key: The key to set expire.
        :param int second: The number of seconds for the key to live.
        :returns boolean: True if the operation is successful.
        """
        return cls._instance.expire(key, second)

    @classmethod
    def rpush(cls, key, *values):
        """Add values to a Redis list from the end.

        The ``values`` argument is a variable-length array and can be
        specified as follows:

        .. code-block:: python

           redis.rpush('danqing', 'val1', 'val2')
           redis.rpush('danqing', 'val1')
           redis.rpush('danqing', 'val1', 'val2', 'val3')

        :param string key: The key of the list. If the list does not exist yet,
            it will be created.
        :param string... values: A list of values to insert. If any is not a
            string, it will be casted to a string.
        :returns int: The total number of elements in the list after the push.
        """
        return cls._instance.rpush(key, *strvals(*values))

    @classmethod
    def delete(cls, key):
        """Delete the key from Redis.

        :param string key: The key to delete.
        :returns int: The number of items deleted. If 1, the key is found and
            deleted. If 0, the key is not found and nothing is done.
        """
        return cls._instance.delete(key)

    @classmethod
    def hgetall(cls, key):
        """Get the hash table at the specified key.

        :param string key: The key to fetch.
        :returns dict: The hash table at the specified key. If no hash table
            found (i.e. key not found), an empty dictionary is returned.
        :raises redis.ResponseError: If ``key`` holds something other than a
            hash table.
        """
        return cls._instance.hgetall(key)

    @classmethod
    def hget(cls, key, hash_key):
        """Get the value for a hash key in the hash table at the specified key.

        :param string key: The key to fetch.
        :param string hash_key: The hash key to fetch value for in the hash
            table.
        :returns string: The value corresponding to the hash key in the hash
            table. If either ``key`` or ``hash_key`` is not found, ``None`` is
            returned.
        :raises redis.ResponseError: If ``key`` holds something other than a
            hash table.
        """
        return cls._instance.hget(key, hash_key)

    @classmethod
    def hset(cls, key, hash_key, hash_value):
        """Set the value for a hash key in the hash table at the specified key.

        :param string key: The key of the hash table. If the hash table does
            not exist yet, it will be created.
        :param string hash_key: The hash key to set value for in the hash
            table.
        :param string hash_value: The value to set to the key. If this is not
            a string, it will be casted to a string.
        :returns int: The number of new fields. If 1, a new field is added
            (``hash_key`` is new). If 0, ``hash_key`` already exists and its
            value is updated.
        :raises redis.ResponseError: If ``key`` holds something other than a
            hash table.
        """
        return cls._instance.hset(key, hash_key, strval(hash_value))

    @classmethod
    def hdelete(cls, key, *hash_keys):
        """Delete keys from a hash table.

        The ``hash_keys`` argument is a variable-length array and can be
        specified as follows:

        .. code-block:: python

           redis.hdelete('danqing', 'key1', 'key2')
           redis.hdelete('danqing', 'key2')
           redis.hdelete('danqing', 'key1', 'key2', 'key3')

        :param string key: The key of the hash table.
        :param string... hash_keys: A list of hash keys to delete from the hash
            table.
        :returns int: The number of keys actually deleted. If 3 hash keys are
            specified but only 1 is found (and deleted), 1 is returned.
        :raises redis.ResponseError: If ``key`` holds something other than a
            hash table.
        """
        return cls._instance.hdel(key, *hash_keys)

    @classmethod
    def lpeek(cls, key, count):
        """Peek the first count elements in the list without popping.

        :param string key: The key of the array.
        :param int count: The number of elements to peek.
        :returns list: The list of peeked elements.
        """
        return cls._instance.lrange(key, 0, count - 1)

    @classmethod
    def lpop(cls, key, count):
        """Pop the first count elements in the list.

        :param string key: The key of the array.
        :param int count: The number of elements to pop. If there are fewer
            than ``count`` elements, everything will be popped.
        :returns list: The list of popped elements.
        """
        pipe = cls._instance.pipeline()
        pipe.lrange(key, 0, count - 1)
        pipe.ltrim(key, count, - 1)
        result = pipe.execute()
        return result[0] if result[1] else []

    @classmethod
    def atomic_rw(cls, key, evaluator=lambda x: x):
        """Atomically read-write a Redis key.

        :param string key: The key to read/write.
        :param function evaluator: The evaluator function. It takes the
            existing value of the key, and should return the new value. If it
            returns None, no update is done and the operation is considered
            aborted. If not provided, the identity function is used.
        :returns *: The value returned by evaluator. If there's an
            atomicity violation, None is returned.
        :returns boolean: True if there's no atomicity error. That is, this
            value is True if write succeeded or the user aborted, and False if
            there's a atomicity violation (that prevented the write).
        """
        with cls._instance.pipeline() as pipe:
            try:
                pipe.watch(key)
                value = evaluator(pipe.get(key))
                if not value:
                    return None, True
                pipe.multi()
                pipe.set(key, strval(value))
                pipe.execute()
                return value, True
            except redis.WatchError:
                return None, False

    @classmethod
    def atomic_rw_hash(cls, key, hash_key, evaluator=lambda x: x):
        """Atomically read-write a Redis hash key.

        :param string key: The key of the hash to read/write.
        :param string hash_key: The hash key within the hash to read/write.
        :param function evaluator: The evaluator function. It takes the
            existing value of the key, and should return the new value. If it
            returns None, no update is done and the operation is considered
            aborted. If not provided, the identity function is used.
        :returns *: The value returned by evaluator. If there's an
            atomicity violation, None is returned.
        :returns boolean: True if there's no atomicity error. That is, this
            value is True if write succeeded or the user aborted, and False if
            there's a atomicity violation (that prevented the write).
        """
        with cls._instance.pipeline() as pipe:
            try:
                pipe.watch(key)
                value = evaluator(pipe.hget(key, hash_key))
                if not value:
                    return None, True
                pipe.multi()
                pipe.hset(key, hash_key, strval(value))
                pipe.execute()
                return value, True
            except redis.WatchError:
                return None, False
