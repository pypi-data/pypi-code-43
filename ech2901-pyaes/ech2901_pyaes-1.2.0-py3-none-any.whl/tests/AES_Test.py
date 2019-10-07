import unittest

from pyaes.AES import ECB
from pyaes.AES import CBC
from pyaes.AES import PCBC
from pyaes.AES import CFB, OFB, CTR




class TestECB(unittest.TestCase):

    def setUp(self):
        self.mode = ECB()
        self.plaintext = b'Hello, world!'
        self.password = b'test key please ignore'
        self.salt = b'No salt please'

    def test_128_base(self):
        # Test for reversibility of encryption

        ciphertext, *_ = self.mode.encrypt(self.plaintext, self.password, 128, salt=self.salt)

        new_plaintext = self.mode.decrypt(ciphertext, self.password, 128, salt=self.salt)

        self.assertEqual(self.plaintext, new_plaintext)

    def test_192_base(self):
        # Test for reversibility of encryption

        ciphertext, *_ = self.mode.encrypt(self.plaintext, self.password, 192, salt=self.salt)

        new_plaintext = self.mode.decrypt(ciphertext, self.password, 192, salt=self.salt)

        self.assertEqual(self.plaintext, new_plaintext)

    def test_256_base(self):
        # Test for reversibility of encryption

        ciphertext, *_ = self.mode.encrypt(self.plaintext, self.password, 256, salt=self.salt)

        new_plaintext = self.mode.decrypt(ciphertext, self.password, 256, salt=self.salt)

        self.assertEqual(self.plaintext, new_plaintext)


class TestCBC(unittest.TestCase):
    def setUp(self):
        self.mode = CBC()
        self.plaintext = b'Hello, world!'
        self.password = b'test key please ignore'
        self.salt = b'No salt please'
        self.iv = b'this is a bad IV'

    def test_128_base(self):
        # Test for reversibility of encryption

        ciphertext, *_ = self.mode.encrypt(self.plaintext, self.password, 128, iv=self.iv, salt=self.salt)

        new_plaintext = self.mode.decrypt(ciphertext, self.password, 128, iv=self.iv, salt=self.salt)

        self.assertEqual(self.plaintext, new_plaintext)

    def test_192_base(self):
        # Test for reversibility of encryption

        ciphertext, *_ = self.mode.encrypt(self.plaintext, self.password, 192, iv=self.iv, salt=self.salt)

        new_plaintext = self.mode.decrypt(ciphertext, self.password, 192, iv=self.iv, salt=self.salt)

        self.assertEqual(self.plaintext, new_plaintext)

    def test_256_base(self):
        # Test for reversibility of encryption

        ciphertext, *_ = self.mode.encrypt(self.plaintext, self.password, 256, iv=self.iv, salt=self.salt)

        new_plaintext = self.mode.decrypt(ciphertext, self.password, 256, iv=self.iv, salt=self.salt)

        self.assertEqual(self.plaintext, new_plaintext)


class TestPCBC(unittest.TestCase):
    def setUp(self):
        self.mode = PCBC()
        self.plaintext = b'Hello, world!'
        self.password = b'test key please ignore'
        self.salt = b'No salt please'
        self.iv = b'this is a bad IV'

    def test_128_base(self):
        # Test for reversibility of encryption

        ciphertext, *_ = self.mode.encrypt(self.plaintext, self.password, 128, iv=self.iv, salt=self.salt)

        new_plaintext = self.mode.decrypt(ciphertext, self.password, 128, iv=self.iv, salt=self.salt)

        self.assertEqual(self.plaintext, new_plaintext)

    def test_192_base(self):
        # Test for reversibility of encryption

        ciphertext, *_ = self.mode.encrypt(self.plaintext, self.password, 192, iv=self.iv, salt=self.salt)

        new_plaintext = self.mode.decrypt(ciphertext, self.password, 192, iv=self.iv, salt=self.salt)

        self.assertEqual(self.plaintext, new_plaintext)

    def test_256_base(self):
        # Test for reversibility of encryption

        ciphertext, *_ = self.mode.encrypt(self.plaintext, self.password, 256, iv=self.iv, salt=self.salt)

        new_plaintext = self.mode.decrypt(ciphertext, self.password, 256, iv=self.iv, salt=self.salt)

        self.assertEqual(self.plaintext, new_plaintext)


class TestCFB(unittest.TestCase):
    def setUp(self):
        self.mode = CFB()
        self.plaintext = b'Hello, world!'
        self.password = b'test key please ignore'
        self.salt = b'No salt please'
        self.iv = b'this is a bad IV'

    def test_128_base(self):
        # Test for reversibility of encryption

        ciphertext, *_ = self.mode.stream(self.plaintext, self.password, 128, iv=self.iv, salt=self.salt)

        new_plaintext, *_ = self.mode.stream(ciphertext, self.password, 128, iv=self.iv, salt=self.salt)

        self.assertEqual(self.plaintext, new_plaintext)

    def test_192_base(self):
        # Test for reversibility of encryption

        ciphertext, *_ = self.mode.stream(self.plaintext, self.password, 192, iv=self.iv, salt=self.salt)

        new_plaintext, *_ = self.mode.stream(ciphertext, self.password, 192, iv=self.iv, salt=self.salt)

        self.assertEqual(self.plaintext, new_plaintext)

    def test_256_base(self):
        # Test for reversibility of encryption

        ciphertext, *_ = self.mode.stream(self.plaintext, self.password, 256, iv=self.iv, salt=self.salt)

        new_plaintext, *_ = self.mode.stream(ciphertext, self.password, 256, iv=self.iv, salt=self.salt)

        self.assertEqual(self.plaintext, new_plaintext)


class TestOFB(unittest.TestCase):
    def setUp(self):
        self.mode = OFB()
        self.plaintext = b'Hello, world!'
        self.password = b'test key please ignore'
        self.salt = b'No salt please'
        self.iv = b'this is a bad IV'

    def test_128_base(self):
        # Test for reversibility of encryption

        ciphertext, *_ = self.mode.stream(self.plaintext, self.password, 128, iv=self.iv, salt=self.salt)

        new_plaintext, *_ = self.mode.stream(ciphertext, self.password, 128, iv=self.iv, salt=self.salt)

        self.assertEqual(self.plaintext, new_plaintext)

    def test_192_base(self):
        # Test for reversibility of encryption

        ciphertext, *_ = self.mode.stream(self.plaintext, self.password, 192, iv=self.iv, salt=self.salt)

        new_plaintext, *_ = self.mode.stream(ciphertext, self.password, 192, iv=self.iv, salt=self.salt)

        self.assertEqual(self.plaintext, new_plaintext)

    def test_256_base(self):
        # Test for reversibility of encryption

        ciphertext, *_ = self.mode.stream(self.plaintext, self.password, 256, iv=self.iv, salt=self.salt)

        new_plaintext, *_ = self.mode.stream(ciphertext, self.password, 256, iv=self.iv, salt=self.salt)

        self.assertEqual(self.plaintext, new_plaintext)


class TestCTR(unittest.TestCase):
    def setUp(self):
        self.mode = CTR()
        self.plaintext = b'Hello, world!'
        self.password = b'test key please ignore'
        self.salt = b'No salt please'
        self.iv = b'this is a bad IV'

    def test_128_base(self):
        # Test for reversibility of encryption

        ciphertext, *_ = self.mode.stream(self.plaintext, self.password, 128, iv=self.iv, salt=self.salt)

        self.mode.reset_counter()

        new_plaintext, *_ = self.mode.stream(ciphertext, self.password, 128, iv=self.iv, salt=self.salt)

        self.assertEqual(self.plaintext, new_plaintext)

    def test_192_base(self):
        # Test for reversibility of encryption

        ciphertext, *_ = self.mode.stream(self.plaintext, self.password, 192, iv=self.iv, salt=self.salt)

        self.mode.reset_counter()

        new_plaintext, *_ = self.mode.stream(ciphertext, self.password, 192, iv=self.iv, salt=self.salt)

        self.assertEqual(self.plaintext, new_plaintext)

    def test_256_base(self):
        # Test for reversibility of encryption

        ciphertext, *_ = self.mode.stream(self.plaintext, self.password, 256, iv=self.iv, salt=self.salt)

        self.mode.reset_counter()

        new_plaintext, *_ = self.mode.stream(ciphertext, self.password, 256, iv=self.iv, salt=self.salt)

        self.assertEqual(self.plaintext, new_plaintext)

if __name__ == '__main__':
    AES_Suite = unittest.TestSuite()

    AES_Suite.addTest(TestECB())
    AES_Suite.addTest(TestCBC())
    AES_Suite.addTest(TestPCBC())
    AES_Suite.addTest(TestCFB())
    AES_Suite.addTest(TestOFB())
    AES_Suite.addTest(TestCTR())

    AES_Suite.run(unittest.TestResult())
