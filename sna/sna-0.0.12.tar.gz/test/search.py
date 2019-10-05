import unittest


class SnaTest(unittest.TestCase):
    def test_importability(self):
        import sna
        from sna import search
        from sna.search import Sna
        from sna.search import Search


if __name__ == "__main__":
    unittest.main()
