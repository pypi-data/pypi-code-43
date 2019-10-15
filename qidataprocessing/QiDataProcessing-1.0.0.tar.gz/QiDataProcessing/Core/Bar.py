import datetime

from QiDataProcessing.Core.BarData import BarData


class Bar:
    def __init__(self):
        self._instrumentId = ''
        self._tradingDate = datetime.datetime(1990, 1, 1)
        self._beginTime = datetime.datetime(1990, 1, 1)
        self._endTime = datetime.datetime(1990, 1, 1)
        self._high = -100000000.0
        self._open = 0.0
        self._low = 100000000.0
        self._close = 0.0
        self._preClose = 0.0
        self._volume = 0.0
        self._turnover = 0.0
        self._isComplete = False
        self._openInterest = 0.0

    @property
    def instrument_id(self):
        return self._instrumentId

    @instrument_id.setter
    def instrument_id(self, value):
        self._instrumentId = value

    @property
    def trading_date(self):
        return self._tradingDate

    @trading_date.setter
    def trading_date(self, value):
        self._tradingDate = value

    @property
    def begin_time(self):
        return self._beginTime

    @begin_time.setter
    def begin_time(self, value):
        self._beginTime = value

    @property
    def end_time(self):
        return self._endTime

    @end_time.setter
    def end_time(self, value):
        self._endTime = value

    @property
    def duration(self):
        return self.end_time - self.begin_time

    @property
    def high(self):
        if (self._high < 1E-07) & (abs(self.volume) < 1E-10):
            return self._preClose
        return self._high

    @high.setter
    def high(self, value):
        self._high = value

    @property
    def open(self):
        if (self._open < 1E-07) & (abs(self.volume) < 1E-10):
            return self._preClose
        return self._open

    @open.setter
    def open(self, value):
        self._open = value

    @property
    def low(self):
        if (self._low < 1E-07) & (abs(self.volume) < 1E-10):
            return self._preClose
        return self._low

    @low.setter
    def low(self, value):
        self._low = value

    @property
    def close(self):
        if (self._close < 1E-07) & (abs(self.volume) < 1E-10):
            return self._preClose
        return self._close

    @close.setter
    def close(self, value):
        self._close = value

    @property
    def pre_close(self):
        return self._preClose

    @pre_close.setter
    def pre_close(self, value):
        self._preClose = value

    @property
    def volume(self):
        return self._volume

    @volume.setter
    def volume(self, value):
        self._volume = value

    @property
    def turnover(self):
        return self._turnover

    @turnover.setter
    def turnover(self, value):
        self._turnover = value

    @property
    def open_interest(self):
        return self._openInterest

    @open_interest.setter
    def open_interest(self, value):
        self._openInterest = value

    def __getitem__(self, item):
        if item == BarData.close:
            return self.close
        elif item == BarData.open:
            return self.open
        elif item == BarData.high:
            return self.high
        elif item == BarData.low:
            return self.low
        elif item == BarData.volume:
            return self.volume
        elif item == BarData.turnover:
            return self.turnover
        else:
            return 0.0

    @property
    def bar_change(self):
        num = 0.0
        if abs(self.open) > 1E-10:
            num = round(100.0 * (self.close / self.open - 1.0), 3)
        return num

    @property
    def change(self):
        num = 0.0
        if abs(self.pre_close) > 1E-10:
            num = round(100.0 * (self.close / self.pre_close - 1.0), 3)
        return num

    def add_tick(self, tick):
        if self._high < tick.last_price:
            self._high = tick.last_price
        if self._low > tick.last_price:
            self._low = tick.last_price
        self._close = tick.last_price
        self.end_time = tick.date_time
        self.open_interest = tick.open_interest

    def add_bar(self, bar):
        if self._high < bar.high:
            self._high = bar.high
        if self._low > bar.low:
            self._low = bar.low
        self._close = bar.close
        self.end_time = bar.end_time
        self.open_interest = bar.open_interest
        self.volume += bar.volume
        self.turnover += bar.turnover
        self.trading_date = bar.trading_date

    def open_bar(self, begin_time, tick, bar):
        self.begin_time = begin_time
        self._high = self._low = self._open = self._close = tick.last_price
        if not any(bar):
            if (tick.high_price > 0.0) & (tick.high_price < 10000000000.0):
                self.high = tick.high_price
            if (tick.low_price > 0.0) & (tick.low_price < 10000000000.0):
                self.low = tick.low_price
            if (tick.open_price > 0.0) & (tick.open_price < 10000000000.0):
                self.open = tick.open_price

        self.end_time = tick.date_time
        if bar is not None:
            self.pre_close = bar.close
        else:
            if tick.pre_close_price > 0.0:
                self.pre_close = tick.pre_close_price
            else:
                self.pre_close = tick.open_price

        self.open_interest = tick.open_interest

    def open_bar_with_new_bar(self, new_bar):
        self.begin_time = new_bar.begin_time
        self.high = new_bar.high
        self.low = new_bar.low
        self.open = new_bar.open
        self.close = new_bar.close
        self.end_time = new_bar.end_time
        self.volume = new_bar.volume
        self.turnover = new_bar.turnover
        self.pre_close = new_bar.pre_close
        self.open_interest = new_bar.open_interest

    def close_bar(self, end_time):
        self.end_time = end_time

    def clone(self):
        bar = Bar()
        bar._instrumentId = self._instrumentId
        bar._beginTime = self._beginTime
        bar._endTime = self._endTime
        bar._high = self._high
        bar._open = self._open
        bar._low = self._low
        bar._close = self._close
        bar._preClose = self._preClose
        bar._volume = self._volume
        bar._turnover = self._turnover
        bar._isComplete = self._isComplete
        bar._openInterest = self._openInterest
        bar._tradingDate = self._tradingDate
        return bar

    def to_string(self):
        msg = "" + "[" + str(self.begin_time) + "-" + str(self.end_time) + "]"
        msg += "高" + str(self.high)
        msg += "开" + str(self.open)
        msg += "低" + str(self.low)
        msg += "收" + str(self.close)
        msg += "量=" + str(self.volume)
        msg += "额=" + str(self.turnover)
        msg += "持仓" + str(self.open_interest)
        msg += "交易日=" + self.trading_date.strftime("%Y/%m/%d")

        return msg
