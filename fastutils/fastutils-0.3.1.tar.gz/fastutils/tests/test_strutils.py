import os
import binascii
import base64
import unittest
from fastutils.strutils import split
from fastutils.strutils import str_composed_by
from fastutils.strutils import is_hex_digits
from fastutils.strutils import join_lines
from fastutils.strutils import is_urlsafeb64_decodable
from fastutils.strutils import is_base64_decodable
from fastutils.strutils import is_unhexlifiable
from fastutils.strutils import split
from fastutils.strutils import text_display_length
from fastutils.strutils import text_display_shorten
from fastutils.strutils import wholestrip


class TestStrUtils(unittest.TestCase):

    def test01(self):
        text = "1,2.3,4.5"
        values = split(text, [",", "."])
        assert values == ["1", "2", "3", "4", "5"]

    def test02(self):
        text = "1,  2 .  3 , 4 . 5 "
        values = split(text, [",", "."], strip=True)
        assert values == ["1", "2", "3", "4", "5"]

    def test03(self):
        assert str_composed_by("abc", "abc") is True
        assert str_composed_by("abcd", "abc") is False
        assert str_composed_by("a", "") is False
        assert str_composed_by("aaa", "a") is True
        assert str_composed_by("aaa", "b") is False
        assert str_composed_by("ab", "abc") is True

    def test04(self):
        assert is_hex_digits("") is False
        assert is_hex_digits("0") is True
        assert is_hex_digits("9") is True
        assert is_hex_digits("a") is True
        assert is_hex_digits("f") is True
        assert is_hex_digits("g") is False
        assert is_hex_digits("0123456789abcdefABCDEF") is True

    def test05(self):
        assert join_lines("") == ""
        assert join_lines("a") == "a"
        assert join_lines("a\n") == "a"
        assert join_lines("a\nb") == "ab"
        assert join_lines("a\nb\n") == "ab"
        assert join_lines("a") == "a"
        assert join_lines("a\r") == "a"
        assert join_lines("a\rb") == "ab"
        assert join_lines("a\rb\r") == "ab"
        assert join_lines("a") == "a"
        assert join_lines("a\r\n") == "a"
        assert join_lines("a\r\nb") == "ab"
        assert join_lines("a\r\nb\r\n") == "ab"
        assert join_lines("a\rb\nc\r\n") == "abc"

    def test06(self):
        assert is_urlsafeb64_decodable("") is False
        assert is_urlsafeb64_decodable("a") is False
        assert is_urlsafeb64_decodable("ab") is False
        assert is_urlsafeb64_decodable("abc") is False
        assert is_urlsafeb64_decodable("abcd") is True
        assert is_urlsafeb64_decodable("abcde") is False
        assert is_urlsafeb64_decodable("abcdef") is False
        assert is_urlsafeb64_decodable("abcdefg") is False
        assert is_urlsafeb64_decodable("abcdefgh") is True
        assert is_urlsafeb64_decodable("abcdefghi") is False
        text = base64.urlsafe_b64encode(os.urandom(4096)).decode()
        assert is_urlsafeb64_decodable(text) is True

    def test07(self):
        assert is_base64_decodable("") is False
        assert is_base64_decodable(" ") is False
        assert is_base64_decodable("a") is False
        assert is_base64_decodable("a    ") is False
        assert is_base64_decodable("ab") is False
        assert is_base64_decodable("ab    ") is False
        assert is_base64_decodable("abc") is False
        assert is_base64_decodable("abcd") is True
        assert is_base64_decodable("abcd  ") is True
        assert is_base64_decodable("abcde") is False
        assert is_base64_decodable("abcdef") is False
        assert is_base64_decodable("abcdefg") is False
        assert is_base64_decodable("abcdefgh") is True
        assert is_base64_decodable("abcdefghi") is False
        text = base64.encodebytes(os.urandom(4096)).decode()
        assert is_base64_decodable(text) is True

    def test08(self):
        assert is_unhexlifiable("") is False
        assert is_unhexlifiable("a") is False
        assert is_unhexlifiable("ab") is True
        assert is_unhexlifiable("abc") is False
        assert is_unhexlifiable("abcd") is True
        assert is_unhexlifiable("abcde") is False
        assert is_unhexlifiable("abcdef") is True
        assert is_unhexlifiable("abcdefg") is False
        assert is_unhexlifiable("abcdefgh") is False
        assert is_unhexlifiable("abcdefghi") is False
        text = binascii.hexlify(os.urandom(4096)).decode()
        assert is_unhexlifiable(text) is True

    def test09(self):
        assert split("", ",") == ['']
        assert split("a", ",") == ["a"]
        assert split("a,b", ",") == ["a", "b"]
        assert split("a,b,", ",") == ["a", "b", ""]

    def test10(self):
        assert text_display_length("") == 0
        assert text_display_length("a") == 1
        assert text_display_length("测") == 2
        assert text_display_length("测试") == 4
        assert text_display_length("测试", unicode_display_length=3) == 6
        assert text_display_length("a测试") == 5
        assert text_display_length("ab测试") == 6
        assert text_display_length("ab测试a") == 7
        assert text_display_length("ab测试ab") == 8

    def test11(self):
        assert text_display_shorten("", 5) == ""
        assert text_display_shorten("a", 5) == "a"
        assert text_display_shorten("ab", 5) == "ab"
        assert text_display_shorten("abc", 5) == "abc"
        assert text_display_shorten("abcd", 5) == "abcd"
        assert text_display_shorten("abcde", 5) == "abcde"
        assert text_display_shorten("abcdef", 5) == "ab..."
        assert text_display_shorten("abcdefg", 5) == "ab..."
        assert text_display_shorten("abcdefgh", 5) == "ab..."
        assert text_display_shorten("测", 5) == "测"
        assert text_display_shorten("测测", 5) == "测测"
        assert text_display_shorten("测测测", 5) == "测..."
        assert text_display_shorten("测测测测", 5) == "测..."
        assert text_display_shorten("测测测测测", 5) == "测..."
        assert text_display_shorten("a测", 5) == "a测"
        assert text_display_shorten("a测测", 5) == "a测测"
        assert text_display_shorten("a测测测", 5) == "a..."
        assert text_display_shorten("a测测测测", 5) == "a..."
        assert text_display_shorten("a测测测测测", 5) == "a..."

    def test12(self):
        assert wholestrip("a b") == "ab"
        assert wholestrip(" a b ") == "ab"

if __name__ == "__main__":
    unittest.main()
