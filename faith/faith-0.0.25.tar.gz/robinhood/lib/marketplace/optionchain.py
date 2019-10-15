from collections import defaultdict
from typing import Any
from typing import DefaultDict
from typing import Dict
from typing import List
from typing import Optional
from typing import Set

from robinhood.lib.marketplace.minticks import MinTicks
from robinhood.lib.marketplace.optioninstrument import option_instrument_from_data
from robinhood.lib.marketplace.optioninstrument import OptionInstrument
from robinhood.lib.robinhoodclient import rhc


class OptionChain(object):

    def __init__(
        self,
        chain_id: str,
        symbol: str,
        trade_value_multiplier: float,
        expiration_dates: List[str],
        min_ticks: MinTicks,
    ) -> None:
        self._chain_id = chain_id
        self._symbol = symbol
        self._trade_value_multiplier = trade_value_multiplier
        self._expiration_dates = expiration_dates
        self._min_ticks = min_ticks

        self._call_option_items: Optional[DefaultDict[str, List[OptionInstrument]]] = None
        self._put_option_items: Optional[DefaultDict[str, List[OptionInstrument]]] = None

    @property
    def chain_id(self) -> str:
        return self._chain_id

    @property
    def symbol(self) -> str:
        return self._symbol

    @property
    def call_option_items(self) -> DefaultDict[str, List[OptionInstrument]]:
        if self._call_option_items is None:
            self._call_option_items = self._get_option_instruments(
                expiration_dates=self._expiration_dates,
                option_type='call',
            )

        return self._call_option_items

    @property
    def put_option_items(self) -> DefaultDict[str, List[OptionInstrument]]:
        if self._put_option_items is None:
            self._put_option_items = self._get_option_instruments(
                expiration_dates=self._expiration_dates,
                option_type='put',
            )

        return self._put_option_items

    @property
    def expiration_dates(self) -> List[str]:
        return self._expiration_dates

    @property
    def min_ticks(self) -> MinTicks:
        return self._min_ticks

    def get_option_instruments(self, exp_date: str, option_type: str) -> List[OptionInstrument]:
        items = self._get_option_instruments(
            expiration_dates=[exp_date],
            option_type=option_type,
        )[exp_date]
        return sorted(items, key=lambda x: x.strike_price)

    def _get_option_instruments(
        self,
        expiration_dates: List[str],
        option_type: str,
    ) -> DefaultDict[str, List[OptionInstrument]]:
        assert self._is_valid_option_type(option_type=option_type)

        endpoint = self._get_option_chain_item_endpoint(
            expiration_dates=expiration_dates,
            option_type=option_type,
        )
        option_instruments = rhc.get_objects(
            url=endpoint,
            callback=option_instrument_from_data,
            result_key='results',
        )
        option_instrument_symbols: Set[str] = set()
        result: DefaultDict[str, List[OptionInstrument]] = defaultdict(list)
        for option_instrument in option_instruments:
            if option_instrument.symbol not in option_instrument_symbols:
                result[option_instrument.exp_date].append(option_instrument)
                option_instrument_symbols.add(option_instrument.symbol)

        return result

    def _get_option_chain_item_endpoint(
        self,
        expiration_dates: List[str],
        option_type: str,
    ) -> str:
        assert self._is_valid_option_type(option_type=option_type)

        comma_separated_exp_dates = ','.join(expiration_dates)
        state = 'active'
        tradability = 'tradable'
        return (
            f'https://api.robinhood.com/options/instruments/'
            f'?chain_id={self._chain_id}'
            f'&expiration_dates={comma_separated_exp_dates}'
            f'&type={option_type}'
            f'&state={state}'
            f'&tradability={tradability}'
        )

    def _is_valid_option_type(self, option_type: str) -> bool:
        return option_type in {'call', 'put'}


def option_chain_from_data(data: Dict[str, Any]) -> OptionChain:
    return OptionChain(
        chain_id=data['id'],
        symbol=data['symbol'],
        trade_value_multiplier=float(data['trade_value_multiplier']),
        expiration_dates=sorted(data['expiration_dates']),
        min_ticks=MinTicks(
            cutoff_price=float(data['min_ticks']['cutoff_price']),
            below_tick=float(data['min_ticks']['below_tick']),
            above_tick=float(data['min_ticks']['above_tick']),
        ),
    )
