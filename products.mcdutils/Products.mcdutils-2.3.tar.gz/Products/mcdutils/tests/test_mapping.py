""" Unit tests for Products.mcdutils.mapping """
import unittest


class MemCacheMappingTests(unittest.TestCase):

    def _getTargetClass(self):
        from Products.mcdutils.mapping import MemCacheMapping
        return MemCacheMapping

    def _makeOne(self, *args, **kw):
        return self._getTargetClass()(*args, **kw)

    def test_conforms_to_IDataManager(self):
        from zope.interface.verify import verifyClass
        from transaction.interfaces import IDataManager
        verifyClass(IDataManager, self._getTargetClass())

    def test___setitem___triggers_register(self):
        mapping = self._makeOne('key', DummyProxy())
        self.assertFalse(mapping._p_changed)
        self.assertFalse(mapping._p_joined)
        mapping['abc'] = 123
        self.assertTrue(mapping._p_changed)
        self.assertTrue(mapping._p_joined)

    def test_has_key(self):
        # Added in for backwards-compatibility under Python 3
        mapping = self._makeOne('key', DummyProxy())

        self.assertFalse(mapping.has_key('foo'))  # NOQA: W601
        mapping['foo'] = 'bar'
        self.assertTrue(mapping.has_key('foo'))  # NOQA: W601

    def test__getstate__and__setstate__(self):
        mapping = self._makeOne('key', DummyProxy())

        self.assertEqual(mapping.__getstate__(), {})
        mapping.__setstate__({'foo': 'bar'})
        self.assertEqual(mapping.__getstate__(), {'foo': 'bar'})

    def test_getContainerKey(self):
        mapping = self._makeOne('key', DummyProxy())

        self.assertEqual(mapping.getContainerKey(), 'key')

    def test_clean(self):
        proxy = DummyProxy()
        proxy._set('key', 'myvalue')
        mapping = self._makeOne('key', proxy)

        self.assertIn('key', proxy._cached)
        mapping._clean()
        self.assertNotIn('key', proxy._cached)

        # Cleaning again won't throw errors
        self.assertIsNone(mapping._clean())

    def test_abort(self):
        proxy = DummyProxy()
        proxy._set('key', 'myvalue')
        mapping = self._makeOne('key', proxy)

        self.assertIn('key', proxy._cached)
        mapping.abort(None)
        self.assertNotIn('key', proxy._cached)

    def test_sortKey(self):
        mapping = self._makeOne('key', DummyProxy())

        self.assertEqual(mapping.sortKey(), 'MemCacheMapping: key')


class DummyClient:
    def _get_server(self, key):
        return self, key


class DummyProxy:

    def __init__(self):
        self._cached = {}

    def _set(self, key, value):
        self._cached[key] = value

    def _clean(self, key):
        try:
            del self._cached[key]
        except KeyError:
            pass

    client = DummyClient()


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(MemCacheMappingTests))
    return suite
