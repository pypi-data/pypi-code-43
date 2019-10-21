import math
from datetime import date
from threading import RLock

from cachetools import cachedmethod, LRUCache
from mercury.api_client import ApiClient
from mercury.client.api.fiddle_api import FiddleApi
from mercury.client.api.marketdata_api import MarketdataApi
from mercury.client.api.tradeservice_api import TradeserviceApi
from mercury.client.model.fiddle import Fiddle
from mercury.client.model.position import Position
from mercury.configuration import Configuration
from mercury.envs.utils import *


class Client(object):
    """Client for API calls"""

    def __init__(self, host, equity='SPX', cache_maxsize=1000):
        """
        :param string host: Host url
        :param string equity: Equity symbol
        :param int cache_maxsize: Maximum number of cached api calls with different params
        """
        self._equity = equity
        self._cfg = Configuration()
        self._cfg.host = host
        self._api_client = ApiClient(configuration=self._cfg)

        self._market_data_api = MarketdataApi(api_client=self._api_client)
        self._trade_service_api = TradeserviceApi(api_client=self._api_client)
        self._fiddle_api = FiddleApi(api_client=self._api_client)

        self._caches = [LRUCache(maxsize=cache_maxsize) for _ in range(5)]
        self._locks = [RLock() for _ in range(5)]

    @cachedmethod(lambda obj: obj._caches[0], lock=lambda obj: obj._locks[0])
    def get_equity_quote_before(self, from_date, count, s_price):
        """
        Gets underlying prices from given date going backwards for given number of days

        :param date from_date: Starting date (not included)
        :param int count: Number of days to take
        :param float s_price: Price for stationarity

        :return list: List of prices [[open, close, low, high],...] where len(list) = count
        """
        args = {'from_date': from_date,
                'count': count}

        r = self._market_data_api.get_equity_quote_before(self._equity, **args)

        prices = []
        for i in range(count - 1, -1, -1):
            opening_price = math.log(r[i].open_price) - s_price
            closing_price = math.log(r[i].close_price) - s_price
            lowest_price = math.log(r[i].low_price) - s_price
            highest_price = math.log(r[i].high_price) - s_price
            prices.append([opening_price, closing_price, lowest_price, highest_price])

        return prices

    @cachedmethod(lambda obj: obj._caches[1], lock=lambda obj: obj._locks[1])
    def get_equity_quote(self, from_date):
        """
        Gets underlying price for given date

        :param date from_date: From date

        :return tuple: Price for date in form of (open, close, low, high)
        """
        args = {'from_date': from_date,
                'to_date': from_date}

        r = self._market_data_api.get_equity_quote(self._equity, **args)

        return (math.log(r[0].open_price), math.log(r[0].close_price), math.log(r[0].low_price),
                math.log(r[0].high_price))

    @cachedmethod(lambda obj: obj._caches[2], lock=lambda obj: obj._locks[2])
    def get_fiddle(self, fiddle_id):
        """
        Gets fiddle for given id

        :param string fiddle_id: Fiddle id

        :return tuple: Position, list of trades, date of first and last trade made, expiration,
            s_expiration, s_price
        """
        r = self._fiddle_api.get_fiddle(fiddle_id)
        trades = r.position.trades

        start_date = trades[0].opening_date
        end_date = trades[-1].opening_date
        expiration = trades[0].option_legs[0].expiration_date

        s_price = self.get_equity_quote(start_date)[1]
        s_expiration = float((expiration - start_date).days - STOP_BEFORE)

        trade_list = []
        for trade in trades:
            trade_list.extend(self._trade2list(trade, s_price, s_expiration))

        return r.position, trade_list, start_date, end_date, expiration, s_expiration, s_price

    def save_fiddle(self, user_id, title, position):
        """
        Saves fiddle

        :param string user_id: User id
        :param string title: Fiddle's title
        :param Position position: Fiddle's position

        :return string: Fiddle id
        """
        fiddle = Fiddle(user_id=user_id,
                        title=title,
                        position=position)

        args = {'fiddle': fiddle}

        return self._fiddle_api.save_fiddle(user_id, **args).id

    @cachedmethod(lambda obj: obj._caches[3], lock=lambda obj: obj._locks[3])
    def get_closest_strike_to_delta(self, contract_type, opening_date, expiration, delta):
        """
        Gets option contract with closest strike to delta

        :param string contract_type: Contract type PUT|CALL
        :param date opening_date: Option's opening date
        :param date expiration: Option's expiration
        :param float delta: Option's delta

        :return: Option contract
        """
        args = {'contract_type': contract_type,
                'date': opening_date,
                'expiration': expiration,
                'delta': delta}

        return self._market_data_api.get_closest_strike_to_delta(self._equity, **args)

    def calculate_instant_decomposed_pnl(self, position, from_date, to_date):
        """
        Calculates position's PnL for given time interval

        :param Position position: Position
        :param date from_date: From date
        :param date to_date: To date

        :return float: Pnl
        """
        args = {'position': position,
                'from_date': from_date,
                'to_date': to_date}

        return self._trade_service_api.calculate_instant_decomposed_pn_l(**args).profit

    def get_margin(self, position, from_date):
        """
        Gets position's margin on given date

        :param Position position: Position
        :param date from_date: Date

        :return float: Margin
        """
        args = {'position': position,
                'date': from_date}

        return self._trade_service_api.calculate_margin(**args)

    @cachedmethod(lambda obj: obj._caches[4], lock=lambda obj: obj._locks[4])
    def is_trading_day(self, check_date):
        """
        Checks if it is trading day or not

        :param date check_date: Date

        :return bool: True if it is trading day, false otherwise
        """
        args = {'date': check_date}
        return self._market_data_api.is_trading_day(**args)

    def _trade2list(self, trade, s_price, s_expiration):
        """
        Creates list of singles

        :param trade: Position's trade
        :param float s_price: Price for stationarity
        :param float s_expiration: Expiration rescaling

        :return list: Trade list -> list of singles [[strike, expiration, quantity, underlying],..]
        """
        closing_price = self.get_equity_quote(trade.opening_date)[1]

        singles = []
        for option_leg in trade.option_legs:
            strike = math.log(float(option_leg.strike)) - closing_price
            expiration = ((option_leg.expiration_date - trade.opening_date).days - STOP_BEFORE) / s_expiration
            quantity = (trade.quantity * option_leg.quantity) / NUM_QUANTITY
            underlying = closing_price - s_price

            singles.append([strike, expiration, quantity, underlying])

        return singles
