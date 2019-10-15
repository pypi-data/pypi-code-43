import os
from datetime import datetime
from typing import Any
from typing import Dict
from typing import List
from typing import Optional

from robinhood.lib.account.stockorder.stockorderexecution import stock_order_execution_from_data
from robinhood.lib.account.stockorder.stockorderexecution import StockOrderExecution
from robinhood.lib.helpers import parse_datetime_with_microsecond
from robinhood.lib.helpers import parse_optional_float


class StockOrder(object):

    def __init__(
        self,
        order_id: str,
        order_type: str,
        order_url: str,
        side: str,
        state: str,
        trigger: str,
        instrument_url: str,
        price: Optional[float],
        average_price: Optional[float],
        quantity: float,
        cumulative_quantity: float,
        executions: List[StockOrderExecution],
        stop_price: Optional[float],
        last_trail_price: Optional[float],
        fees: float,
        ref_id: str,
        extended_hours: bool,
        time_in_force: str,
        response_category: str,
        account_url: str,
        override_dtbp_checks: bool,
        override_day_trade_checks: bool,
        position_url: str,
        last_transaction_at: datetime,
        created_at: datetime,
        updated_at: datetime,
    ) -> None:
        self._order_id = order_id
        self._order_type = order_type
        self._order_url = order_url
        self._side = side
        self._state = state
        self._trigger = trigger
        self._instrument_url = instrument_url
        self._price = price
        self._average_price = average_price
        self._quantity = quantity
        self._cumulative_quantity = cumulative_quantity
        self._executions = executions
        self._stop_price = stop_price
        self._last_trail_price = last_trail_price
        self._fees = fees
        self._ref_id = ref_id
        self._extended_hours = extended_hours
        self._time_in_force = time_in_force
        self._response_category = response_category
        self._account_url = account_url
        self._override_dtbp_checks = override_dtbp_checks
        self._override_day_trade_checks = override_day_trade_checks
        self._position_url = position_url
        self._last_transaction_at = last_transaction_at
        self._created_at = created_at
        self._updated_at = updated_at

    @property
    def order_type(self) -> str:
        return self._order_type

    @property
    def side(self) -> str:
        return self._side

    @property
    def state(self) -> str:
        return self._state

    @property
    def instrument_id(self) -> str:
        return os.path.basename(os.path.normpath(self._instrument_url))

    @property
    def instrument_url(self) -> str:
        return self._instrument_url

    @property
    def average_price(self) -> Optional[float]:
        return self._average_price

    @property
    def quantity(self) -> float:
        return self._quantity

    @property
    def updated_at(self) -> datetime:
        return self._updated_at

    @property
    def symbol_event_name(self) -> str:
        return f'{self._order_type} {self._side}'.upper()


def stock_order_from_data(data: Dict[str, Any]) -> StockOrder:
    executions = [
        stock_order_execution_from_data(data=row)
        for row in data['executions']
    ]
    return StockOrder(
        order_id=data['id'],
        order_type=data['type'],
        order_url=data['url'],
        side=data['side'],
        state=data['state'],
        trigger=data['trigger'],
        instrument_url=data['instrument'],
        price=parse_optional_float(data['price']),
        average_price=parse_optional_float(data['average_price']),
        quantity=float(data['quantity']),
        cumulative_quantity=float(data['cumulative_quantity']),
        executions=executions,
        stop_price=parse_optional_float(data['stop_price']),
        last_trail_price=parse_optional_float(data['last_trail_price']),
        fees=float(data['fees']),
        ref_id=data['ref_id'],
        extended_hours=data['extended_hours'],
        time_in_force=data['time_in_force'],
        response_category=data['response_category'],
        account_url=data['account'],
        override_dtbp_checks=data['override_dtbp_checks'],
        override_day_trade_checks=data['override_day_trade_checks'],
        position_url=data['position'],
        last_transaction_at=parse_datetime_with_microsecond(data['last_transaction_at']),
        created_at=parse_datetime_with_microsecond(data['created_at']),
        updated_at=parse_datetime_with_microsecond(data['updated_at']),
    )
