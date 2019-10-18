import time

from QiDataProcessing.Core.Quote import Quote


class Tick:
    def __init__(self):
        self._instrumentId = ""
        self._exchangeId = ""
        self._quote = Quote()
        self._lastPrice = 0.0
        self._iopv = 0.0
        self._preClosePrice = 0.0
        self._openPrice = 0.0
        self._highPrice = 0.0
        self._lowPrice = 0.0
        self._volume = 0
        self._turnover = 0.0
        self._upLimitPrice = 0.0
        self._dropLimitPrice = 0.0
        self._tradingDay = time.time()
        self._naturalTime = time.time()
        self._localTime = time.time()
        self._openInterest = 0.0
        self._preOpenInterest = 0.0
        self._preSettlementPrice = 0.0
        self._market = 1
        self._status = 1
        self.BidPriceLevel = 1
        self.skPriceLevel = 1

        self.num_trades = 0
        self.total_bid_qty = 0
        self.total_ask_qty = 0
        self.weighted_avg_bid_price = 0.0
        self.weighted_avg_ask_price = 0.0

    @property
    def instrument_id(self):
        return self._instrumentId

    @instrument_id.setter
    def instrument_id(self, value):
        self._instrumentId = value

    @property
    def exchange_id(self):
        return self._exchangeId

    @exchange_id.setter
    def exchange_id(self, value):
        self._exchangeId = value

    @property
    def market(self):
        return self._market

    @market.setter
    def market(self, value):
        self._market = value

    @property
    def local_time(self):
        return self._localTime

    @local_time.setter
    def local_time(self, value):
        self._localTime = value

    @property
    def date_time(self):
        return self._naturalTime

    @date_time.setter
    def date_time(self, value):
        self._naturalTime = value

    @property
    def time_now(self):
        return time.mktime(str(self._naturalTime.timetuple()))

    @property
    def trading_day(self):
        return self._tradingDay

    @trading_day.setter
    def trading_day(self, value):
        self._tradingDay = value

    @property
    def quote(self):
        return self._quote

    @quote.setter
    def quote(self, value):
        self._quote = value

    @property
    def ask_price1(self):
        return self._quote.ask_price1

    @ask_price1.setter
    def ask_price1(self, value):
        self._quote.ask_price1 = value

    @property
    def ask_volume1(self):
        return self._quote.ask_volume1

    @ask_volume1.setter
    def ask_volume1(self, value):
        self._quote.ask_volume1 = value

    @property
    def bid_price1(self):
        return self._quote.bid_price1

    @bid_price1.setter
    def bid_price1(self, value):
        self._quote.bid_price1 = value

    @property
    def bid_volume1(self):
        return self._quote.bid_volume1

    @bid_volume1.setter
    def bid_volume1(self, value):
        self._quote.bid_volume1 = value

    @property
    def pre_close_price(self):
        return self._preClosePrice

    @pre_close_price.setter
    def pre_close_price(self, value):
        self._preClosePrice = value

    @property
    def open_price(self):
        return self._openPrice

    @open_price.setter
    def open_price(self, value):
        self._openPrice = value

    @property
    def high_price(self):
        return self._highPrice

    @high_price.setter
    def high_price(self, value):
        self._highPrice = value

    @property
    def low_price(self):
        return self._lowPrice

    @low_price.setter
    def low_price(self, value):
        self._lowPrice = value

    @property
    def last_price(self):
        return self._lastPrice

    @last_price.setter
    def last_price(self, value):
        self._lastPrice = value

    @property
    def iopv(self):
        return self._iopv

    @iopv.setter
    def iopv(self, value):
        self._iopv = value

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
    def up_limit(self):
        return self._upLimitPrice

    @up_limit.setter
    def up_limit(self, value):
        self._upLimitPrice = value

    @property
    def drop_limit(self):
        return self._dropLimitPrice

    @drop_limit.setter
    def drop_limit(self, value):
        self._dropLimitPrice = value

    @property
    def open_interest(self):
        return self._openInterest

    @open_interest.setter
    def open_interest(self, value):
        self._openInterest = value

    @property
    def pre_open_interest(self):
        return self._preOpenInterest

    @pre_open_interest.setter
    def pre_open_interest(self, value):
        self._preOpenInterest = value

    @property
    def pre_settlement_price(self):
        return self._preSettlementPrice

    @pre_settlement_price.setter
    def pre_settlement_price(self, value):
        self._preSettlementPrice = value

    @property
    def change(self):
        if self.pre_close_price > 0.0:
            return round((self.last_price / self.pre_close_price - 1.0) * 100.0, 4)
        if self.pre_settlement_price > 0.0:
            return round((self.last_price / self.pre_settlement_price - 1.0) * 100.0, 4)
        return 0.0

    @property
    def if_up_limit(self):
        return (self.ask_price1 <= 0.0) & (self.bid_price1 > 0.0)

    @property
    def IfDropLimit(self):
        return (self.bid_price1 <= 0.0) & (self.ask_price1 > 0.0)

    @property
    def status(self):
        return self._status

    @status.setter
    def status(self, value):
        self._status = value
        
    @property
    def bid_num_order1(self):
        return self.quote.bid_num_order1

    @property
    def ask_num_order1(self):
        return self.quote.ask_num_order1

    def to_string(self):
        string_builder = ""
        string_builder += self.market
        string_builder += ("[" + self.instrument_id + "]")
        string_builder += ("交易日" + self.trading_day.strftime('%Y/%m/%d')) + ","
        string_builder += ("自然时" + self.date_time.strftime('%Y-%m-%d %H:%M:%S.%f')) + ","
        string_builder += ("最新=" + str(self.last_price)) + ","
        string_builder += ("开=" + str(self.open_price)) + ","
        string_builder += ("高=" + str(self.high_price)) + ","
        string_builder += ("低=" + str(self.low_price)) + ","
        string_builder += ("昨收=" + str(self.pre_close_price)) + ","
        if self.change >= 0.0:
            string_builder += ("涨幅=" + str(round(self.change, 2))) + "%,"
        else:
            string_builder += ("跌幅=" + str(round(self.change, 2))) + "%,"
        string_builder += ("量" + str(self.volume)) + ","
        string_builder += ("额" + str(self.turnover)) + ","
        string_builder += ("[" + str(self.quote.bid_volume1) + "|" + str(self.quote.bid_price1) + "][" + str(self.quote.ask_price1) + "|" +
                           str(self.quote.ask_volume1) + "]")
        return string_builder

    def clone(self):
        tick = Tick()
        tick._market = self._market
        tick._naturalTime = self._naturalTime
        tick._tradingDay = self._tradingDay
        tick._dropLimitPrice = self._dropLimitPrice
        tick._exchangeId = self._exchangeId
        tick._highPrice = self._highPrice
        tick._instrumentId = self._instrumentId
        tick._lastPrice = self._lastPrice
        tick._lowPrice = self._lowPrice
        tick._openInterest = self._openInterest
        tick._openPrice = self._openPrice
        tick._preClosePrice = self._preClosePrice
        tick._preOpenInterest = self._preOpenInterest
        tick._preSettlementPrice = self._preSettlementPrice

        if self._quote is not None:
            tick._quote = self._quote.clone()

        tick._turnover = self._turnover
        tick._upLimitPrice = self._upLimitPrice
        tick._volume = self._volume

        return tick
