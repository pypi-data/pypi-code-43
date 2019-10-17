import unittest
import logging
from urlunshort3 import UrlUnshortener

# all of these should resolve to https://github.com/remotephone/urlunshort3

class TestResolve(unittest.TestCase):
    shortener = UrlUnshortener()

    def test_generic(self):
        logging.info("Testing generic url resolution")
        shortener = UrlUnshortener(tricks=True)
        urls = ["https://bit.ly/2nBRa1c", "https://tinyurl.com/yyucc4ph", "https://is.gd/gPqAfb", "https://t.co/202LlppKBL", "https://tiny.cc/d0efez"]
        for url in urls:
            dst = shortener.resolve_short(url)
            self.assertEqual(dst, "https://github.com/remotephone/urlunshort3")

    def test_404(self):
        logging.info("Testing known 404")
        shortener = UrlUnshortener()
        assert shortener.resolve_short("http://example.org/adsfasd.fasdfasads,masdf") == None

    def test_bad_host(self):
        logging.info("Testing known bad host")
        shortener = UrlUnshortener()
        assert shortener.resolve_short("http://alewklfafadsfaewfadasfa/foo") == None


if __name__ == "__main__":
    unittest.main()
