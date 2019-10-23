import datetime

from QiDataProcessing.Core.EnumFutureType import EnumFutureType
from QiDataProcessing.Core.EnumMarket import EnumMarket
from QiDataProcessing.Instrument.Instrument import Instrument


class Future(Instrument):
    def __init__(self):
        super().__init__()
        self._open_date = datetime.datetime
        self._future_type = EnumFutureType.Normal
        self._real_future = None
        self._expire_date = datetime.datetime
        self._long_margin_ratio = 0.0
        self._short_margin_ratio = 0.0

        self._can_sel_today_pos = True
        self._market = EnumMarket.期货

    @property
    def open_date(self):
        return self._open_date

    @open_date.setter
    def open_date(self, value):
        self._open_date = value

    @property
    def future_type(self):
        return self._future_type

    @future_type.setter
    def future_type(self, value):
        self._future_type = value

    @property
    def real_future(self):
        return self._real_future

    @real_future.setter
    def real_future(self, value):
        self._real_future = value

    @property
    def expire_date(self):
        return self._expire_date

    @expire_date.setter
    def expire_date(self, value):
        self._expire_date = value

    @property
    def long_margin_ratio(self):
        return self._long_margin_ratio

    @long_margin_ratio.setter
    def long_margin_ratio(self, value):
        self._long_margin_ratio = value

    @property
    def short_margin_ratio(self):
        return self._short_margin_ratio

    @short_margin_ratio.setter
    def short_margin_ratio(self, value):
        self._short_margin_ratio = value

    @property
    def is_arbitrage(self):
        return self.id.startswith("SP")

    def link(self, old_future, new_future):
        pass

    def clone(self):
        future = Future()
        future._exchange_id = self._exchange_id
        future._expire_date = self._expire_date
        future._id = self._id
        future._name = self._name
        future._long_margin_ratio = self._long_margin_ratio
        future._open_date = self._open_date
        future._price_tick = self._price_tick
        future._product_id = self._product_id
        future._short_margin_ratio = self._short_margin_ratio
        future._volume_multiple = self._volume_multiple
        future._last_tick = self._last_tick

        return future

    def to_string(self):
        string_builder = ""
        string_builder += ("[" + self._id + "]")
        string_builder += self._name + ","
        string_builder += self._product_id + ","
        string_builder += self._exchange_id + ","
        string_builder += "OpenDate=" + self._open_date.strftime("%Y/%m/%d") + ","
        string_builder += "ExpireDate=" + self._expire_date.strftime("%Y/%m/%d") + ","
        string_builder += "LongMarginRatio=" + str(self._long_margin_ratio) + ","
        string_builder += "ShortMarginRatio=" + str(self._short_margin_ratio) + ","
        string_builder += "VolumeMultiple=" + str(self._volume_multiple) + ","
        string_builder += "PriceTick=" + str(self._price_tick) + ","
        string_builder += "昨收=" + str(self._pre_close) + ","
        return string_builder
