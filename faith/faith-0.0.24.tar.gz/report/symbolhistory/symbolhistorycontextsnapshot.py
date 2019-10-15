from typing import Dict

from report.symbolhistory.symbolhistorycontextholding import SymbolHistoryContextHolding


class SymbolHistoryContextSnapshot(object):

    def __init__(
        self,
        profit: float,
        stock_holding: SymbolHistoryContextHolding,
        option_sell_holding: Dict[str, SymbolHistoryContextHolding],
        option_buy_holding: Dict[str, SymbolHistoryContextHolding],
    ) -> None:
        self._profit = profit
        self._stock_holding = stock_holding
        self._option_sell_holding = option_sell_holding
        self._option_buy_holding = option_buy_holding

    @property
    def profit(self) -> float:
        return self._profit

    @property
    def stock_holding(self) -> SymbolHistoryContextHolding:
        return self._stock_holding

    @property
    def option_buy_holding(self) -> Dict[str, SymbolHistoryContextHolding]:
        return self._option_buy_holding

    @property
    def option_sell_holding(self) -> Dict[str, SymbolHistoryContextHolding]:
        return self._option_sell_holding
