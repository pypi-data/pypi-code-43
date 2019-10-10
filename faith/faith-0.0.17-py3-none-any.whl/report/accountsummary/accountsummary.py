from concurrent.futures import as_completed
from concurrent.futures import ThreadPoolExecutor
from typing import Dict
from typing import List
from typing import Optional
from typing import Set

from terminaltables import AsciiTable

from report.symbolhistory.symbolhistory import SymbolHistory
from robinhood.lib.account.account import account
from robinhood.lib.helpers import format_price
from robinhood.lib.helpers import format_quantity
from robinhood.lib.marketplace.equity import Equity
from robinhood.lib.marketplace.marketplace import marketplace


class AccountSummary(object):

    def __init__(self, symbol_history: SymbolHistory) -> None:
        self._symbol_history = symbol_history

    def show(self) -> None:
        print(self._gen_reports())

    def _gen_reports(self) -> str:
        equities = marketplace.get_equities(symbols=account.active_symbols)

        account_summary_report = self._gen_account_summary_report(
            active_symbols=account.active_symbols,
            equities=equities,
            margin_used=account.margin_used,
            buying_power=account.buying_power,
        )
        individual_report = self._gen_individual_report(
            active_symbols=account.active_symbols,
            equities=equities,
        )

        return f'{account_summary_report}\n\n{individual_report}'

    def _gen_account_summary_report(
        self,
        active_symbols: Set[str],
        equities: Dict[str, Equity],
        margin_used: float,
        buying_power: float,
    ) -> str:
        data = self._gen_account_summary_report_data(
            active_symbols=active_symbols,
            equities=equities,
            margin_used=margin_used,
            buying_power=buying_power,
        )
        t = AsciiTable(data)
        t.inner_column_border = True
        t.inner_footing_row_border = False
        t.inner_heading_row_border = True
        t.inner_row_border = False
        t.outer_border = False
        t.justify_columns = {
            0: 'right',
            1: 'right',
            2: 'right',
            3: 'right',
            4: 'right',
            5: 'right',
            6: 'right',
            7: 'right',
            8: 'right',
            9: 'right',
        }

        return str(t.table)

    def _gen_individual_report(
        self,
        active_symbols: Set[str],
        equities: Dict[str, Equity],
    ) -> str:
        data = self._gen_individual_report_data(
            active_symbols=active_symbols,
            equities=equities,
        )
        t = AsciiTable(data)
        t.inner_column_border = True
        t.inner_footing_row_border = False
        t.inner_heading_row_border = True
        t.inner_row_border = False
        t.outer_border = False
        t.justify_columns = {
            0: 'right',
            1: 'right',
            2: 'right',
            3: 'right',
            4: 'right',
            5: 'right',
            6: 'right',
            7: 'right',
            8: 'right',
        }

        return str(t.table)

    def _gen_account_summary_report_data(
        self,
        active_symbols: Set[str],
        equities: Dict[str, Equity],
        margin_used: float,
        buying_power: float,
    ) -> List[List[str]]:
        stock_value = self._get_stock_value(
            active_symbols=active_symbols,
            equities=equities,
        )

        profit_on_stocks = self._get_profit_on_stocks(
            active_symbols=active_symbols,
            equities=equities,
        )

        option_value = self._get_option_value(active_symbols=active_symbols)
        account_value = stock_value + option_value - margin_used
        profit_on_options = self._get_profit_on_options(active_symbols=active_symbols)
        profit_on_call_writes = self._get_profit_on_call_writes(
            active_symbols=active_symbols,
            equities=equities,
        )

        profit_on_put_writes = self._get_profit_on_put_writes(
            active_symbols=active_symbols,
            equities=equities,
        )

        data = [[
            'Stock Value',
            'Option Value',
            'Margin Used',
            'Account Value',
            'Buying Power',
            '# of Symbols',
            'Profit on Stocks',
            'Profit on Options',
            'Profit on Call Writes',
            'Profit on Put Writes',
        ]]
        data.append([
            format_price(stock_value),
            format_price(option_value),
            format_price(margin_used),
            format_price(account_value),
            format_price(buying_power),
            format_quantity(len(active_symbols)),
            format_price(profit_on_stocks),
            format_price(profit_on_options),
            format_price(profit_on_call_writes),
            format_price(profit_on_put_writes),
        ])
        return data

    def _gen_individual_report_data(
        self,
        active_symbols: Set[str],
        equities: Dict[str, Equity],
    ) -> List[List[str]]:
        data = [[
            'Symbol',
            'Last Price',
            '# of Shares',
            'Stock Value',
            'Option Value',
            'Settled Profit',
            'Profit on Stocks',
            'Profit on Options',
            'Profit on Call Writes',
            'Profit on Put Writes',
        ]]

        with ThreadPoolExecutor() as executor:
            futures = [
                executor.submit(
                    self._gen_individual_report_data_for_one_symbol,
                    symbol,
                    active_symbols,
                    equities,
                )
                for symbol in active_symbols
            ]

        rows: List[List[str]] = []
        for future in as_completed(futures):
            rows.append(future.result())

        data.extend(sorted(rows, key=lambda row: row[0]))

        return data

    def _gen_individual_report_data_for_one_symbol(
        self,
        symbol: str,
        active_symbols: Set[str],
        equities: Dict[str, Equity],
    ) -> List[str]:
        equity = equities[symbol]
        num_of_shares = self._symbol_history.get_events(symbol)[-1].context.stock_holding.quantity
        stock_cost_basis = self._symbol_history.get_events(symbol)[-1].context.stock_holding.stock_cost_basis
        stock_value = num_of_shares * equity.last_price
        stock_profit = stock_value - stock_cost_basis
        settled_profit = self._symbol_history.get_events(symbol)[-1].context.profit
        option_value = self._get_option_value(
            active_symbols=active_symbols,
            selected_symbol=symbol,
        )
        option_profit = self._get_profit_on_options(
            active_symbols=active_symbols,
            selected_symbol=symbol,
        )
        profit_on_call_writes = self._get_profit_on_call_writes(
            active_symbols=active_symbols,
            equities=equities,
            selected_symbol=symbol,
        )
        profit_on_put_writes = self._get_profit_on_put_writes(
            active_symbols=active_symbols,
            equities=equities,
            selected_symbol=symbol,
        )
        data = [
            symbol,
            format_price(equities[symbol].last_price),
            format_quantity(num_of_shares),
            format_price(stock_value, empty_for_zero=True),
            format_price(option_value, empty_for_zero=True),
            format_price(settled_profit, empty_for_zero=True),
            format_price(stock_profit, empty_for_zero=True),
            format_price(option_profit, empty_for_zero=True),
            format_price(profit_on_call_writes, empty_for_zero=True),
            format_price(profit_on_put_writes, empty_for_zero=True),
        ]

        return data

    def _get_stock_value(
        self,
        active_symbols: Set[str],
        equities: Dict[str, Equity],
    ) -> float:
        value = 0.0
        for symbol in active_symbols:
            stock_holding = self._symbol_history.get_events(symbol=symbol)[-1].context.stock_holding
            if stock_holding.quantity > 0:
                value += equities[symbol].last_price * stock_holding.quantity

        return value

    def _get_profit_on_stocks(
        self,
        active_symbols: Set[str],
        equities: Dict[str, Equity],
    ) -> float:
        profit = 0.0
        for symbol in active_symbols:
            stock_holding = self._symbol_history.get_events(symbol=symbol)[-1].context.stock_holding
            if stock_holding.quantity > 0:
                profit += (equities[symbol].last_price - stock_holding.avg_unit_price) * stock_holding.quantity

        return profit

    def _get_option_value(
        self,
        active_symbols: Set[str],
        selected_symbol: Optional[str] = None,
    ) -> float:
        value = 0.0
        for symbol in active_symbols:
            if selected_symbol is not None and symbol != selected_symbol:
                continue

            context = self._symbol_history.get_events(symbol=symbol)[-1].context
            for _, holding in context.option_buy_holding.items():
                value += holding.option_buy_value

        return value

    def _get_profit_on_options(
        self,
        active_symbols: Set[str],
        selected_symbol: Optional[str] = None,
    ) -> float:
        profit = 0.0
        for symbol in active_symbols:
            if selected_symbol is not None and symbol != selected_symbol:
                continue

            context = self._symbol_history.get_events(symbol=symbol)[-1].context
            for _, holding in context.option_buy_holding.items():
                profit += holding.option_buy_profit

        return profit

    def _get_profit_on_call_writes(
        self,
        active_symbols: Set[str],
        equities: Dict[str, Equity],
        selected_symbol: Optional[str] = None,
    ) -> float:
        profit = 0.0
        for symbol in active_symbols:
            if selected_symbol is not None and symbol != selected_symbol:
                continue

            context = self._symbol_history.get_events(symbol=symbol)[-1].context
            for _, holding in context._option_sell_holding.items():
                option_instrument = holding.option_instrument
                stock_price = equities[option_instrument.chain_symbol].last_price
                if option_instrument.instrument_type == 'call':
                    if option_instrument.strike_price >= stock_price:
                        current_profit = holding.avg_unit_price * holding.quantity * 100
                    else:
                        current_profit = (
                            holding.avg_unit_price
                            - stock_price
                            + option_instrument.strike_price
                        ) * holding.quantity * 100

                    profit += current_profit

        return profit

    def _get_profit_on_put_writes(
        self,
        active_symbols: Set[str],
        equities: Dict[str, Equity],
        selected_symbol: Optional[str] = None,
    ) -> float:
        profit = 0.0
        for symbol in active_symbols:
            if selected_symbol is not None and symbol != selected_symbol:
                continue

            context = self._symbol_history.get_events(symbol=symbol)[-1].context
            for _, holding in context._option_sell_holding.items():
                option_instrument = holding.option_instrument
                stock_price = equities[option_instrument.chain_symbol].last_price
                if option_instrument.instrument_type == 'put':
                    if option_instrument.strike_price <= stock_price:
                        current_profit = holding.avg_unit_price * holding.quantity * 100
                    else:
                        current_profit = (
                            holding.avg_unit_price
                            - option_instrument.strike_price
                            + stock_price
                        ) * holding.quantity * 100

                    profit += current_profit

        return profit
