import unittest

from pyaes.Field import GF, modulus
from pyaes.Field import sbox, invsbox


class TestFieldMethods(unittest.TestCase):

    def test_int_nofail(self):
        # Test to make sure all possible ints can be made
        # into GF objects
        for i in range(131_071):
            val = GF(i)
            self.assertIsNotNone(val)
            self.assertIsInstance(val, GF)
            self.assertIsNotNone(val.int)
            self.assertEqual(val.int, i)

    def test_int_fail(self):
        # Test to make sure that -only- ints that are greater than
        # or equal to 0 may be created and not any other data type
        for i in [-1, 'a', True, False, b'help', lambda x: 0, None]:
            self.assertRaises(Exception, GF, i)

    def test_int_extra_paramaters_fail(self):
        # Test to make sure that extra parameters raise an error
        # when trying to create a GF object
        a = [1, 2]
        for i in range(3, 100):
            self.assertRaises(Exception, GF, *a)
            a.append(i)

    def test_mul_nofail(self):
        # Test multiplication to make sure it works as expected
        # Values used calculated with pen & paper first
        param_a = (0, 0, 1, 14)
        param_b = (0, 15, 15, 112)
        param_c = (0, 0, 15, 672)

        for a, b, c in zip(param_a, param_b, param_c):
            self.assertEqual(GF(a) * GF(b), GF(c))

    def test_mul_fail(self):
        # Test multiplication to make sure -only- GF objects
        # can multiply together
        param_a = (0, 1, 12, 143, 16_387)
        param_b = (0, 1, -1, True, False, 'abc', b'abc', (1, 2, 3), (-1, -2, -3))
        for a in param_a:
            for b in param_b:
                self.assertRaises(Exception, GF(a).__mul__, b)

    def test_floordiv_nofail(self):
        param_a = (0, 1, 2, 1, 3, 4, 15, 283)
        param_b = (1, 1, 1, 2, 2, 2, 5, 5)
        param_c = (0, 1, 2, 0, 1, 2, 3, 82)
        for a, b, c in zip(param_a, param_b, param_c):
            self.assertEqual(GF(a) // GF(b), GF(c))

    def test_floordiv_fail(self):
        pass

    def test_mod_nofail(self):
        # Test modulus operations to make sure works as expected
        # Values used calculated with pen & paper first
        param_a = (0, 1, 15, 213)
        param_b = (1, 24, 5, 24)
        param_c = (0, 1, 0, 13)

        for a, b, c in zip(param_a, param_b, param_c):
            self.assertEqual(GF(a) % GF(b), GF(c))

    def test_mod_fail(self):
        # Test modulus to make sure -only- GF objects
        # can multiply together
        param_a = (0, 1, 30, 213)
        param_b = (0, 1, -1, True, False, 'abc', b'abc', (1, 2, 3), (-1, -2, -3))
        for a in param_a:
            for b in param_b:
                self.assertRaises(Exception, GF(a).__mod__, b)

    def test_xor_nofail(self):
        # Test xor operations to make sure works as expected
        # Values used calculated with pen & paper first
        param_a = (0, 1, 15, 170)
        param_b = (0, 1, 120, 340)
        for a in param_a:
            for b in param_b:
                self.assertEqual(GF(a) ^ GF(b), GF(a ^ b))

    def test_xor_fail(self):
        # Test xor to make sure -only- GF objects
        # can multiply together
        param_a = (0, 1, 15, 213)
        param_b = (0, 1, -1, True, False, 'abc', b'abc', (1, 2, 3), (-1, -2, -3))
        for a in param_a:
            for b in param_b:
                self.assertRaises(Exception, GF(a).__xor__, b)

    def test_inverse_nofail(self):
        # Test inversion of GF objects
        # Needs to work for S-box & inverse S-Box operations
        test_param = GF(1)
        # Test to see if GF(i) * (1/GF(i)) == 1
        for i in range(1, 256):
            val = GF(i)
            self.assertEqual(val.mul(val.inverse, modulus), test_param)


class TestSboxFunctions(unittest.TestCase):

    def test_inputs_nofail(self):
        # Test to make sure S-box and inverse S-box
        # are able to cancel each other out
        for i in range(256):
            val = GF(i)
            self.assertEqual(invsbox(sbox(val)), val)

    def test_inputs_fail(self):
        # Test to make sure that only GF objects can be used
        for i in (0, 1, -1, True, False, 'abc', b'abc', (1, 2, 3), (-1, -2, -3)):
            self.assertRaises(Exception, sbox, i)
            self.assertRaises(Exception, invsbox, i)


if __name__ == '__main__':
    # Run all the tests
    Field_Suite = unittest.TestSuite()

    Field_Suite.addTest(TestFieldMethods())
    Field_Suite.addTest(TestSboxFunctions())

    Field_Suite.run(unittest.TestResult())
