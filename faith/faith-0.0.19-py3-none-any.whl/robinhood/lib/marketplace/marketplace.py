from concurrent.futures import as_completed
from concurrent.futures import ThreadPoolExecutor
from typing import Dict
from typing import List
from typing import Set

from robinhood.lib.marketplace.equity import Equity
from robinhood.lib.marketplace.equity import equity_from_data
from robinhood.lib.marketplace.optionchain import option_chain_from_data
from robinhood.lib.marketplace.optionchain import OptionChain
from robinhood.lib.robinhoodclient import rhc


class Marketplace(object):

    STOCKS_OPTION_CHAINS_BATCH_SIZE = 64

    def __init__(self) -> None:
        pass

    def get_equities(self, symbols: Set[str]) -> Dict[str, Equity]:
        endpoint = self._get_equities_endpoint(symbols=symbols)
        equities: List[Equity] = rhc.get_objects(
            url=endpoint,
            result_key='results',
            callback=equity_from_data,
        )
        results: Dict[str, Equity] = {}
        for equity in equities:
            results[equity.symbol] = equity

        return results

    def get_option_chains(self, equity_instrument_ids: List[str]) -> Dict[str, OptionChain]:
        num_of_batches = self._get_num_of_option_chains_batches(n=len(equity_instrument_ids))
        with ThreadPoolExecutor() as executor:
            N = self.STOCKS_OPTION_CHAINS_BATCH_SIZE
            futures = [
                executor.submit(
                    self._get_option_chains_one_batch,
                    equity_instrument_ids[i * N:(i + 1) * N],
                )
                for i in range(num_of_batches)
            ]

        option_chains: Dict[str, OptionChain] = {}
        for future in as_completed(futures):
            option_chains.update(future.result())

        return option_chains

    def _get_num_of_option_chains_batches(self, n: int) -> int:
        num_of_batches = n // self.STOCKS_OPTION_CHAINS_BATCH_SIZE
        if n % self.STOCKS_OPTION_CHAINS_BATCH_SIZE > 0:
            num_of_batches += 1

        return num_of_batches

    def _get_option_chains_one_batch(self, equity_instrument_ids: List[str]) -> Dict[str, OptionChain]:
        n = len(equity_instrument_ids)
        assert n <= self.STOCKS_OPTION_CHAINS_BATCH_SIZE

        endpoint = self._get_option_chains_end_point(equity_instrument_ids=equity_instrument_ids)
        option_chains = rhc.get_objects(
            url=endpoint,
            result_key='results',
            callback=option_chain_from_data,
        )
        results: Dict[str, OptionChain] = {}
        for option_chain in option_chains:
            results[option_chain.symbol] = option_chain

        return results

    def _get_equities_endpoint(self, symbols: Set[str]) -> str:
        comma_separated_symbols = ','.join(symbols)
        return f'https://api.robinhood.com/quotes/?symbols={comma_separated_symbols}'

    def _get_option_chains_end_point(self, equity_instrument_ids: List[str]) -> str:
        n = len(equity_instrument_ids)
        assert n <= self.STOCKS_OPTION_CHAINS_BATCH_SIZE

        ids = ','.join(equity_instrument_ids)
        return f'https://api.robinhood.com/options/chains/?equity_instrument_ids={ids}'


marketplace = Marketplace()
