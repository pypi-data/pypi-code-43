import unittest

from pyaes.Field import GF
from pyaes.Key import expand_128, expand_192, expand_256


# TODO comment code
# TODO create docstrings

# Tests the key expansion algorithm against
# Known inputs / outputs
# Test vectors from https://www.samiam.org/key-schedule.html


class TestExpand128(unittest.TestCase):

    def setUp(self):
        # Load test parameters from Key_Test_Data_128.txt
        # Store in self.test as a list containing tuples
        # Each test tuple will hold data in format:
        # (Key_To_Expand, Expected_Expanded_Key)

        self.tests = list()
        with open(r'TestVectors/Key_Test_Data_128.txt', 'r') as file:
            for line in file:
                expected = line.split(',')
                given_key = [GF(int(i)) for i in expected[:16]]
                expected = [GF(int(i)) for i in expected]
                self.tests.append((given_key, expected))



    def test_inputs(self):
        # Test known values from sources to make sure key expansion works like it should
        for key, expected in self.tests:
            with self.subTest(f'Test Expanding: ({key}))'):
                test_expansion = expand_128(key)
                for e_key, t_key in zip(expected, test_expansion):
                        self.assertEqual(e_key, t_key)





class TestExpand192(unittest.TestCase):

    def setUp(self):
        # Load test parameters from Key_Test_Data_192.txt
        # Store in self.test as a list containing tuples
        # Each test tuple will hold data in format:
        # (Key_To_Expand, Expected_Expanded_Key)

        self.tests = list()
        with open(r'TestVectors/Key_Test_Data_192.txt', 'r') as file:
            for line in file:
                expected = line.split(',')
                given_key = [GF(int(i)) for i in expected[:24]]
                expected = [GF(int(i)) for i in expected]
                self.tests.append((given_key, expected))



    def test_inputs(self):
        # Test known values from sources to make sure key expansion works like it should
        for key, expected in self.tests:
            with self.subTest(f'Test Expanding: ({key}))'):
                test_expansion = expand_192(key)
                for e_key, t_key in zip(expected, test_expansion):
                        self.assertEqual(e_key, t_key)


class TestExpand256(unittest.TestCase):

    def setUp(self):
        # Load test parameters from Key_Test_Data_256.txt
        # Store in self.test as a list containing tuples
        # Each test tuple will hold data in format:
        # (Key_To_Expand, Expected_Expanded_Key)

        self.tests = list()
        with open(r'TestVectors/Key_Test_Data_256.txt', 'r') as file:
            for line in file:
                expected = line.split(',')
                given_key = [GF(int(i)) for i in expected[:32]]
                expected = [GF(int(i)) for i in expected]
                self.tests.append((given_key, expected))



    def test_inputs(self):
        # Test known values from sources to make sure key expansion works like it should
        for key, expected in self.tests:
            with self.subTest(f'Test Expanding: ({key}))'):
                test_expansion = expand_256(key)
                for e_key, t_key in zip(expected, test_expansion):
                        self.assertEqual(e_key, t_key)


if __name__ == '__main__':
    Key_Suite = unittest.TestSuite()

    Key_Suite.addTest(TestExpand128())
    Key_Suite.addTest(TestExpand192())
    Key_Suite.addTest(TestExpand256())

    Key_Suite.run(unittest.TestResult())
