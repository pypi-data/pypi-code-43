''' Test `dates` module

History:
08-29-2017 - 1.0.0 - Stephen Funkhouser
    Created
'''
__version__ = '1.0.0'
import unittest

from dds_pylib.dates import julian2gregorian, Gregorian


class TestGregorian(unittest.TestCase):
    def test_gregorian_strdate(self):
        self.assertEqual(
            Gregorian(date_str='2-23-2001').strdate(), '2-23-2001'
        )

    def test_gregorian_day(self):
        self.assertEqual(
            Gregorian(date_str='2-23-2001').day, 23
        )

    def test_gregorian_julian(self):
        self.assertEqual(
            Gregorian(date_str='2-23-2001').julian(), 2451964
        )


class TestJulian2Gregorian(unittest.TestCase):
    def test_j2g(self):
        self.assertEqual(
            julian2gregorian(julian=2451964), Gregorian(date_str='2-23-2001')
        )
        self.assertEqual(
            julian2gregorian(julian=2449524), Gregorian(date_str='06-20-1994')
        )
        self.assertEqual(
            julian2gregorian(julian=2457995), Gregorian(date_str='08-29-2017')
        )


if __name__ == '__main__':
    unittest.main()
