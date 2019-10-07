import unittest

from mock import MagicMock

from cloudshell.firewall.fortinet.helpers.cached_property import cached_property


class TestCachedProperty(unittest.TestCase):
    def setUp(self):
        mock_result = MagicMock()
        mock_func = MagicMock(return_value=mock_result)

        class A(object):
            @cached_property
            def b(self):
                return mock_func()
        self.mock_result = mock_result
        self.mock_func = mock_func
        self.a = A()
        self.class_a = A

    def test_cached_property(self):
        self.assertEqual(self.mock_result, self.a.b)
        _ = self.a.b
        _ = self.a.b
        self.mock_func.assert_called_once()

    def test_delete_cache(self):
        self.assertEqual(self.mock_result, self.a.b)
        self.mock_func.assert_called_once()
        del self.a.b

        self.assertEqual(self.mock_result, self.a.b)
        self.assertEqual(2, self.mock_func.call_count)

    def test_class_returns(self):
        self.assertIsInstance(self.class_a.b, cached_property)
