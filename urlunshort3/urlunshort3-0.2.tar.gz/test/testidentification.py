import unittest
from urlunshort3 import UrlUnshortener


class TestResolve(unittest.TestCase):
    def test_is_shortened(self):
        shortener = UrlUnshortener()
        for service in shortener.services:
            assert shortener.is_shortened("http://{}/asdf".format(service)), "http://{}/asdf".format(service)
            assert not shortener.is_shortened("http://{}".format(service)), "http://{}".format(service)


if __name__ == "__main__":
    unittest.main()
