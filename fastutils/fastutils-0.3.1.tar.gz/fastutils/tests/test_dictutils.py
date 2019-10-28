import unittest
from fastutils.dictutils import deep_merge
from fastutils.dictutils import select
from fastutils.dictutils import update


class TestDictUtils(unittest.TestCase):
    def test01(self):
        data1 = {
            "a": {
                "b": {
                    "c": "c",
                }
            }
        }
        data2 = {
            "a": {
                "b": {
                    "d": "d",
                }
            }
        }
        deep_merge(data1, data2)
        assert data1["a"]["b"]["c"] == "c"
        assert data1["a"]["b"]["d"] == "d"
    
    def test02(self):
        data1 = {
            "a": "a",
        }
        data2 = {
            "a": [1, 2, 3]
        }
        deep_merge(data1, data2)
        assert data1["a"] == [1, 2, 3]

    def test03(self):
        data = {
            "a": {
                "b": {
                    "c": "c",
                }
            }
        }
        assert "b" in select(data, "a")
        assert "c" in select(data, "a.b")
        assert select(data, "a.b.c") == "c"

    def test04(self):
        data = [1, 2, 3]
        assert select(data, "0") == 1

    def test05(self):
        data = {
            "a": [{
                "b": {
                    "c": "c"
                }
            }]
        }
        assert select(data, "a.0.b.c") == "c"

    def test06(self):
        data = {
            "a": [{
                "b": {
                    "c": "c"
                }
            }]
        }
        assert select(data, "a.1") is None

    def test07(self):
        data = {}
        update(data, "a.b.c.d", "d")
        assert select(data, "a.b.c.d") == "d"

    def test08(self):
        data = {}
        update(data, "a.0.c.d", "d")
        assert select(data, "a.0.c.d") == "d"

    def test09(self):
        data = {}
        update(data, "a.1.c.d", "d")
        assert data["a"][0] is None
        assert select(data, "a.1.c.d") == "d"

    def test10(self):
        data = {
            "a": [{
                "c": {
                    "d": "d",
                }
            }]
        }
        update(data, "a.0.c.d", "e")
        assert select(data, "a.0.c.d") == "e"

    def test11(self):
        data = []
        update(data, "5", "e")
        assert select(data, "5") == "e"

    def test12(self):
        data = {
            "a": [{
                "b": {
                    "c": "c",
                }
            }]
        }
        update(data, "a.0.b.d", "d")
        assert select(data, "a.0.b.c") == "c"
        assert select(data, "a.0.b.d") == "d"

if __name__ == "__main__":
    unittest.main()
