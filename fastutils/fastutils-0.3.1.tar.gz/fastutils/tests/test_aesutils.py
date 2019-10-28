import os
import random
import string
import unittest
from fastutils.aesutils import encrypt
from fastutils.aesutils import decrypt
from fastutils.aesutils import encrypt_and_safeb64encode
from fastutils.aesutils import decrypt_and_safeb64decode
from fastutils.aesutils import encrypt_and_hexlify
from fastutils.aesutils import decrypt_and_unhexlify
from fastutils.aesutils import padding_ansix923
from fastutils.aesutils import remove_padding_ansix923
from fastutils.aesutils import padding_iso10126
from fastutils.aesutils import remove_padding_iso10126

class TestDictUtils(unittest.TestCase):

    def test01(self):
        for length in range(1, 2048):
            data1 = os.urandom(length)
            data2 = encrypt(data1, "1234")
            data3 = decrypt(data2, "1234")
            assert data1 == data3

    def test02(self):
        for length in range(1, 2048):
            data1 = "".join(random.choices(string.ascii_letters, k=length))
            data2 = encrypt_and_safeb64encode(data1, "1234")
            data3 = decrypt_and_safeb64decode(data2, "1234")
            assert data1 == data3

    def test03(self):
        for length in range(1, 2048):
            data1 = "".join(random.choices(string.ascii_letters, k=length))
            data2 = encrypt_and_hexlify(data1, "1234")
            data3 = decrypt_and_unhexlify(data2, "1234")
            assert data1 == data3

    def test04(self):
        for length in range(1, 2048):
            data1 = os.urandom(length)
            data2 = padding_ansix923(data1)
            data3 = remove_padding_ansix923(data2)
            assert data1 == data3

    def test05(self):
        for length in range(1, 2048):
            data1 = os.urandom(length)
            data2 = padding_iso10126(data1)
            data3 = remove_padding_iso10126(data2)
            assert data1 == data3
          

if __name__ == "__main__":
    unittest.main()
