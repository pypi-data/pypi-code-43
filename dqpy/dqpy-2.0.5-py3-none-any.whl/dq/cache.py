import json
from functools import wraps

from dq.redis import init_redis, strval

_redis = init_redis('cache')


def cache(ttl=600, key_func=None):
    """Cache decorator.

    This can be applied to any function that returns a raw or JSON-serializable
    response. To allow caching, the ``cache`` key must be set in the config,
    namely the redis connection for cache.

    If the function has a keyword argument named ``fresh``, then the decorator
    gets a fresh copy when it's set to a truthy value.

    If the function has a keyword argument named ``raw``, then the decorator
    returns the raw (bytes) Redis response as-is, without JSON-deserializing.

    :param number ttl: The TTL in second. Default is 10 minutes.
    :param func key_func: The key function. This function should take the same
        arguments as the wrapped function, and return the corresponding cache
        key as a string.
    """
    def memoize(func):
        @wraps(func)
        def decorated_func(*args, **kwargs):
            if not _redis or not key_func:
                return func(*args, **kwargs)
            key = key_func(*args, **kwargs)
            if not kwargs.get('fresh'):
                resp = _redis.get(key)
                if resp is not None:
                    return resp if kwargs.get('raw') else json.loads(resp)
            resp = func(*args, **kwargs)
            _redis.setex(key, ttl, strval(resp))
            return resp

        return decorated_func
    return memoize
