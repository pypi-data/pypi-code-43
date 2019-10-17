from concurrent.futures import as_completed
from concurrent.futures import Future
from concurrent.futures import ThreadPoolExecutor
from typing import cast
from typing import List
from typing import Optional
from typing import Union

from terminaltables import AsciiTable

from data.watchlist import ALL
from report.optionsellscreener.optionsellcandidate import OptionSellCandidate
from robinhood.lib.helpers import format_percentage
from robinhood.lib.helpers import format_price
from robinhood.lib.helpers import format_quantity
from robinhood.lib.marketplace.marketplace import marketplace
from robinhood.lib.marketplace.optioninstrument import OptionInstrument
from robinhood.lib.marketplace.optionmarketdata import OptionMarketData


class OptionSellScreener(object):

    def __init__(
        self,
        exp_date: str,
        option_type: str,
        min_chance_of_profit: float,
        min_fund_efficiency: float = 0.0075,
    ) -> None:
        self._exp_date = exp_date
        self._option_type = option_type
        self._min_chance_of_profit = min_chance_of_profit
        self._min_fund_efficiency = min_fund_efficiency

    def show(self) -> None:
        data = self._gen_ascii_tbl_data()
        if len(data) == 1:
            print('No good candidates...')
            return

        t = AsciiTable(data)
        t.inner_column_border = True
        t.inner_footing_row_border = False
        t.inner_heading_row_border = True
        t.inner_row_border = False
        t.outer_border = False
        t.justify_columns = {
            0: 'center',
            1: 'right',
            2: 'right',
            3: 'right',
            4: 'right',
            5: 'right',
            6: 'right',
            7: 'right',
            8: 'right',
            9: 'right',
            10: 'right',
        }
        print(t.table)

    def _gen_ascii_tbl_data(self) -> List[List[str]]:
        data = [[
            'Symbol',
            'Strike Price',
            'Current Price',
            '% to Strike',
            'Chance',
            'H.SP',
            'M.SP',
            'L.SP',
            'Est. Profit',
            'Efficiency',
            'Open Interest',
        ]]

        option_sell_candidates = self._get_option_sell_candidates()
        symbols = {
            option_sell_candidate.chain_symbol
            for option_sell_candidate in option_sell_candidates
        }
        if len(symbols) == 0:
            return data

        equities = marketplace.get_equities(symbols=symbols)
        rows: List[List[Union[str, float]]] = []
        for option_sell_candidate in option_sell_candidates:
            rows.append(
                option_sell_candidate.gen_data_row(
                    chain_symbol_market_data=equities[option_sell_candidate.chain_symbol],
                ),
            )
        rows = sorted(rows, key=lambda x: x[8], reverse=True)
        for row in rows:
            data.append(self._format_data_row(row=row))

        return data

    def _format_data_row(self, row: List[Union[str, float]]) -> List[str]:
        assert len(row) == 11

        new_row: List[str] = []
        for i in range(len(row)):
            if i == 0:
                new_row.append(cast(str, row[i]))
            elif i in [1, 2, 5, 6, 7, 8]:
                new_row.append(format_price(cast(float, row[i])))
            elif i in [3, 4, 9]:
                new_row.append(format_percentage(cast(float, row[i])))
            else:
                new_row.append(format_quantity(cast(float, row[i])))

        return new_row

    def _get_option_sell_candidates(self) -> List[OptionSellCandidate]:
        ids = self._get_all_equity_instrument_ids()
        option_chains = marketplace.get_option_chains(ids)
        with ThreadPoolExecutor() as executor:
            future_option_instruments = [
                executor.submit(
                    option_chain.get_option_instruments,
                    self._exp_date,
                    self._option_type,
                )
                for symbol, option_chain in option_chains.items()
            ]

            future_candidates: List[Future[Optional[OptionSellCandidate]]] = []
            for future_option_instrument in as_completed(future_option_instruments):
                option_instruments = future_option_instrument.result()
                future_candidates.append(
                    executor.submit(
                        self._find_best_option_instruments,
                        option_instruments,
                    ),
                )

        option_sell_candidates: List[OptionSellCandidate] = []
        for future_candidate in as_completed(future_candidates):
            option_sell_candidate = future_candidate.result()
            if option_sell_candidate is not None:
                option_sell_candidates.append(option_sell_candidate)

        return option_sell_candidates

    def _find_best_option_instruments(
        self,
        option_instruments: List[OptionInstrument],
    ) -> Optional[OptionSellCandidate]:
        start_idx = 0
        end_idx = len(option_instruments)
        best_option_instrument: Optional[OptionInstrument] = None
        best_market_data: Optional[OptionMarketData] = None
        while start_idx <= end_idx:
            if len(option_instruments) == 0 or start_idx == end_idx == len(option_instruments):
                return None

            i = (start_idx + end_idx) // 2
            option_instrument = option_instruments[i]
            market_data = option_instrument.market_data
            if (
                market_data is None
                or market_data.chance_of_profit_short is None
                or market_data.high_fill_rate_sell_price == 0.0
                or market_data.open_interest < 10
            ):
                del option_instruments[i]
                end_idx -= 1
                continue

            if market_data.chance_of_profit_short > self._min_chance_of_profit:
                if (
                    best_option_instrument is None
                    or (
                        best_market_data is not None
                        and best_market_data.chance_of_profit_short is not None
                        and market_data.chance_of_profit_short < best_market_data.chance_of_profit_short
                    )
                ):
                    best_option_instrument = option_instruments[i]
                    best_market_data = market_data

                start_idx = i + 1
            else:
                end_idx = i - 1

        if best_option_instrument is not None:
            assert best_market_data is not None
            fund_efficiency = self._fund_efficiency(
                option_instrument=best_option_instrument,
                market_data=best_market_data,
            )
            if fund_efficiency >= self._min_fund_efficiency:
                return OptionSellCandidate(
                    option_instrument=best_option_instrument,
                    market_data=best_market_data,
                    fund_efficiency=fund_efficiency,
                )

        return None

    def _get_all_equity_instrument_ids(self) -> List[str]:
        return list(ALL.values())

    def _fund_efficiency(
        self,
        option_instrument: OptionInstrument,
        market_data: OptionMarketData,
    ) -> float:
        assert market_data.medium_fill_rate_sell_price is not None
        return market_data.medium_fill_rate_sell_price / option_instrument.strike_price
