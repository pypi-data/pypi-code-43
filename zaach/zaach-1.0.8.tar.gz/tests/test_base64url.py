import unittest

from zaach import base64url


class Base64UrlTests(unittest.TestCase):

    def test_encode_drops_padding(self):
        unencoded = 'a'
        encoded = base64url.encode(unencoded)
        expected = 'YQ'
        self.assertEqual(encoded, expected)

    def test_encode_underscore(self):
        unencoded = 'subjects?_d=1'
        encoded = base64url.encode(unencoded)
        expected = 'c3ViamVjdHM_X2Q9MQ'
        self.assertEqual(encoded, expected)

    def test_encode_minus(self):
        unencoded = ''.join([chr(i) for i in range(128)])
        encoded = base64url.encode(unencoded)
        expected = (
            'AAECAwQFBgcICQoLDA0ODxAREhMUFRYXGBkaGxwdHh8gISIjJCUmJygpKissLS4v'
            'MDEyMzQ1Njc4OTo7PD0-P0BBQkNERUZHSElKS0xNTk9QUVJTVFVWV1hZWltcXV5f'
            'YGFiY2RlZmdoaWprbG1ub3BxcnN0dXZ3eHl6e3x9fn8'
        )
        self.assertEqual(encoded, expected)

    def test_decode_adds_padding(self):
        encoded = 'YQ'
        unencoded = base64url.decode(encoded)
        expected = 'a'
        self.assertEqual(unencoded, expected)

    def test_decode_underscore(self):
        encoded = 'c3ViamVjdHM_X2Q9MQ'
        unencoded = base64url.decode(encoded)
        expected = 'subjects?_d=1'
        self.assertEqual(unencoded, expected)

    def test_decode_minus(self):
        encoded = (
            'AAECAwQFBgcICQoLDA0ODxAREhMUFRYXGBkaGxwdHh8gISIjJCUmJygpKissLS4v'
            'MDEyMzQ1Njc4OTo7PD0-P0BBQkNERUZHSElKS0xNTk9QUVJTVFVWV1hZWltcXV5f'
            'YGFiY2RlZmdoaWprbG1ub3BxcnN0dXZ3eHl6e3x9fn8'
        )
        unencoded = base64url.decode(encoded)
        expected = ''.join([chr(i) for i in range(128)])
        self.assertEqual(unencoded, expected)
