from typing import List
from typing import Union

from robinhood.lib.marketplace.equity import Equity
from robinhood.lib.marketplace.optioninstrument import OptionInstrument
from robinhood.lib.marketplace.optionmarketdata import OptionMarketData


class OptionSellCandidate(object):

    def __init__(
        self,
        option_instrument: OptionInstrument,
        market_data: OptionMarketData,
        fund_efficiency: float,
    ) -> None:
        self._option_instrument = option_instrument
        self._market_data = market_data
        self._fund_efficiency = fund_efficiency

    @property
    def symbol(self) -> str:
        return self._option_instrument.symbol

    @property
    def chain_symbol(self) -> str:
        return self._option_instrument.chain_symbol

    @property
    def fund_efficiency(self) -> float:
        return self._fund_efficiency

    def gen_data_row(self, chain_symbol_market_data: Equity) -> List[Union[str, float]]:
        assert self._market_data.chance_of_profit_short is not None
        assert self._market_data.high_fill_rate_sell_price is not None
        assert self._market_data.medium_fill_rate_sell_price is not None
        assert self._market_data.low_fill_rate_sell_price is not None

        row: List[Union[str, float]] = [
            self._option_instrument.symbol,
            self._option_instrument.strike_price,
            chain_symbol_market_data.last_price,
            self._get_percentage_to_strike(
                strike_price=self._option_instrument.strike_price,
                current_price=chain_symbol_market_data.last_price,
            ),
            self._market_data.chance_of_profit_short,
            self._market_data.high_fill_rate_sell_price,
            self._market_data.medium_fill_rate_sell_price,
            self._market_data.low_fill_rate_sell_price,
            self._get_estimated_profit_per_10k(
                fill_price=self._market_data.medium_fill_rate_sell_price,
                strike_price=self._option_instrument.strike_price,
                chance_of_profit=self._market_data.chance_of_profit_short,
            ),
            self._fund_efficiency,
            self._market_data.open_interest,
        ]

        return row

    def _get_percentage_to_strike(self, strike_price: float, current_price: float) -> float:
        return 1 - strike_price / current_price

    def _get_estimated_profit_per_10k(self, fill_price: float, strike_price: float, chance_of_profit: float) -> float:
        return fill_price * chance_of_profit / strike_price * 10000
