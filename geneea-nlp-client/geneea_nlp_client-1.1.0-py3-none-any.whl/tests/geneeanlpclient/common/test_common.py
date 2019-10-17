from typing import Any, NamedTuple
from unittest import TestCase

from geneeanlpclient.common.common import isSequential, toBool, objToStr, objRepr


class ObjOne:
    def __init__(self, a, b, c):
        self.a = a
        self.b = b
        self.c = c

class ObjTwo(NamedTuple):
    x: Any
    y: Any
    z: Any


class TestCommon(TestCase):

    def test_isSequential(self):
        self.assertTrue(isSequential([1, 2, 3, 4, 5]))
        self.assertTrue(isSequential([-1, 0, 1]))
        self.assertTrue(isSequential([0]))
        self.assertTrue(isSequential([5]))
        self.assertTrue(isSequential([]))

        self.assertFalse(isSequential([1, 2, 3, 5]))
        self.assertFalse(isSequential([1, 1]))
        self.assertFalse(isSequential([1, 0]))

    def test_toBool(self):
        self.assertTrue(toBool(True))
        self.assertTrue(toBool(' TRUE '))
        self.assertTrue(toBool('true'))
        self.assertTrue(toBool('1'))
        self.assertTrue(toBool(1))

        self.assertFalse(toBool(None))
        self.assertFalse(toBool(False))
        self.assertFalse(toBool('Yes'))
        self.assertFalse(toBool('anything'))
        self.assertFalse(toBool(0))
        self.assertFalse(toBool(2))
        self.assertFalse(toBool([True]))
        self.assertFalse(toBool({'my': 'dict'}))

    def test_objToStr(self):
        self.assertEqual('ObjOne(a="A", b=0.5, c=1)', objToStr(ObjOne('A', 0.5, 1), ('a','b','c')))
        self.assertEqual('ObjOne(c=[1, 2], c=[1, 2])', objToStr(ObjOne('A', None, [1,2]), ('b','c','d','c','b')))
        self.assertEqual('ObjOne(c={\'C\': \'C\'})', objToStr(ObjOne(None, None, {'C':'C'}), ('c','a')))

        self.assertEqual('ObjTwo(x="X", y=0.5, z=1)', objToStr(ObjTwo('X', 0.5, 1), ('x','y','z')))
        self.assertEqual('ObjTwo(z=[1, 2], z=[1, 2])', objToStr(ObjTwo('X', None, [1,2]), ('y','z','w','z','y')))
        self.assertEqual('ObjTwo(z={\'Z\': \'Z\'})', objToStr(ObjTwo(None, None, {'Z':'Z'}), ('z','x')))

    def test_objRepr(self):
        self.assertEqual(__name__ + '.ObjOne(a=\'A\', b=0.5, c=1, c=1)', objRepr(ObjOne('A', 0.5, 1), ('a','b','c','c')))
        self.assertEqual(__name__ + '.ObjOne(b=None, c=[1, 2], d=None)', objRepr(ObjOne('A', None, [1,2]), ('b','c','d')))
        self.assertEqual(__name__ + '.ObjOne(c={\'C\': \'C\'}, a=None)', objRepr(ObjOne(None, None, {'C':'C'}), ('c','a')))

        self.assertEqual(__name__ + '.ObjTwo(x=\'X\', y=0.5, z=1, z=1)', objRepr(ObjTwo('X', 0.5, 1), ('x','y','z','z')))
        self.assertEqual(__name__ + '.ObjTwo(y=None, z=[1, 2], w=None)', objRepr(ObjTwo('X', None, [1,2]), ('y','z','w')))
        self.assertEqual(__name__ + '.ObjTwo(z={\'Z\': \'Z\'}, x=None)', objRepr(ObjTwo(None, None, {'Z':'Z'}), ('z','x')))
