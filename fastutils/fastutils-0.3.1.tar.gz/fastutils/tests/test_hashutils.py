import unittest
from fastutils.hashutils import get_md5
from fastutils.hashutils import get_sha1
from fastutils.hashutils import get_sha1_base64
from fastutils.hashutils import get_pbkdf2_hmac
from fastutils.hashutils import get_pbkdf2_sha256
from fastutils.hashutils import validate_pbkdf2_sha256
from fastutils.hashutils import get_pbkdf2_md5
from fastutils.hashutils import validate_pbkdf2_md5

class TestListUtils(unittest.TestCase):

    def test01(self):
        text = get_md5()
        assert text == "d41d8cd98f00b204e9800998ecf8427e"

    def test02(self):
        text = get_md5("a")
        assert text == "0cc175b9c0f1b6a831c399e269772661"

    def test03(self):
        text = get_md5("a", "b")
        assert text == "187ef4436122d1cc2f40dc2b92f0eba0"

    def test04(self):
        text = get_md5("a", "b", 1)
        assert text == "68b6a776378decbb4a79cda89087c4ce"

    def test05(self):
        text = get_sha1("a", 1, True)
        assert text == "3251aeb0f68984b60d7cb2ed7f2505bee819a7c7"
    
    def test06(self):
        text = get_sha1_base64("a", 1, True, 0.01)
        assert text == "yrZxIUBkyZ03qTIMbYORcBdnFRc="

    def test07(self):
        text = get_pbkdf2_hmac("testpassword", salt="bPBMORgAZP53", iterations=150000, hash_name="sha256")
        assert text == "pbkdf2_sha256$150000$bPBMORgAZP53$yPCstMcQYC9Rgn0h2mT0egPjUdW5T7WUiViib9Sn0dM="

    def test08(self):
        text = get_pbkdf2_sha256("testpassword", salt="bPBMORgAZP53", iterations=150000)
        assert text == "pbkdf2_sha256$150000$bPBMORgAZP53$yPCstMcQYC9Rgn0h2mT0egPjUdW5T7WUiViib9Sn0dM="
  
    def test09(self):
        text = get_pbkdf2_sha256("just a test")
        assert validate_pbkdf2_sha256("just a test", text)

    def test10(self):
        text = get_pbkdf2_md5("just a test")
        assert validate_pbkdf2_md5("just a test", text)


if __name__ == "__main__":
    unittest.main()
