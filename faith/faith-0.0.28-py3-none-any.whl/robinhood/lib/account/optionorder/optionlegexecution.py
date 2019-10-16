from datetime import datetime
from typing import Any
from typing import Dict

from robinhood.lib.helpers import parse_date
from robinhood.lib.helpers import parse_datetime_with_optional_microsecond


class OptionLegExecution(object):

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

    @property
    def price(self) -> float:
        return self._price

    @property
    def quantity(self) -> float:
        return self._quantity


def option_leg_execution_from_data(data: Dict[str, Any]) -> OptionLegExecution:
    return OptionLegExecution(
        execution_id=data['id'],
        price=float(data['price']),
        quantity=float(data['quantity']),
        timestamp=parse_datetime_with_optional_microsecond(data['timestamp']),
        settlement_date=parse_date(data['settlement_date']),
    )
