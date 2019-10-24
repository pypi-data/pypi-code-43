from django.core.cache import cache
from functools import wraps
import hashlib
import json


def __sha224(data):
    return hashlib.sha224(data.encode("utf-8")).hexdigest()


def api_cache_global(cache_timeout):
    def _api_cache(func):  # pragma: no cover
        def cache_logic(*argv, **kwargs):
            response = None
            try:
                func_name = func.__name__
                cache_key_args = {"args": argv[2:], "kwargs": kwargs}
                cache_key = __sha224(json.dumps(cache_key_args))
                cached_data = cache.get(func_name)
                if cached_data is None:
                    cached_data = {}
                if cache_key not in cached_data:
                    response = func(*argv, **kwargs)
                    if "status" in response and response["status"] == 200:
                        cached_data[cache_key] = response
                        cache.set(func_name, cached_data, cache_timeout)
                else:
                    response = cached_data[cache_key]
            except ConnectionError:
                response = func(*argv, **kwargs)
            finally:
                return response
        return wraps(func)(cache_logic)
    return _api_cache
