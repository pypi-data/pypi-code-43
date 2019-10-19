from datetime import datetime, timedelta
from unittest import TestCase

from pbp import time_util

TODAY_NORMALIZED = datetime.today().replace(hour=0, minute=0, second=0, microsecond=0)
NEXT_YEAR_NORMALIZED = TODAY_NORMALIZED + timedelta(days=365)


class TimeUtilTest(TestCase):
    def test_get_today(self):
        self.assertEqual(TODAY_NORMALIZED, time_util.get_today())

    def test_get_next_year(self):
        self.assertEqual(NEXT_YEAR_NORMALIZED, time_util.get_next_year())

    def test_get_dates_weekly_single_day(self):
        frequency = "every week until next month"
        expected_day_name = time_util.get_today().day_name()

        dates = time_util.get_dates(frequency)
        self.assertGreater(len(dates), 0)

        for date in dates:
            self.assertEqual(expected_day_name, date.day_name())

    def test_get_dates_weekly_couple_of_day(self):
        frequency = "every week on Friday and Saturday"

        dates = time_util.get_dates(frequency)
        self.assertGreater(len(dates), 0)

        friday = "Friday"
        saturday = "Saturday"
        expected_weekdays = [friday, saturday]
        expected_day = None

        for date in dates:
            weekday = date.day_name()

            self.assertIn(weekday, expected_weekdays)

            if expected_day:
                self.assertEqual(expected_day, weekday)

            expected_day = friday if (weekday == saturday) else saturday

    def test_get_dates_monthly(self):
        frequency = "every month starting on November 5th"

        dates = time_util.get_dates(frequency)
        self.assertGreater(len(dates), 0)

        expected_day = 5

        for date in dates:
            self.assertEqual(expected_day, date.day)
