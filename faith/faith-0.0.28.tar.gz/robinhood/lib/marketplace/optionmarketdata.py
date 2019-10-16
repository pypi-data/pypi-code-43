from typing import Any
from typing import Optional

from robinhood.lib.helpers import parse_optional_float
from robinhood.lib.helpers import parse_optional_int


class OptionMarketData(object):

    def __init__(
        self,
        adjusted_mark_price: float,
        ask_price: float,
        ask_size: int,
        bid_price: float,
        bid_size: int,
        last_trade_price: Optional[float],
        last_trade_size: Optional[int],
        open_interest: int,
        implied_volatility: Optional[float],
        chance_of_profit_long: Optional[float],
        chance_of_profit_short: Optional[float],
        delta: Optional[float],
        gamma: Optional[float],
        rho: Optional[float],
        theta: Optional[float],
        vega: Optional[float],
        high_fill_rate_buy_price: Optional[float],
        high_fill_rate_sell_price: Optional[float],
        low_fill_rate_buy_price: Optional[float],
        low_fill_rate_sell_price: Optional[float],
    ) -> None:
        self._adjusted_mark_price = adjusted_mark_price
        self._ask_price = ask_price
        self._ask_size = ask_size
        self._bid_price = bid_price
        self._bid_size = bid_size
        self._last_trade_price = last_trade_price
        self._last_trade_size = last_trade_size
        self._open_interest = open_interest
        self._implied_volatility = implied_volatility
        self._chance_of_profit_long = chance_of_profit_long
        self._chance_of_profit_short = chance_of_profit_short
        self._delta = delta
        self._gamma = gamma
        self._rho = rho
        self._theta = theta
        self._vega = vega
        self._high_fill_rate_buy_price = high_fill_rate_buy_price
        self._high_fill_rate_sell_price = high_fill_rate_sell_price
        self._low_fill_rate_buy_price = low_fill_rate_buy_price
        self._low_fill_rate_sell_price = low_fill_rate_sell_price

    @property
    def adjusted_mark_price(self) -> float:
        return self._adjusted_mark_price

    @property
    def implied_volatility(self) -> Optional[float]:
        return self._implied_volatility

    @property
    def last_trade_price(self) -> Optional[float]:
        return self._last_trade_price

    @property
    def chance_of_profit_long(self) -> Optional[float]:
        return self._chance_of_profit_long

    @property
    def chance_of_profit_short(self) -> Optional[float]:
        return self._chance_of_profit_short

    @property
    def high_fill_rate_sell_price(self) -> Optional[float]:
        return self._high_fill_rate_sell_price

    @property
    def medium_fill_rate_sell_price(self) -> Optional[float]:
        if self._high_fill_rate_sell_price is None or self._low_fill_rate_sell_price is None:
            return None

        return (self._high_fill_rate_sell_price + self._low_fill_rate_sell_price) / 2

    @property
    def low_fill_rate_sell_price(self) -> Optional[float]:
        return self._low_fill_rate_sell_price

    @property
    def delta(self) -> Optional[float]:
        return self._delta

    @property
    def theta(self) -> Optional[float]:
        return self._theta

    @property
    def gamma(self) -> Optional[float]:
        return self._gamma

    @property
    def rho(self) -> Optional[float]:
        return self._rho

    @property
    def vega(self) -> Optional[float]:
        return self._vega

    @property
    def open_interest(self) -> int:
        return self._open_interest


def option_market_data_from_data(data: Any) -> OptionMarketData:
    return OptionMarketData(
        adjusted_mark_price=float(data['adjusted_mark_price']),
        ask_price=float(data['ask_price']),
        ask_size=int(data['ask_size']),
        bid_price=float(data['bid_price']),
        bid_size=int(data['bid_size']),
        last_trade_price=parse_optional_float(data['last_trade_price']),
        last_trade_size=parse_optional_int(data['last_trade_size']),
        open_interest=int(data['open_interest']),
        implied_volatility=parse_optional_float(data['implied_volatility']),
        chance_of_profit_long=parse_optional_float(data['chance_of_profit_long']),
        chance_of_profit_short=parse_optional_float(data['chance_of_profit_short']),
        delta=parse_optional_float(data['delta']),
        gamma=parse_optional_float(data['gamma']),
        rho=parse_optional_float(data['rho']),
        theta=parse_optional_float(data['theta']),
        vega=parse_optional_float(data['vega']),
        high_fill_rate_buy_price=parse_optional_float(data['high_fill_rate_buy_price']),
        high_fill_rate_sell_price=parse_optional_float(data['high_fill_rate_sell_price']),
        low_fill_rate_buy_price=parse_optional_float(data['low_fill_rate_buy_price']),
        low_fill_rate_sell_price=parse_optional_float(data['low_fill_rate_sell_price']),
    )
