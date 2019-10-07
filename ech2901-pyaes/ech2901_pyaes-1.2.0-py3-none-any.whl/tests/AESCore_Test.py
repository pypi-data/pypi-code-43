import unittest

from pyaes import AESCore as Core
from pyaes.Field import GF
from pyaes.Key import iter_key


# TODO comment code
# TODO create docstrings
# TODO format according to PEP 8


# Test encryption data from known good inputs
# Test vectors from https://nvlpubs.nist.gov/nistpubs/FIPS/NIST.FIPS.197.pdf
# And
# Test vectors from https://csrc.nist.gov/CSRC/media/Projects/Cryptographic-Algorithm-Validation-Program/documents/aes/AESAVS.pdf


# Helper function to turn inputs from given hex values
# To a list of GF instances
def hex_to_arr(data):
    data = bytes.fromhex(data)
    return [GF(i) for i in data]


class TestEncrypt128(unittest.TestCase):
    def setUp(self):
        self.tests = dict()

        with open('TestVectors/AES_Test_VarText_128.txt', 'r') as file:
            self.tests['Variable Plaintext'] = list()
            key = file.readline()
            for line in file:
                plaintext, expected_ciphertext = line.split(' ')
                self.tests['Variable Plaintext'].append((plaintext, key, expected_ciphertext))

        with open('TestVectors/AES_Test_VarKey_128.txt', 'r') as file:
            self.tests['Variable Key'] = list()
            plaintext = file.readline()
            for line in file:
                key, expected_ciphertext = line.split(' ')
                self.tests['Variable Key'].append((plaintext, key, expected_ciphertext))

    def test_input_1(self):
        plaintext = hex_to_arr(r'00112233445566778899aabbccddeeff')
        key = hex_to_arr(r'000102030405060708090a0b0c0d0e0f')
        expected_out = hex_to_arr(r'69c4e0d86a7b0430d8cdb78070b4c55a')

        test_out = Core.encrypt_128(plaintext, iter_key(key, 128))

        for expected, test in zip(expected_out, test_out):
            self.assertEqual(expected, test)

    def test_variable_plaintext(self):
        for plaintext, key, expected_ciphertext in self.tests['Variable Plaintext']:
            with self.subTest(plaintext=plaintext, key=key, expected_ciphertext=expected_ciphertext):
                test_ciphertext = Core.encrypt_128(hex_to_arr(plaintext), iter_key(hex_to_arr(key), 128))
                for e_item, t_item in zip(hex_to_arr(expected_ciphertext), test_ciphertext):
                    self.assertEqual(e_item, t_item)

    def test_variable_key(self):
        for plaintext, key, expected_ciphertext in self.tests['Variable Key']:
            with self.subTest(plaintext=plaintext, key=key, expected_ciphertext=expected_ciphertext):
                test_ciphertext = Core.encrypt_128(hex_to_arr(plaintext), iter_key(hex_to_arr(key), 128))
                for e_item, t_item in zip(hex_to_arr(expected_ciphertext), test_ciphertext):
                    self.assertEqual(e_item, t_item)


class TestDecrypt128(unittest.TestCase):
    def setUp(self):
        self.tests = dict()

        with open('TestVectors/AES_Test_VarText_128.txt', 'r') as file:
            self.tests['Variable Plaintext'] = list()
            key = file.readline()
            for line in file:
                expected_plaintext, ciphertext = line.split(' ')
                self.tests['Variable Plaintext'].append((expected_plaintext, key, ciphertext))

        with open('TestVectors/AES_Test_VarKey_128.txt', 'r') as file:
            self.tests['Variable Key'] = list()
            plaintext = file.readline()
            for line in file:
                key, expected_ciphertext = line.split(' ')
                self.tests['Variable Key'].append((plaintext, key, expected_ciphertext))

    def test_input_1(self):
        ciphertext = hex_to_arr(r'69c4e0d86a7b0430d8cdb78070b4c55a')
        key = hex_to_arr(r'000102030405060708090a0b0c0d0e0f')
        expected_out = hex_to_arr(r'00112233445566778899aabbccddeeff')

        test_out = Core.decrypt_128(ciphertext, iter_key(key, 128, reverse=True))

        for expected, test in zip(expected_out, test_out):
            self.assertEqual(expected, test)

    def test_variable_plaintext(self):
        for expected_plaintext, key, ciphertext in self.tests['Variable Plaintext']:
            with self.subTest(expected_plaintext=expected_plaintext, key=key, ciphertext=ciphertext):
                test_plaintext = Core.decrypt_128(hex_to_arr(ciphertext), iter_key(hex_to_arr(key), 128, reverse=True))
                for e_item, t_item in zip(hex_to_arr(expected_plaintext), test_plaintext):
                    self.assertEqual(e_item, t_item)

    def test_variable_key(self):
        for expected_plaintext, key, ciphertext in self.tests['Variable Key']:
            with self.subTest(expected_plaintext=expected_plaintext, key=key, ciphertext=ciphertext):
                test_plaintext = Core.decrypt_128(hex_to_arr(ciphertext), iter_key(hex_to_arr(key), 128, reverse=True))
                for e_item, t_item in zip(hex_to_arr(expected_plaintext), test_plaintext):
                    self.assertEqual(e_item, t_item)


class TestEncrypt192(unittest.TestCase):
    def setUp(self):
        self.tests = dict()

        with open('TestVectors/AES_Test_VarText_192.txt', 'r') as file:
            self.tests['Variable Plaintext'] = list()
            key = file.readline()
            for line in file:
                plaintext, expected_ciphertext = line.split(' ')
                self.tests['Variable Plaintext'].append((plaintext, key, expected_ciphertext))

        with open('TestVectors/AES_Test_VarKey_192.txt', 'r') as file:
            self.tests['Variable Key'] = list()
            plaintext = file.readline()
            for line in file:
                key, expected_ciphertext = line.split(' ')
                self.tests['Variable Key'].append((plaintext, key, expected_ciphertext))

    def test_input_1(self):
        plaintext = hex_to_arr(r'00112233445566778899aabbccddeeff')
        key = hex_to_arr(r'000102030405060708090a0b0c0d0e0f1011121314151617')
        expected_out = hex_to_arr(r'dda97ca4864cdfe06eaf70a0ec0d7191')

        test_out = Core.encrypt_192(plaintext, iter_key(key, 192))

        for expected, test in zip(expected_out, test_out):
            self.assertEqual(expected, test)

    def test_variable_plaintext(self):
        for plaintext, key, expected_ciphertext in self.tests['Variable Plaintext']:
            with self.subTest(plaintext=plaintext, key=key, expected_ciphertext=expected_ciphertext):
                test_ciphertext = Core.encrypt_192(hex_to_arr(plaintext), iter_key(hex_to_arr(key), 192))
                for e_item, t_item in zip(hex_to_arr(expected_ciphertext), test_ciphertext):
                    self.assertEqual(e_item, t_item)

    def test_variable_key(self):
        for plaintext, key, expected_ciphertext in self.tests['Variable Key']:
            with self.subTest(plaintext=plaintext, key=key, expected_ciphertext=expected_ciphertext):
                test_ciphertext = Core.encrypt_192(hex_to_arr(plaintext), iter_key(hex_to_arr(key), 192))
                for e_item, t_item in zip(hex_to_arr(expected_ciphertext), test_ciphertext):
                    self.assertEqual(e_item, t_item)


class TestDecrypt192(unittest.TestCase):
    def setUp(self):
        self.tests = dict()

        with open('TestVectors/AES_Test_VarText_192.txt', 'r') as file:
            self.tests['Variable Plaintext'] = list()
            key = file.readline()
            for line in file:
                expected_plaintext, ciphertext = line.split(' ')
                self.tests['Variable Plaintext'].append((expected_plaintext, key, ciphertext))

        with open('TestVectors/AES_Test_VarKey_192.txt', 'r') as file:
            self.tests['Variable Key'] = list()
            plaintext = file.readline()
            for line in file:
                key, expected_ciphertext = line.split(' ')
                self.tests['Variable Key'].append((plaintext, key, expected_ciphertext))

    def test_input_1(self):
        ciphertext = hex_to_arr(r'dda97ca4864cdfe06eaf70a0ec0d7191')
        key = hex_to_arr(r'000102030405060708090a0b0c0d0e0f1011121314151617')
        expected_out = hex_to_arr(r'00112233445566778899aabbccddeeff')

        test_out = Core.decrypt_192(ciphertext, iter_key(key, 192, reverse=True))

        for expected, test in zip(expected_out, test_out):
            self.assertEqual(expected, test)

    def test_variable_plaintext(self):
        for expected_plaintext, key, ciphertext in self.tests['Variable Plaintext']:
            with self.subTest(expected_plaintext=expected_plaintext, key=key, ciphertext=ciphertext):
                test_plaintext = Core.decrypt_192(hex_to_arr(ciphertext), iter_key(hex_to_arr(key), 192, reverse=True))
                for e_item, t_item in zip(hex_to_arr(expected_plaintext), test_plaintext):
                    self.assertEqual(e_item, t_item)

    def test_variable_key(self):
        for expected_plaintext, key, ciphertext in self.tests['Variable Key']:
            with self.subTest(expected_plaintext=expected_plaintext, key=key, ciphertext=ciphertext):
                test_plaintext = Core.decrypt_192(hex_to_arr(ciphertext), iter_key(hex_to_arr(key), 192, reverse=True))
                for e_item, t_item in zip(hex_to_arr(expected_plaintext), test_plaintext):
                    self.assertEqual(e_item, t_item)


class TestEncrypt256(unittest.TestCase):
    def setUp(self):
        self.tests = dict()

        with open('TestVectors/AES_Test_VarText_256.txt', 'r') as file:
            self.tests['Variable Plaintext'] = list()
            key = file.readline()
            for line in file:
                plaintext, expected_ciphertext = line.split(' ')
                self.tests['Variable Plaintext'].append((plaintext, key, expected_ciphertext))

        with open('TestVectors/AES_Test_VarKey_256.txt', 'r') as file:
            self.tests['Variable Key'] = list()
            plaintext = file.readline()
            for line in file:
                key, expected_ciphertext = line.split(' ')
                self.tests['Variable Key'].append((plaintext, key, expected_ciphertext))

    def test_input_1(self):
        plaintext = hex_to_arr(r'00112233445566778899aabbccddeeff')
        key = hex_to_arr(r'000102030405060708090a0b0c0d0e0f101112131415161718191a1b1c1d1e1f')
        expected_out = hex_to_arr(r'8ea2b7ca516745bfeafc49904b496089')

        test_out = Core.encrypt_256(plaintext, iter_key(key, 256))

        for expected, test in zip(expected_out, test_out):
            self.assertEqual(expected, test)

    def test_variable_plaintext(self):
        for plaintext, key, expected_ciphertext in self.tests['Variable Plaintext']:
            with self.subTest(plaintext=plaintext, key=key, expected_ciphertext=expected_ciphertext):
                test_ciphertext = Core.encrypt_256(hex_to_arr(plaintext), iter_key(hex_to_arr(key), 256))
                for e_item, t_item in zip(hex_to_arr(expected_ciphertext), test_ciphertext):
                    self.assertEqual(e_item, t_item)

    def test_variable_key(self):
        for plaintext, key, expected_ciphertext in self.tests['Variable Key']:
            with self.subTest(plaintext=plaintext, key=key, expected_ciphertext=expected_ciphertext):
                test_ciphertext = Core.encrypt_256(hex_to_arr(plaintext), iter_key(hex_to_arr(key), 256))
                for e_item, t_item in zip(hex_to_arr(expected_ciphertext), test_ciphertext):
                    self.assertEqual(e_item, t_item)


class TestDecrypt256(unittest.TestCase):
    def setUp(self):
        self.tests = dict()

        with open('TestVectors/AES_Test_VarText_256.txt', 'r') as file:
            self.tests['Variable Plaintext'] = list()
            key = file.readline()
            for line in file:
                expected_plaintext, ciphertext = line.split(' ')
                self.tests['Variable Plaintext'].append((expected_plaintext, key, ciphertext))

        with open('TestVectors/AES_Test_VarKey_256.txt', 'r') as file:
            self.tests['Variable Key'] = list()
            plaintext = file.readline()
            for line in file:
                key, expected_ciphertext = line.split(' ')
                self.tests['Variable Key'].append((plaintext, key, expected_ciphertext))

    def test_input_1(self):
        ciphertext = hex_to_arr(r'8ea2b7ca516745bfeafc49904b496089')
        key = hex_to_arr(r'000102030405060708090a0b0c0d0e0f101112131415161718191a1b1c1d1e1f')
        expected_out = hex_to_arr(r'00112233445566778899aabbccddeeff')

        test_out = Core.decrypt_256(ciphertext, iter_key(key, 256, reverse=True))

        for expected, test in zip(expected_out, test_out):
            self.assertEqual(expected, test)

    def test_variable_plaintext(self):
        for expected_plaintext, key, ciphertext in self.tests['Variable Plaintext']:
            with self.subTest(expected_plaintext=expected_plaintext, key=key, ciphertext=ciphertext):
                test_plaintext = Core.decrypt_256(hex_to_arr(ciphertext), iter_key(hex_to_arr(key), 256, reverse=True))
                for e_item, t_item in zip(hex_to_arr(expected_plaintext), test_plaintext):
                    self.assertEqual(e_item, t_item)

    def test_variable_key(self):
        for expected_plaintext, key, ciphertext in self.tests['Variable Key']:
            with self.subTest(expected_plaintext=expected_plaintext, key=key, ciphertext=ciphertext):
                test_plaintext = Core.decrypt_256(hex_to_arr(ciphertext), iter_key(hex_to_arr(key), 256, reverse=True))
                for e_item, t_item in zip(hex_to_arr(expected_plaintext), test_plaintext):
                    self.assertEqual(e_item, t_item)

if __name__ == '__main__':

    Core_Suite = unittest.TestSuite()

    Core_Suite.addTest(TestEncrypt128())
    Core_Suite.addTest(TestEncrypt128())

    Core_Suite.addTest(TestEncrypt192())
    Core_Suite.addTest(TestEncrypt192())

    Core_Suite.addTest(TestEncrypt256())
    Core_Suite.addTest(TestEncrypt256())

    Core_Suite.run(unittest.TestResult())
