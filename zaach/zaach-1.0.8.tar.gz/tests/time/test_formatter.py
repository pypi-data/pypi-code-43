import datetime
import unittest

from zaach.time import formatter


class FormatterTests(unittest.TestCase):

    def test_iso_8601_duration_1(self):
        self.assertEqual(
            formatter.iso_8601_duration(0),
            "PT0S"
        )

    def test_iso_8601_duration_2(self):
        self.assertEqual(
            formatter.iso_8601_duration(1),
            "PT1S"
        )

    def test_iso_8601_duration_3(self):
        self.assertEqual(
            formatter.iso_8601_duration(60),
            "PT1M"
        )

    def test_iso_8601_duration_4(self):
        self.assertEqual(
            formatter.iso_8601_duration(70),
            "PT1M10S"
        )

    def test_iso_8601_duration_5(self):
        self.assertEqual(
            formatter.iso_8601_duration(3600),
            "PT1H"
        )

    def test_iso_8601_duration_6(self):
        self.assertEqual(
            formatter.iso_8601_duration(3610),
            "PT1H10S"
        )

    def test_iso_8601_duration_7(self):
        self.assertEqual(
            formatter.iso_8601_duration(3660),
            "PT1H1M"
        )

    def test_iso_8601_duration_8(self):
        self.assertEqual(
            formatter.iso_8601_duration(3661),
            "PT1H1M1S"
        )

    def test_timestamp_1(self):
        ts = formatter.timestamp()
        self.assertTrue(ts)

    def test_timestamp_2(self):
        ts = formatter.timestamp(datetime.datetime(1970, 1, 1))
        self.assertEqual(ts, 0)

    def test_timestamp_3(self):
        if hasattr(datetime.datetime, 'timestamp'):  # python3
            ts1 = formatter.timestamp()
            ts2 = datetime.datetime.timestamp(datetime.datetime.utcnow())
            self.assertTrue((ts2 - ts1) < 1)


if __name__ == '__main__':
    unittest.main()
