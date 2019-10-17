import time
from functools import wraps

_cache_map = {}


def cache(func):
    func.__redmin_cache_key = f"{func.__module__}.{func.__name__}-{time.time()}"

    @wraps(func)
    def wrapper(*args, **kwargs):
        key = func.__redmin_cache_key
        if key in _cache_map:
            return _cache_map[key]
        else:
            _cache_map[key] = result = func(*args, **kwargs)
            return result

    return wrapper


def clear_cache(func):
    key = getattr(func, "__redmin_cache_key", None)
    if key and key in _cache_map:
        _cache_map.pop(key)
