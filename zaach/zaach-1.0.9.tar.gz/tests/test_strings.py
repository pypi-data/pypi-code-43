import unittest

from zaach import strings


class StringsTestCase(unittest.TestCase):
    def test_lcut_1(self):
        s = "'foo'"
        sub = "'"
        self.assertEqual(strings.lcut(s, sub), "foo'")

    def test_lcut_2(self):
        s = ""
        sub = "'"
        self.assertEqual(strings.lcut(s, sub), "")

    def test_rcut_1(self):
        s = "'foo'"
        sub = "'"
        self.assertEqual(strings.rcut(s, sub), "'foo")

    def test_rcut_2(self):
        s = ""
        sub = "'"
        self.assertEqual(strings.rcut(s, sub), "")

    def test_cut(self):
        s = "'foo'"
        sub = "'"
        self.assertEqual(strings.cut(s, sub), "foo")
