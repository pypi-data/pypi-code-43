# coding=utf-8

import datetime
import re


class DateString(str):
    """
    Date string.

    >>> ds = DateString('20180624')
    >>> ds
    '20180624'

    >>> ds = DateString('2018/06/24')
    >>> ds
    '20180624'

    >>> ds = DateString('2018-06-24')
    >>> ds
    '20180624'

    >>> ds = DateString('2018年6月24日')
    >>> ds
    '20180624'

    >>> ds = DateString(datetime.datetime(2018, 6, 24))
    >>> ds
    '20180624'

    >>> begin_ds = DateString('2019-01-01')
    >>> begin_ds
    '20190101'

    >>> end_ds = DateString('2019/1/3')
    >>> end_ds
    '20190103'

    >>> pd.date_range(begin_ds, end_ds)
    DatetimeIndex(['2019-01-01', '2019-01-02', '2019-01-03'], dtype='datetime64[ns]', freq='D')

    """
    def __new__(cls, ds):
        if isinstance(ds, datetime.date):
            ds = ds.strftime('%Y%m%d')
        elif isinstance(ds, str):
            ds = re.sub(
                pattern=r'(\d{4})[^\d](\d{1,2})[^\d](\d{1,2})[^\d]{0,1}',
                repl=lambda m: '%d%02d%02d' % tuple(map(int, m.groups())),
                string=ds
            )
        else:
            raise TypeError(
                "expect 'str', 'datetime.date', 'datetime.datetime', 'pandas.Timestamp', or 'DateString', get '%s'" % type(ds).__name__)
        self = super().__new__(cls, ds)

        try:
            if not self.isdigit() or len(self) != 8:
                raise ValueError
            setattr(self, '__dt', datetime.datetime.strptime(self, '%Y%m%d'))
        except ValueError:
            raise ValueError('unknown date string: %s' % self)

        return self

    @property
    def dt(self):
        return getattr(self, '__dt')

    def __hash__(self):
        return hash(self.__str__())

    def __add__(self, n):
        """
        >>> DateString('2018/6/24') + 90
        '20180922'
        """
        dt = self.dt + datetime.timedelta(n)
        return DateString(dt.strftime('%Y%m%d'))

    def __sub__(self, x):
        """
        >>> DateString('2018-09-22') - 90
        '20180624'

        >>> DateString('2018-09-22') - '2018/06/24'
        90

        >>> DateString('2018/9/22') - datetime.datetime(2018, 6, 24)
        90

        >>> DateString('20180922') - DateString('2018-6-24')
        90

        >>> DateString('2018年9月22日') - pd.Timestamp('2018-06-24')
        90
        """
        if isinstance(x, int):
            return self. __add__(-x)
        if isinstance(x, str):
            return (self.dt - DateString(x).dt).days
        if isinstance(x, datetime.date):
            return (self.dt - x).days
        if isinstance(x, DateString):
            return (self.dt - x.dt).days
        raise TypeError(
            "expect 'str', 'int', 'datetime.date', 'datetime.datetime', 'pandas.Timestamp', or 'DateString', get '%s'" % type(x).__name__)

    def __eq__(self, x):
        """
        >>> DateString('20180922') == '2018/9/22'
        True
        >>> DateString('20180922') == '2018/6/24'
        False
        """
        try:
            return self - x == 0
        except:
            return False

    def __ge__(self, x):
        """
        >>> DateString('20180922') >= '2018/6/24'
        True
        >>> DateString('20180922') >= '2019/9/22'
        False
        """
        return self - x >= 0

    def __gt__(self, x):
        return self - x > 0

    def __le__(self, x):
        return self - x <= 0

    def __lt__(self, x):
        return self - x < 0

    @property
    def year(self):
        """
        >>> DateString('2019-06-18').year
        2019
        """
        return self.dt.year

    @property
    def month(self):
        """
        >>> DateString('2019-06-18').month
        6
        """
        return self.dt.month

    @property
    def day(self):
        """
        >>> DateString('2019-06-18').day
        18
        """
        return self.dt.day

    @property
    def dayofweek(self):
        """
        >>> DateString('2019/6/13').dayofweek
        3
        """
        return self.dt.weekday()

    @property
    def dayofyear(self):
        """
        >>> DateString('20190101').dayofyear
        1
        >>> DateString('2018年12月31日').dayofyear
        365
        """
        offset = [[0, 31, 59, 90, 120, 151, 181, 212, 243, 273, 304, 334],
                  [0, 31, 60, 91, 121, 152, 182, 213, 244, 274, 305, 335]]
        return offset[self.is_leap_year][self.month - 1] + self.day

    @property
    def is_leap_year(self):
        year = self.year
        return ((year % 4 == 0) and (year % 100 != 0)) or year % 400 == 0

    @property
    def is_weekday(self):
        return self.dayofweek < 5

    @property
    def is_weekend(self):
        return self.dayofweek > 4

    @property
    def is_month_beginning(self):
        return self.day == 1

    @property
    def is_month_end(self):
        """
        >>> DateString('20080229').is_month_end
        True
        >>> DateString('1999-12-31').is_month_end
        True
        >>> DateString('2005/1/1').is_month_end
        False
        """
        offset = [[31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31],
                  [31, 29, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]]
        return self.day == offset[self.is_leap_year][self.month - 1]

    @classmethod
    def today(cls, shift=0):
        day = datetime.date.today() + datetime.timedelta(days=shift)
        return DateString(day.strftime('%Y%m%d'))

    def reformat(self, delimiter='-'):
        """
        >>> ds = DateString('20190613')
        >>> ds.reformat()
        '2019-06-13'
        >>> ds.reformat('/')
        '2019/06/13'
        """
        return '{year:d}{delimiter:s}{month:02d}{delimiter:s}{day:02d}'.format(year=self.year, month=self.month, day=self.day, delimiter=delimiter)


if __name__ == "__main__":
    import doctest
    import pandas as pd
    doctest.testmod(verbose=True)
    print(DateString.today(-1))
