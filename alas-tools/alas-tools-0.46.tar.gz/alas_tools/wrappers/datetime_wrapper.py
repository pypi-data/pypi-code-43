import datetime
import datetime as _datetime
from api_core.common.utils import utc_to_tz, datetime_to_str


class DatetimeWrapper(datetime.datetime):

    @staticmethod
    def x__datetime():
        return _datetime

    @staticmethod
    def get_today(country_code = 'cl'):
        local_now = utc_to_tz(
            datetime.utcnow(), country_code
        ).replace(hour=12, minute=0, second=0)

        return local_now

    @staticmethod
    def get_now(country_code = 'cl'):
        local_now = utc_to_tz(
            datetime.utcnow(), country_code()
        )

        return local_now

    @staticmethod
    def datetime_to_str(dt, format=None):
        return datetime_to_str(dt, format)
