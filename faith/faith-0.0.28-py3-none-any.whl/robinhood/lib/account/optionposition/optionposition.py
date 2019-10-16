from datetime import datetime
from typing import Any
from typing import Dict

from robinhood.lib.helpers import parse_datetime_with_microsecond


class OptionPosition(object):

    def __init__(
        self,
        position_id: str,
        position_type: str,
        position_url: str,
        account_url: str,
        option_instrument_url: str,
        chain_id: str,
        chain_symbol: str,
        average_price: float,
        quantity: float,
        trade_value_multiplier: float,
        intraday_average_open_price: float,
        intraday_quantity: float,
        pending_assignment_quantity: float,
        pending_exercise_quantity: float,
        pending_expiration_quantity: float,
        pending_expired_quantity: float,
        pending_buy_quantity: float,
        pending_sell_quantity: float,
        created_at: datetime,
        updated_at: datetime,
    ) -> None:
        self._position_id = position_id
        self._position_type = position_type
        self._position_url = position_url
        self._account_url = account_url
        self._option_instrument_url = option_instrument_url
        self._chain_id = chain_id
        self._chain_symbol = chain_symbol
        self._average_price = average_price
        self._quantity = quantity
        self._trade_value_multiplier = trade_value_multiplier
        self._intraday_average_open_price = intraday_average_open_price
        self._intraday_quantity = intraday_quantity
        self._pending_assignment_quantity = pending_assignment_quantity
        self._pending_exercise_quantity = pending_exercise_quantity
        self._pending_expiration_quantity = pending_expiration_quantity
        self._pending_expired_quantity = pending_expired_quantity
        self._pending_buy_quantity = pending_buy_quantity
        self._pending_sell_quantity = pending_sell_quantity
        self._created_at = created_at
        self._updated_at = updated_at

    @property
    def position_id(self) -> str:
        return self._position_id

    @property
    def position_type(self) -> str:
        return self._position_type

    @property
    def option_instrument_url(self) -> str:
        return self._option_instrument_url

    @property
    def chain_symbol(self) -> str:
        return self._chain_symbol

    @property
    def average_price(self) -> float:
        return abs(self._average_price)

    @property
    def avg_unit_price(self) -> float:
        return abs(self._average_price) / self._trade_value_multiplier

    @property
    def active_quantity(self) -> float:
        return (
            self._quantity
            - self._pending_expiration_quantity
            - self._pending_assignment_quantity
        )

    @property
    def quantity(self) -> float:
        return self._quantity

    @property
    def pending_expiration_quantity(self) -> float:
        return self._pending_expiration_quantity

    @property
    def pending_assignment_quantity(self) -> float:
        return self._pending_assignment_quantity


def option_position_from_data(data: Dict[str, Any]) -> OptionPosition:
    return OptionPosition(
        position_id=data['id'],
        position_type=data['type'],
        position_url=data['url'],
        account_url=data['account'],
        option_instrument_url=data['option'],
        chain_id=data['chain_id'],
        chain_symbol=data['chain_symbol'],
        average_price=float(data['average_price']),
        quantity=float(data['quantity']),
        trade_value_multiplier=float(data['trade_value_multiplier']),
        intraday_average_open_price=float(data['intraday_average_open_price']),
        intraday_quantity=float(data['intraday_quantity']),
        pending_assignment_quantity=float(data['pending_assignment_quantity']),
        pending_exercise_quantity=float(data['pending_exercise_quantity']),
        pending_expiration_quantity=float(data['pending_expiration_quantity']),
        pending_expired_quantity=float(data['pending_expired_quantity']),
        pending_buy_quantity=float(data['pending_buy_quantity']),
        pending_sell_quantity=float(data['pending_sell_quantity']),
        created_at=parse_datetime_with_microsecond(data['created_at']),
        updated_at=parse_datetime_with_microsecond(data['updated_at']),
    )
