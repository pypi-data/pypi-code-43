import unittest

from dq import cache


class TestCache(unittest.TestCase):

    def test_cache_none(self):
        redis = cache._redis
        cache._redis = None

        def key_func():
            return ''

        @cache.cache(key_func=key_func)
        def some_func():
            return 'hello'

        assert some_func() == 'hello'

        cache._redis = redis

        @cache.cache()
        def some_func_2():
            return 'hello2'

        assert some_func_2() == 'hello2'

    def test_cache_fresh(self):
        value = 'hello'

        def key_func(fresh=False, raw=False):
            return 'cache-fresh-key'

        @cache.cache(key_func=key_func)
        def some_func(fresh=False, raw=False):
            nonlocal value
            if value == 'hello':
                value = 'world'
                return 'hello'
            return value

        assert some_func(fresh=True) == 'hello'
        assert some_func(raw=True) == b'hello'
        assert some_func(fresh=True) == 'world'
