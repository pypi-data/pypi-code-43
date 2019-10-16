import os
from datetime import datetime
from typing import Any
from typing import Optional

from robinhood.lib.helpers import parse_optional_float


class Equity(object):

    def __init__(
        self,
        symbol: str,
        instrument_id: str,
        ask_price: float,
        ask_size: int,
        bid_price: float,
        bid_size: int,
        last_trade_price: float,
        last_extended_hours_trade_price: Optional[float],
        previous_close: float,
        adjusted_previous_close: float,
        previous_close_date: datetime,
        trading_halted: bool,
        has_traded: bool,
        last_trade_price_source: str,
        updated_at: datetime,
    ) -> None:
        self._symbol = symbol
        self._instrument_id = instrument_id
        self._ask_price = ask_price
        self._ask_size = ask_size
        self._bid_price = bid_price
        self._bid_size = bid_size
        self._last_trade_price = last_trade_price
        self._last_extended_hours_trade_price = last_extended_hours_trade_price
        self._previous_close = previous_close
        self._adjusted_previous_close = adjusted_previous_close
        self._previous_close_date = previous_close_date
        self._trading_halted = trading_halted
        self._has_traded = has_traded
        self._last_trade_price_source = last_trade_price_source
        self._updated_at = updated_at

    @property
    def symbol(self) -> str:
        return self._symbol

    @property
    def instrument_id(self) -> str:
        return self._instrument_id

    @property
    def last_trade_price(self) -> float:
        return self._last_trade_price

    @property
    def last_price(self) -> float:
        if self._last_extended_hours_trade_price is None:
            return self._last_trade_price
        else:
            return self._last_extended_hours_trade_price

    @property
    def dod_percentage(self) -> float:
        return self.last_price / self._adjusted_previous_close - 1


def equity_from_data(data: Any) -> Equity:
    return Equity(
        symbol=data['symbol'],
        instrument_id=os.path.basename(os.path.normpath(data['instrument'])),
        ask_price=float(data['ask_price']),
        ask_size=data['ask_size'],
        bid_price=float(data['bid_price']),
        bid_size=data['bid_size'],
        last_trade_price=float(data['last_trade_price']),
        last_extended_hours_trade_price=parse_optional_float(data['last_extended_hours_trade_price']),
        previous_close=float(data['previous_close']),
        adjusted_previous_close=float(data['adjusted_previous_close']),
        previous_close_date=datetime.strptime(data['previous_close_date'], '%Y-%m-%d'),
        trading_halted=data['trading_halted'],
        has_traded=data['has_traded'],
        last_trade_price_source=data['last_trade_price_source'],
        updated_at=datetime.strptime(data['updated_at'], '%Y-%m-%dT%H:%M:%SZ'),
    )
