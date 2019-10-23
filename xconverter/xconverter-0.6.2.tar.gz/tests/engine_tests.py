import unittest

from converter import engine


class Engine(unittest.TestCase):

    def test_check_support(self):

        result = engine.check_support('erudit_article', 'erudit_ps')

        self.assertIsNone(result)

    def test_check_support_unsupported_exception(self):

        with self.assertRaises(engine.UnsupportedConvertion):
            engine.check_support('erudit_article', 'xxx')
