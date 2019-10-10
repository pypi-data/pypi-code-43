import unittest

from dq import string


class TestString(unittest.TestCase):

    def test_lower_no_punc(self):
        sin = 'Cornell is #1~~!!'
        sout = 'cornell is 1'
        assert string.lower_no_punc(sin) == sout

    def test_random_string(self):
        r1 = string.random_string(8)
        assert len(r1) == 8
        assert r1 != string.random_string(8)

    def test_valid_filename(self):
        assert string.valid_filename('a/b/ha ha.pdf') == 'abha_ha.pdf'

    def test_relative_path(self):
        assert not string.safe_relative_path(None)
        assert not string.safe_relative_path('')
        assert not string.safe_relative_path(123)
        assert string.safe_relative_path('hello')
        assert not string.safe_relative_path('/danqing')
        assert string.safe_relative_path('cornell/no1')
        assert string.safe_relative_path('cornell/no1..')
        assert string.safe_relative_path('cornell/no.1')
        assert string.safe_relative_path('cornell/no..1/forreal')
        assert not string.safe_relative_path('cornell/./no1')
        assert not string.safe_relative_path('cornell/../no1')
        assert not string.safe_relative_path('cornell/..//no1')
        assert not string.safe_relative_path('../danqing')
        assert not string.safe_relative_path('..//danqing')
        assert string.safe_relative_path('./danqing')
        assert not string.safe_relative_path('..')
        assert not string.safe_relative_path('/')
        assert not string.safe_relative_path('//')
        assert not string.safe_relative_path('/..')
        assert not string.safe_relative_path('//..')
        assert not string.safe_relative_path('../')
        assert not string.safe_relative_path('..//')
        assert string.safe_relative_path('cornell/.is/..no1')
