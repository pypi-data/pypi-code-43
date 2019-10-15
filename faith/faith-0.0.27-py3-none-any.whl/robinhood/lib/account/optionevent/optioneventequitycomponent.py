from typing import Any
from typing import Dict


class OptionEventEquityComponent(object):

    def __init__(
        self,
        component_id: str,
        symbol: str,
        side: str,
        instrument_url: str,
        price: float,
        quantity: float,
    ) -> None:
        self._component_id = component_id
        self._symbol = symbol
        self._side = side
        self._instrument_url = instrument_url
        self._price = price
        self._quantity = quantity


def option_event_equity_component_from_data(data: Dict[str, Any]) -> OptionEventEquityComponent:
    return OptionEventEquityComponent(
        component_id=data['id'],
        symbol=data['symbol'],
        side=data['side'],
        instrument_url=data['instrument'],
        price=float(data['price']),
        quantity=float(data['quantity']),
    )
