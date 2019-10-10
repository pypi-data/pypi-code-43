import random
import time
import unittest

from zaach.oop import cache


class CacheObject(cache.CacheMixin, object):
    pass


class CacheTests(unittest.TestCase):

    def test_cache_dict(self):
        co1 = CacheObject()
        co1cache = co1._cache
        self.assertIsInstance(co1cache, dict)

        co2 = CacheObject()
        co2cache = co2._cache
        self.assertIsInstance(co2cache, dict)

        self.assertNotEqual(id(co1cache), id(co2cache))

    def test_cacheget_and_cacheset_with_expiration(self):
        co = CacheObject()
        rnd = random.random()

        self.assertIsNone(co.cacheget('rnd'))
        co.cacheset('rnd', rnd, 0.01)
        self.assertEqual(co.cacheget('rnd'), rnd)
        self.assertEqual(co.cacheget('rnd'), rnd)

        time.sleep(0.01)
        self.assertIsNone(co.cacheget('rnd'))

    def test_cacheget_and_cacheset_without_expiration(self):
        co = CacheObject()
        rnd = random.random()

        self.assertIsNone(co.cacheget('rnd'))
        co.cacheset('rnd', rnd)
        self.assertEqual(co.cacheget('rnd'), rnd)
        self.assertEqual(co.cacheget('rnd'), rnd)


if __name__ == '__main__':
    unittest.main()
