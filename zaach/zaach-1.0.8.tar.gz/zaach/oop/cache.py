import time


class CacheMixin:

    @property
    def _cache(self):
        cache_dict = getattr(self, '_cache_dict', None)
        if cache_dict is None:
            cache_dict = dict()
            self._cache_dict = cache_dict
        return cache_dict

    def cacheget(self, key):
        value, expires = self._cache.get(key, (None, None))

        if value is not None and expires is not None and time.time() > expires:
            del self._cache[key]
            value = None

        return value

    def cacheset(self, key, value, seconds=None):
        expires = time.time() + seconds if seconds else None
        self._cache[key] = (value, expires)
        return (value, expires)
