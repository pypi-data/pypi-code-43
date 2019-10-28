import datetime

import pytz


class TimezoneUtils:

    @staticmethod
    def utcnow_localize():
        return pytz.utc.localize(datetime.datetime.utcnow())

    @staticmethod
    def as_timezone(dt: datetime, tz: str = 'Asia/Bangkok'):
        if dt.tzinfo is None:
            dt = pytz.utc.localize(dt)

        zone = pytz.timezone(tz)
        return dt.astimezone(zone)
