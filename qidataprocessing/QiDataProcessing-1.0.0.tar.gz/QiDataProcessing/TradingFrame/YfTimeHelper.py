import datetime


class YfTimeHelper:

    @staticmethod
    def join_date_time(trading_day, pre_trading_day1, pre_trading_day2, time_span):
        temp = datetime.datetime(2000, 1, 1) + time_span
        if temp.hour < 7:
            return pre_trading_day2 + time_span
        if temp.hour < 18:
            return trading_day + time_span

        return pre_trading_day1 + time_span

    @staticmethod
    def get_trading_day(date_time):
        """
        获取交易日
        :param date_time:datetime.datetime
        :return:datetime.datetime
        """
        if date_time.hour < 7:
            if date_time.weekday() != 5:
                return datetime.datetime(date_time.year, date_time.month, date_time.day)
            return datetime.datetime(date_time.year, date_time.month, date_time.day) + datetime.timedelta(days=2)

        if date_time.hour < 18:
            return datetime.datetime(date_time.year, date_time.month, date_time.day)

        if date_time.weekday() != 4:
            return datetime.datetime(date_time.year, date_time.month, date_time.day) + datetime.timedelta(days=1)
        return datetime.datetime(date_time.year, date_time.month, date_time.day) + datetime.timedelta(days=3)

    @staticmethod
    def get_date_time_by_trading_day(trading_day, time_span):
        temp = datetime.datetime(2000, 1, 1) + time_span
        if temp.hour < 7:
            if trading_day.weekday() != 0:
                return trading_day + time_span

            return trading_day + datetime.timedelta(days=-2) + time_span

        if temp.hour < 18:
            return trading_day + time_span

        if trading_day.weekday() != 0:
            return trading_day + datetime.timedelta(days=-1) + time_span

        return trading_day + datetime.timedelta(days=-3) + time_span
