from report.accountsummary.accountsummary import AccountSummary
from report.symbolhistory.symbolhistory import SymbolHistory
from robinhood.lib.account.account import account


account.update_in_parallel()
symbol_history = SymbolHistory(
    stock_orders=account.stock_orders,
    option_orders=account.option_orders,
    option_events=account.option_events,
)
report = AccountSummary(symbol_history=symbol_history)


def test_gen_reports() -> None:
    text = report._gen_reports()
    for s in {
        'Stock Value',
        'Option Value',
        'Margin Used',
        'Account Value',
        '# of Symbols',
        'Profit on Stocks',
        'Profit on Options',
        'Profit on Call Writes',
        'Profit on Put Writes',
        'Symbol',
        '# of Shares',
        'Settled Profit',
        'Last Price',
        'Buying Power',
    }:
        assert s in text
