from data.watchlist import ALL
from robinhood.lib.marketplace.marketplace import marketplace


symbols = {'AAPL', 'MSFT'}


def test_get_equities_endpoint() -> None:
    endpoint = marketplace._get_equities_endpoint(symbols=symbols)
    assert endpoint in {
        'https://api.robinhood.com/quotes/?symbols=AAPL,MSFT',
        'https://api.robinhood.com/quotes/?symbols=MSFT,AAPL',
    }


def test_get_equities() -> None:
    equities = marketplace.get_equities(symbols=symbols)
    assert len(equities.keys()) == 2
    for symbol in equities.keys():
        assert symbol in symbols


def test_equity_instrument_ids_not_change() -> None:
    equities = marketplace.get_equities(symbols=set(ALL.keys()))
    for symbol, equity in equities.items():
        assert equity.instrument_id == ALL[symbol]


def test_get_option_chains() -> None:
    option_chain_ids = {
        'AAPL': 'cee01a93-626e-4ee6-9b04-60e2fd1392d1',
        'MSFT': '1ac71e01-0677-42c6-a490-1457980954f8',
    }
    equity_instrument_ids = [ALL[symbol] for symbol in symbols]
    option_chains = marketplace.get_option_chains(equity_instrument_ids=equity_instrument_ids)
    assert len(option_chains) == 2
    for symbol, option_chain in option_chains.items():
        assert symbol in symbols
        assert option_chain.chain_id == option_chain_ids[symbol]
