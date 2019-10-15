import os
from datetime import datetime
from typing import Any
from typing import Dict

from data.watchlist import ALL_REVERSED
from robinhood.lib.helpers import parse_datetime_with_microsecond


class StockPosition(object):

    def __init__(
        self,
        instrument_url: str,
        quantity: float,
        position_url: str,
        account_url: str,
        intraday_quantity: float,
        average_buy_price: float,
        pending_average_buy_price: float,
        intraday_average_buy_price: float,
        shares_pending_from_options_events: float,
        shares_held_for_options_collateral: float,
        shares_held_for_options_events: float,
        shares_held_for_stock_grants: float,
        shares_held_for_buys: float,
        shares_held_for_sells: float,
        created_at: datetime,
        updated_at: datetime,
    ) -> None:
        self._instrument_url = instrument_url
        self._quantity = quantity
        self._position_url = position_url
        self._account_url = account_url
        self._intraday_quantity = intraday_quantity
        self._average_buy_price = average_buy_price
        self._pending_average_buy_price = pending_average_buy_price
        self._intraday_average_buy_price = intraday_average_buy_price
        self._shares_pending_from_options_events = shares_pending_from_options_events
        self._shares_held_for_options_collateral = shares_held_for_options_collateral
        self._shares_held_for_options_events = shares_held_for_options_events
        self._shares_held_for_stock_grants = shares_held_for_stock_grants
        self._shares_held_for_buys = shares_held_for_buys
        self._shares_held_for_sells = shares_held_for_sells
        self._created_at = created_at
        self._updated_at = updated_at

    @property
    def instrument_id(self) -> str:
        return os.path.basename(os.path.normpath(self._instrument_url))

    @property
    def symbol(self) -> str:
        return ALL_REVERSED[self.instrument_id]

    @property
    def quantity(self) -> float:
        return self._quantity


def stock_position_from_data(data: Dict[str, Any]) -> StockPosition:
    return StockPosition(
        instrument_url=data['instrument'],
        quantity=float(data['quantity']),
        position_url=data['url'],
        account_url=data['account'],
        intraday_quantity=float(data['intraday_quantity']),
        average_buy_price=float(data['average_buy_price']),
        pending_average_buy_price=float(data['pending_average_buy_price']),
        intraday_average_buy_price=float(data['intraday_average_buy_price']),
        shares_pending_from_options_events=float(data['shares_pending_from_options_events']),
        shares_held_for_options_collateral=float(data['shares_held_for_options_collateral']),
        shares_held_for_options_events=float(data['shares_held_for_options_events']),
        shares_held_for_stock_grants=float(data['shares_held_for_stock_grants']),
        shares_held_for_buys=float(data['shares_held_for_buys']),
        shares_held_for_sells=float(data['shares_held_for_sells']),
        created_at=parse_datetime_with_microsecond(data['created_at']),
        updated_at=parse_datetime_with_microsecond(data['updated_at']),
    )
