from QiDataProcessing.TradingFrame.TradingFrameHelper import TradingFrameHelper


class TradingFrame:
    def __init__(self):
        self._begin_day_string = ""
        self._trading_time = ""

    @property
    def begin_day_string(self):
        return self._begin_day_string

    @begin_day_string.setter
    def begin_day_string(self, value):
        self._begin_day_string = value

    @property
    def trading_time(self):
        return self._trading_time

    @trading_time.setter
    def trading_time(self, value):
        self._trading_time = value

    @property
    def begin_day(self):
        return TradingFrameHelper.parse_date(self._begin_day_string)

    @property
    def trading_time_slices(self):
        return TradingFrameHelper.parse_time_slice(self._trading_time)
