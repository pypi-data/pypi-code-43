from datetime import datetime, timedelta


__all__ = ["Date"]


class Date(datetime):

    def __new__(cls, dt=datetime.today()):
        if not isinstance(dt, datetime):
            raise TypeError("Wrong type. Should be Datetime")
        self = datetime.__new__(cls, dt.year, dt.month, dt.day)
        self._dt = dt
        return self

    def to_string_YYYY_MM_DD(self, delimiter="-") -> str:
        """
        :return: str
        """
        f = "%Y{0}%m{0}%d".format(delimiter)
        return self.strftime(f)

    def to_string_YYYYMMDD(self) -> str:
        """
        :return: str
        """
        return self.strftime("%Y%m%d")

    def offset(self, days: int) -> datetime:
        """
        :param days:
        :return:
        """
        self._dt = self._dt + timedelta(days=days)
        return Date(self._dt)

    def next_days(self, days: int) -> datetime:
        """
        :param days:
        :return:
        """
        if days <= 0:
            raise ValueError("Days could not be zero or negative. Current Value is: {}".format(days))
        return self.offset(days)

    def before_days(self, days: int) -> datetime:
        """
        :param days:
        :return:
        """
        if days <= 0:
            raise ValueError("Days could not be zero or negative. Current Value is: {}".format(days))
        return self.offset(-days)

    @staticmethod
    def today() -> datetime:
        return Date(datetime.today())

    @staticmethod
    def yesterday() -> datetime:
        return Date(datetime.today()).before_days(1)
