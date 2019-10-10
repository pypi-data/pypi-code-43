import unittest

from tests.entities import SimpleEntity


class TestEntity(unittest.TestCase):

    def test_string(self):
        e = SimpleEntity({'name': 'danqing'})
        assert str(e) == "<SimpleEntity {'name': 'danqing'}>"
