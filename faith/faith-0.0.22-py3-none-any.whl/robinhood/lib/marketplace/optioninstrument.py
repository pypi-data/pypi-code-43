import json
import os
from datetime import date
from datetime import datetime
from typing import Any
from typing import Dict
from typing import Optional

from data.redis import redis
from robinhood.lib.errors import URLNotFoundError
from robinhood.lib.helpers import parse_date
from robinhood.lib.helpers import parse_datetime_with_microsecond
from robinhood.lib.marketplace.minticks import min_ticks_from_data
from robinhood.lib.marketplace.minticks import MinTicks
from robinhood.lib.marketplace.optionmarketdata import option_market_data_from_data
from robinhood.lib.marketplace.optionmarketdata import OptionMarketData
from robinhood.lib.robinhoodclient import rhc


class OptionInstrument(object):

    def __init__(
        self,
        instrument_id: str,
        instrument_type: str,
        issue_date: date,
        state: str,
        tradability: str,
        rhs_tradability: str,
        chain_symbol: str,
        exp_date: str,
        strike_price: float,
        chain_id: str,
        url: str,
        min_ticks: MinTicks,
        created_at: datetime,
        updated_at: datetime,
    ) -> None:
        self._instrument_id = instrument_id
        self._instrument_type = instrument_type
        self._issue_date = issue_date
        self._state = state
        self._tradability = tradability
        self._rhs_tradability = rhs_tradability
        self._chain_symbol = chain_symbol
        self._exp_date = exp_date
        self._strike_price = strike_price
        self._chain_id = chain_id
        self._url = url
        self._min_ticks = min_ticks
        self._created_at = created_at
        self._updated_at = updated_at
        self._url = url

    @property
    def instrument_id(self) -> str:
        return self._instrument_id

    @property
    def instrument_type(self) -> str:
        return self._instrument_type

    @property
    def is_call(self) -> bool:
        assert self.instrument_type in {'call', 'put'}
        return self.instrument_type == 'call'

    @property
    def is_put(self) -> bool:
        assert self.instrument_type in {'call', 'put'}
        return self.instrument_type == 'put'

    @property
    def instrument_type_short(self) -> str:
        return self._instrument_type.upper()[0]

    @property
    def instrument_type_full(self) -> str:
        return self._instrument_type.upper()

    @property
    def issue_date(self) -> date:
        return self._issue_date

    @property
    def state(self) -> str:
        return self._state

    @property
    def tradability(self) -> str:
        return self._tradability

    @property
    def rhs_tradability(self) -> str:
        return self._rhs_tradability

    @property
    def chain_symbol(self) -> str:
        return self._chain_symbol

    @property
    def chain_id(self) -> str:
        return self._chain_id

    @property
    def exp_date(self) -> str:
        return self._exp_date

    @property
    def days_to_expire(self) -> int:
        exp_date = datetime.strptime(self.exp_date, '%Y-%m-%d')
        diff = exp_date - datetime.now()
        return diff.days + 1

    @property
    def formatted_exp_date(self) -> str:
        return self._exp_date.replace('-', '')

    @property
    def strike_price(self) -> float:
        return self._strike_price

    @property
    def url(self) -> str:
        return self._url

    @property
    def min_ticks(self) -> MinTicks:
        return self._min_ticks

    @property
    def created_at(self) -> datetime:
        return self._created_at

    @property
    def updated_at(self) -> datetime:
        return self._updated_at

    @property
    def symbol(self) -> str:
        return (
            f'{self._chain_symbol}{self.formatted_exp_date}'
            f'{self.instrument_type_short}{self._strike_price}'
        )

    @property
    def market_data(self) -> Optional[OptionMarketData]:
        return self._get_market_data()

    def _get_market_data(self) -> Optional[OptionMarketData]:
        try:
            market_data: OptionMarketData = rhc.get_object(
                url=self._get_market_data_endpoint(),
                callback=option_market_data_from_data,
            )
            return market_data
        except URLNotFoundError:
            return None

    def _get_market_data_endpoint(self) -> str:
        return f'https://api.robinhood.com/marketdata/options/{self._instrument_id}/'


def option_instrument_from_data(data: Dict[str, Any]) -> OptionInstrument:
    min_ticks = min_ticks_from_data(data=data['min_ticks'])
    return OptionInstrument(
        instrument_id=data['id'],
        instrument_type=data['type'],
        issue_date=parse_date(data['issue_date']),
        state=data['state'],
        tradability=data['tradability'],
        rhs_tradability=data['rhs_tradability'],
        chain_symbol=data['chain_symbol'],
        exp_date=data['expiration_date'],
        strike_price=float(data['strike_price']),
        chain_id=data['chain_id'],
        url=data['url'],
        min_ticks=min_ticks,
        created_at=parse_datetime_with_microsecond(data['created_at']),
        updated_at=parse_datetime_with_microsecond(data['updated_at']),
    )


def option_instrument_from_url(url: str) -> OptionInstrument:
    option_instrument_id = os.path.basename(os.path.normpath(url))
    redis_key = f'ROBINHOOD:OPTION_INSTRUMENT:{option_instrument_id}'
    redis_cache = redis.get(redis_key)
    if redis_cache is None:
        raw = rhc.get_url(url, return_raw_response=True)
        redis.set(name=redis_key, value=raw)
    else:
        raw = redis_cache

    data = json.loads(raw.decode('utf-8'))
    return option_instrument_from_data(data=data)
