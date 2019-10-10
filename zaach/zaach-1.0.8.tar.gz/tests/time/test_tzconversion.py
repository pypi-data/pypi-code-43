import datetime
import random
import unittest

from zaach.time import tzconversion


class TimezonConversionTests(unittest.TestCase):

    def test_last_sunday(self):
        for year in range(2011, 2100):
            for month in range(1, 13):
                sunday = tzconversion.get_last_sunday(year, month)
                self.assertEqual(sunday.weekday(), 6)

    def test_reference_against_performant_implementation(self):
        start_year = 1900 + int(random.random() * 300)
        for year in range(start_year, start_year + 2):
            for month in range(1, 13):
                for day in range(1, 29):
                    for hour in range(0, 24):
                        utc_dt = datetime.datetime(
                            year, month, day, hour,
                            int(random.random() * 60),
                            int(random.random() * 60)
                        )
                        offset_ref = tzconversion.get_utc_offset_reference(
                            utc_dt
                        )
                        offset = tzconversion.get_utc_offset(utc_dt)
                        self.assertEqual(offset_ref, offset)

    def test_utcnow_in_local_time(self):
        dt_utc = datetime.datetime.utcnow()
        dt_local = tzconversion.utc_to_cet_or_cest(dt_utc)
        self.assertNotEqual(dt_utc, dt_local)
        self.assertTrue(dt_local > dt_utc)
        self.assertTrue((dt_local - dt_utc).seconds in [3600, 7200])

    def test_reference_cet_to_cest_barriers(self):
        date_tuples_cet_to_cest = [
            (2020, 3, 29), (2019, 3, 31), (2018, 3, 25), (2017, 3, 26),
            (2016, 3, 27), (2015, 3, 29), (2014, 3, 30), (2013, 3, 31),
            (2012, 3, 25), (2011, 3, 27), (2010, 3, 28), (2009, 3, 29),
            (2008, 3, 30), (2007, 3, 25), (2006, 3, 26), (2005, 3, 27),
            (2004, 3, 28), (2003, 3, 30), (2002, 3, 31), (2001, 3, 25),
            (2000, 3, 26), (1999, 3, 28),
        ]
        for year, month, day in date_tuples_cet_to_cest:
            for hour in [0, 1, 2]:
                dt_utc = datetime.datetime(year, month, day, hour)
                dt_local = tzconversion.utc_to_cet_or_cest(dt_utc)
                delta_seconds = (dt_local - dt_utc).seconds
                if hour == 0:
                    self.assertEqual(delta_seconds, 3600)
                else:
                    self.assertEqual(delta_seconds, 7200)

    def test_reference_cest_to_cet_barriers(self):
        date_tuples_cest_to_cet = [
            (2020, 10, 25), (2019, 10, 27), (2018, 10, 28), (2017, 10, 29),
            (2016, 10, 30), (2015, 10, 25), (2014, 10, 26), (2013, 10, 27),
            (2012, 10, 28), (2011, 10, 30), (2010, 10, 31), (2009, 10, 25),
            (2008, 10, 26), (2007, 10, 28), (2006, 10, 29), (2005, 10, 30),
            (2004, 10, 31), (2003, 10, 26), (2002, 10, 27), (2001, 10, 28),
            (2000, 10, 29), (1999, 10, 31),
        ]
        for year, month, day in date_tuples_cest_to_cet:
            for hour in [0, 1, 2]:
                dt_utc = datetime.datetime(year, month, day, hour)
                dt_local = tzconversion.utc_to_cet_or_cest(dt_utc)
                delta_seconds = (dt_local - dt_utc).seconds
                if hour == 0:
                    self.assertEqual(delta_seconds, 7200)
                else:
                    self.assertEqual(delta_seconds, 3600)


if __name__ == '__main__':
    unittest.main()
