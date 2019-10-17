from copy import copy
from typing import Dict

from report.symbolhistory.symbolhistorycontextholding import SymbolHistoryContextHolding
from report.symbolhistory.symbolhistorycontextsnapshot import SymbolHistoryContextSnapshot
from robinhood.lib.marketplace.optioninstrument import OptionInstrument


class SymbolHistoryContext(object):

    def __init__(self, symbol: str) -> None:
        self._profit = 0.0
        self._stock_holding = SymbolHistoryContextHolding(
            symbol=symbol,
            quantity=0,
            avg_unit_price=0.0,
            option_instrument=None,
        )
        self._option_sell_holding: Dict[str, SymbolHistoryContextHolding] = {}
        self._option_buy_holding: Dict[str, SymbolHistoryContextHolding] = {}

    @property
    def stock_cost_basis(self) -> float:
        return self._stock_holding.quantity * self._stock_holding.avg_unit_price

    @property
    def option_sell_holding(self) -> Dict[str, SymbolHistoryContextHolding]:
        return self._option_sell_holding

    @property
    def option_buy_holding(self) -> Dict[str, SymbolHistoryContextHolding]:
        return self._option_buy_holding

    def take_snapshot(self) -> SymbolHistoryContextSnapshot:
        return SymbolHistoryContextSnapshot(
            profit=self._profit,
            stock_holding=self._stock_holding,
            option_sell_holding=copy(self._option_sell_holding),
            option_buy_holding=copy(self._option_buy_holding),
        )

    def limit_or_market_buy_stock(self, quantity: int, price: float) -> None:
        total_cost = self.stock_cost_basis + quantity * price
        total_quantity = self._stock_holding.quantity + quantity
        self._stock_holding = SymbolHistoryContextHolding(
            symbol=self._stock_holding.symbol,
            quantity=self._stock_holding.quantity + quantity,
            avg_unit_price=total_cost / total_quantity,
            option_instrument=None,
        )

    def limit_or_market_sell_stock(self, quantity: int, price: float) -> None:
        self._profit += (price - self._stock_holding.avg_unit_price) * quantity
        self._stock_holding = SymbolHistoryContextHolding(
            symbol=self._stock_holding.symbol,
            quantity=self._stock_holding.quantity - quantity,
            avg_unit_price=self._stock_holding.avg_unit_price,
            option_instrument=None,
        )

    def sell_to_open(
        self,
        symbol: str,
        quantity: int,
        unit_price: float,
        option_instrument: OptionInstrument,
    ) -> None:
        self._buy_or_sell_to_open(
            buy_or_sell='sell',
            symbol=symbol,
            quantity=quantity,
            unit_price=unit_price,
            option_instrument=option_instrument,
        )

    def buy_to_close(
        self,
        symbol: str,
        quantity: int,
        unit_price: float,
    ) -> None:
        self._buy_or_sell_to_close(
            buy_or_sell='buy',
            symbol=symbol,
            quantity=quantity,
            unit_price=unit_price,
        )

    def buy_to_open(
        self,
        symbol: str,
        quantity: int,
        unit_price: float,
        option_instrument: OptionInstrument,
    ) -> None:
        self._buy_or_sell_to_open(
            buy_or_sell='buy',
            symbol=symbol,
            quantity=quantity,
            unit_price=unit_price,
            option_instrument=option_instrument,
        )

    def sell_to_close(
        self,
        symbol: str,
        quantity: int,
        unit_price: float,
    ) -> None:
        self._buy_or_sell_to_close(
            buy_or_sell='sell',
            symbol=symbol,
            quantity=quantity,
            unit_price=unit_price,
        )

    def call_assignment(self, symbol: str, quantity: int, price: float) -> None:
        holding = self._option_sell_holding[symbol]
        current_avg_unit_price = holding.avg_unit_price
        new_quantity = holding.quantity - quantity
        if new_quantity == 0:
            del self._option_sell_holding[symbol]
        else:
            self._option_sell_holding[symbol] = SymbolHistoryContextHolding(
                symbol=symbol,
                quantity=new_quantity,
                avg_unit_price=holding.avg_unit_price,
                option_instrument=holding.option_instrument,
            )

        shares_sold = quantity * 100
        profit_per_share = price - self._stock_holding.avg_unit_price + current_avg_unit_price
        self._profit += profit_per_share * shares_sold
        self._stock_holding = SymbolHistoryContextHolding(
            symbol=self._stock_holding.symbol,
            quantity=self._stock_holding.quantity - shares_sold,
            avg_unit_price=self._stock_holding.avg_unit_price,
            option_instrument=None,
        )

    def put_asignment(self, symbol: str, quantity: int, price: float, strike_price: float) -> None:
        holding = self._option_sell_holding[symbol]
        new_quantity = holding.quantity - quantity
        if new_quantity == 0:
            del self._option_sell_holding[symbol]
        else:
            self._option_sell_holding[symbol] = SymbolHistoryContextHolding(
                symbol=symbol,
                quantity=new_quantity,
                avg_unit_price=holding.avg_unit_price,
                option_instrument=holding.option_instrument,
            )

        shares_bought = quantity * 100
        new_cost = (strike_price - holding.avg_unit_price) * shares_bought
        self._stock_holding = SymbolHistoryContextHolding(
            symbol=self._stock_holding.symbol,
            quantity=self._stock_holding.quantity + shares_bought,
            avg_unit_price=(self.stock_cost_basis + new_cost) / (self._stock_holding.quantity + shares_bought),
            option_instrument=None,
        )

    def call_exercise(
        self,
        symbol: str,
        quantity: int,
        price: float,
        strike_price: float,
    ) -> None:
        holding = self._option_buy_holding[symbol]
        shares_bought = quantity * 100
        effective_cost_per_share = strike_price + price
        new_cost = effective_cost_per_share * shares_bought
        total_cost = self.stock_cost_basis + new_cost

        self._stock_holding = SymbolHistoryContextHolding(
            symbol=self._stock_holding.symbol,
            quantity=self._stock_holding.quantity + shares_bought,
            avg_unit_price=total_cost / self._stock_holding.quantity,
            option_instrument=None,
        )

        new_quantity = holding.quantity - quantity
        if new_quantity == 0:
            del self._option_buy_holding[symbol]
        else:
            self._option_buy_holding[symbol] = SymbolHistoryContextHolding(
                symbol=symbol,
                quantity=new_quantity,
                avg_unit_price=holding.avg_unit_price,
                option_instrument=holding.option_instrument,
            )

    def option_expire(self, symbol: str, quantity: int) -> None:
        if symbol in self._option_buy_holding:
            holding_dict = self._option_buy_holding
            holding = self._option_buy_holding[symbol]
            profit = -holding.quantity * holding.avg_unit_price * 100
        elif symbol in self._option_sell_holding:
            holding_dict = self._option_sell_holding
            holding = self._option_sell_holding[symbol]
            profit = holding.quantity * holding.avg_unit_price * 100
        else:
            return

        assert holding.quantity - quantity == 0
        del holding_dict[symbol]
        self._profit += profit

    def _buy_or_sell_to_open(
        self,
        buy_or_sell: str,
        symbol: str,
        quantity: int,
        unit_price: float,
        option_instrument: OptionInstrument,
    ) -> None:
        if buy_or_sell == 'buy':
            option_holding_dict = self._option_buy_holding
        else:
            option_holding_dict = self._option_sell_holding

        if symbol in option_holding_dict:
            holding = option_holding_dict[symbol]
            new_quantity = holding.quantity + quantity
            new_price = (holding.quantity * holding.avg_unit_price + quantity * unit_price) / new_quantity
        else:
            new_quantity = quantity
            new_price = unit_price

        option_holding_dict[symbol] = SymbolHistoryContextHolding(
            symbol=symbol,
            quantity=new_quantity,
            avg_unit_price=new_price,
            option_instrument=option_instrument,
        )

    def _buy_or_sell_to_close(
        self,
        buy_or_sell: str,
        symbol: str,
        quantity: int,
        unit_price: float,
    ) -> None:
        if buy_or_sell == 'buy':
            option_holding_dict = self._option_sell_holding
            unit_profit = option_holding_dict[symbol].avg_unit_price - unit_price
        else:
            option_holding_dict = self._option_buy_holding
            unit_profit = unit_price - option_holding_dict[symbol].avg_unit_price

        new_quantity = option_holding_dict[symbol].quantity - quantity
        self._profit += quantity * unit_profit * 100
        if new_quantity == 0:
            del option_holding_dict[symbol]
        else:
            option_holding_dict[symbol] = SymbolHistoryContextHolding(
                symbol=symbol,
                quantity=new_quantity,
                avg_unit_price=option_holding_dict[symbol].avg_unit_price,
                option_instrument=option_holding_dict[symbol].option_instrument,
            )
