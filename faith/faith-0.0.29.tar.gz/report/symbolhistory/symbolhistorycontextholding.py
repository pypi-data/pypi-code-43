from typing import Optional

from robinhood.lib.marketplace.optioninstrument import OptionInstrument


class SymbolHistoryContextHolding(object):

    def __init__(
        self,
        symbol: str,
        quantity: int,
        avg_unit_price: float,
        option_instrument: Optional[OptionInstrument],
    ) -> None:
        self._symbol = symbol
        self._quantity = quantity
        self._avg_unit_price = avg_unit_price
        self._option_instrument = option_instrument

    @property
    def symbol(self) -> str:
        return self._symbol

    @property
    def quantity(self) -> int:
        return self._quantity

    @property
    def avg_unit_price(self) -> float:
        if self._quantity == 0:
            return 0.0

        return self._avg_unit_price

    @property
    def stock_cost_basis(self) -> float:
        assert self._option_instrument is None
        return self.quantity * self.avg_unit_price

    @property
    def option_instrument(self) -> OptionInstrument:
        assert self._option_instrument is not None
        return self._option_instrument

    @property
    def option_buy_profit(self) -> float:
        assert self._option_instrument is not None
        market_data = self._option_instrument.market_data
        assert market_data is not None
        return (market_data.adjusted_mark_price - self.avg_unit_price) * self.quantity * 100

    @property
    def option_buy_value(self) -> float:
        assert self._option_instrument is not None
        market_data = self._option_instrument.market_data
        assert market_data is not None
        return market_data.adjusted_mark_price * self.quantity * 100
