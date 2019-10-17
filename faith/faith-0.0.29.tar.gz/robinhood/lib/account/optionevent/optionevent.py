from datetime import datetime
from typing import Any
from typing import Dict
from typing import List
from typing import Optional

from robinhood.lib.account.optionevent.optioneventequitycomponent import option_event_equity_component_from_data
from robinhood.lib.account.optionevent.optioneventequitycomponent import OptionEventEquityComponent
from robinhood.lib.helpers import parse_date
from robinhood.lib.helpers import parse_datetime_with_microsecond
from robinhood.lib.helpers import parse_optional_float
from robinhood.lib.marketplace.optioninstrument import option_instrument_from_url
from robinhood.lib.marketplace.optioninstrument import OptionInstrument


class OptionEvent(object):

    def __init__(
        self,
        event_id: str,
        event_type: str,
        event_date: datetime,
        state: str,
        account_url: str,
        position_url: str,
        option_instrument_url: str,
        chain_id: str,
        equity_components: List[OptionEventEquityComponent],
        direction: str,
        underlying_price: Optional[float],
        total_cash_amount: float,
        quantity: float,
        created_at: datetime,
        updated_at: datetime,
    ) -> None:
        self._event_id = event_id
        self._event_type = event_type
        self._event_date = event_date
        self._state = state
        self._account_url = account_url
        self._position_url = position_url
        self._option_instrument_url = option_instrument_url
        self._chain_id = chain_id
        self._equity_components = equity_components
        self._direction = direction
        self._underlying_price = underlying_price
        self._total_cash_amount = total_cash_amount
        self._quantity = quantity
        self._created_at = created_at
        self._updated_at = updated_at

    @property
    def state(self) -> str:
        return self._state

    @property
    def event_type(self) -> str:
        return self._event_type

    @property
    def option_instrument(self) -> OptionInstrument:
        return option_instrument_from_url(url=self._option_instrument_url)

    @property
    def quantity(self) -> float:
        return self._quantity

    @property
    def direction(self) -> str:
        return self._direction

    @property
    def created_at(self) -> datetime:
        return self._created_at


def option_event_from_data(data: Dict[str, Any]) -> OptionEvent:
    equity_components = [
        option_event_equity_component_from_data(data=row)
        for row in data['equity_components']
    ]
    option_event = OptionEvent(
        event_id=data['id'],
        event_type=data['type'],
        event_date=parse_date(data['event_date']),
        state=data['state'],
        account_url=data['account'],
        position_url=data['position'],
        option_instrument_url=data['option'],
        chain_id=data['chain_id'],
        equity_components=equity_components,
        direction=data['direction'],
        underlying_price=parse_optional_float(data['underlying_price']),
        total_cash_amount=float(data['total_cash_amount']),
        quantity=float(data['quantity']),
        created_at=parse_datetime_with_microsecond(data['created_at']),
        updated_at=parse_datetime_with_microsecond(data['updated_at']),
    )
    return option_event
