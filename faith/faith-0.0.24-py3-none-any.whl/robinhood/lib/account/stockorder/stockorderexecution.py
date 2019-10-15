from datetime import datetime
from typing import Any
from typing import Dict

from robinhood.lib.helpers import parse_date
from robinhood.lib.helpers import parse_datetime_with_microsecond


class StockOrderExecution(object):

    def __init__(
        self,
        execution_id: str,
        price: float,
        quantity: float,
        timestamp: datetime,
        settlement_date: datetime,
    ) -> None:
        self._execution_id = execution_id
        self._price = price
        self._quantity = quantity
        self._timestamp = timestamp
        self._settlement_date = settlement_date


def stock_order_execution_from_data(data: Dict[str, Any]) -> StockOrderExecution:
    return StockOrderExecution(
        execution_id=data['id'],
        price=float(data['price']),
        quantity=float(data['quantity']),
        timestamp=parse_datetime_with_microsecond(data['timestamp']),
        settlement_date=parse_date(data['settlement_date']),
    )
