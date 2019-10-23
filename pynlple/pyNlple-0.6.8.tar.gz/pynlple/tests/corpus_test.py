# -*- coding: utf-8 -*-
import unittest

from collections import OrderedDict
from pynlple.data.corpus import StackingSource, DeduplicatingFixedCacheSizeSource


class StackingSourceTest(unittest.TestCase):

    def setUp(self):
        self.source1 = [
            '1', '2', '3'
        ]
        self.source2 = [
            4, 5, 6
        ]

    def test_should_return_all_items_consequently(self):
        stacking_source = StackingSource([self.source1, self.source2])
        expected_items = ['1', '2', '3', 4, 5, 6]

        self.assertEqual(expected_items, [item for item in stacking_source])


class DeduplicatingFixedCacheSizeSourceTest(unittest.TestCase):

    def setUp(self):
        self.source = [1, 1, 2, 2, 3, 1, 2, 4, 5, 1, 1, 2, 2, 3, 3, 4, 6, 7]

    def test_should_yield_deduplicated_no_cache_overflow(self):
        dedup_source = DeduplicatingFixedCacheSizeSource(self.source, cache_size=15)

        expected_result = [1, 2, 3, 4, 5, 6, 7]
        self.assertEqual(expected_result, [i for i in dedup_source])

    def test_should_yield_partially_deduplicated_cache_overflow(self):
        dedup_source = DeduplicatingFixedCacheSizeSource(self.source, cache_size=4, refresh=False)

        expected_result = [1, 2, 3, 4, 5, 1, 2, 3, 4, 6, 7]
        self.assertEqual(expected_result, [i for i in dedup_source])

    def test_should_yield_partially_deduplicated_cache_overflow_refreshing(self):
        dedup_source = DeduplicatingFixedCacheSizeSource(self.source, cache_size=4, refresh=True)

        expected_result = [1, 2, 3, 4, 5, 3, 4, 6, 7]
        self.assertEqual(expected_result, [i for i in dedup_source])

    def test_should_yield_deduplicated_feature_extrator(self):
        dedup_source = DeduplicatingFixedCacheSizeSource(self.source, cache_size=15, feature_extractor=lambda x: x if x <= 4 else 4)

        expected_result = [1, 2, 3, 4]
        self.assertEqual(expected_result, [i for i in dedup_source])


class DeduplicatingSourceSharedCacheTest(unittest.TestCase):

    def setUp(self):
        self.source = [1, 1, 2, 2, 3, 1, 2, 4, 5, 1, 1, 2, 2, 3, 3, 4, 6, 7]
        self.source2 = [8, 1, 8, 9, 2, 9, 10, 3, 10, 10, 8, 8]

    def test_should_yield_deduplicated_single_source_no_cache_overflow(self):
        cache = OrderedDict()
        dedup_source = DeduplicatingFixedCacheSizeSource(self.source, cache, cache_size=15)

        expected_result = [1, 2, 3, 4, 5, 6, 7]
        self.assertEqual(expected_result, [i for i in dedup_source])

    def test_should_yield_deduplicated_single_source_cache_overflow(self):
        cache = OrderedDict()
        dedup_source = DeduplicatingFixedCacheSizeSource(self.source, cache, cache_size=4, refresh=False)

        expected_result = [1, 2, 3, 4, 5, 1, 2, 3, 4, 6, 7]
        self.assertEqual(expected_result, [i for i in dedup_source])

    def test_should_yield_deduplicated_multiple_source_no_cache_overflow(self):
        cache = OrderedDict()
        dedup_source = DeduplicatingFixedCacheSizeSource(self.source, cache, cache_size=15)
        dedup_source2 = DeduplicatingFixedCacheSizeSource(self.source2, cache, cache_size=15)

        expected_result = [1, 2, 3, 4, 5, 6, 7]
        expected_result2 = [8, 9, 10]

        result = list(dedup_source)
        result2 = list(dedup_source2)
        self.assertEqual(expected_result, result)
        self.assertEqual(expected_result2, result2)

    def test_should_yield_deduplicated_multiple_source_cache_overflow(self):
        cache = OrderedDict()
        dedup_source = DeduplicatingFixedCacheSizeSource(self.source, cache, cache_size=4)
        dedup_source2 = DeduplicatingFixedCacheSizeSource(self.source2, cache, cache_size=4)

        expected_result = [1, 2, 3, 4, 5, 1, 2, 3, 4, 6, 7]
        expected_result2 = [8, 1, 9, 2, 10, 3, 8]

        self.assertEqual(expected_result, list(dedup_source))
        self.assertEqual(expected_result2, list(dedup_source2))

    def test_should_yield_deduplicated_multiple_source_cache_overflow_on_second(self):
        cache = OrderedDict()
        dedup_source = DeduplicatingFixedCacheSizeSource(self.source, cache, cache_size=7)
        dedup_source2 = DeduplicatingFixedCacheSizeSource(self.source2, cache, cache_size=7)

        expected_result = [1, 2, 3, 4, 5, 6, 7]
        expected_result2 = [8, 1, 9, 2, 10, 3]

        self.assertEqual(expected_result, list(dedup_source))
        self.assertEqual(expected_result2, list(dedup_source2))
