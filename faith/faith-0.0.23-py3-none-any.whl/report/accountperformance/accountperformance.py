from collections import defaultdict
from datetime import datetime
from typing import DefaultDict
from typing import List
from typing import Set

from terminaltables import AsciiTable

from report.symbolhistory.symbolhistory import SymbolHistory
from robinhood.lib.helpers import format_price
from robinhood.lib.helpers import get_month
from robinhood.lib.helpers import get_week


class AccountPerformance(object):

    def __init__(self, symbol_history: SymbolHistory) -> None:
        self._symbol_history = symbol_history

    def show(self, interval: str) -> None:
        assert interval in {'Week', 'Month', 'All Time'}
        print(self._gen_reports(interval=interval))

    def _gen_reports(self, interval: str) -> str:
        data = self._gen_data(interval=interval)
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
        }

        return str(t.table)

    def _gen_data(self, interval: str) -> List[List[str]]:
        if interval == 'Week':
            event_date_func = get_week
        elif interval == 'Month':
            event_date_func = get_month
        else:
            assert interval == 'All Time'

            def event_date_func(d: datetime) -> str:
                return '-'

        data = [[
            interval,
            'Settled Profit from Stock',
            'Settled Profit from Option',
            'Total Settled Profit',
        ]]

        stock_profit: DefaultDict[str, float] = defaultdict(float)
        option_profit: DefaultDict[str, float] = defaultdict(float)

        for _, events in self._symbol_history.events_by_symbol.items():
            for i in range(1, len(events)):
                previous_event = events[i - 1]
                current_event = events[i]
                diff = current_event.context.profit - previous_event.context.profit
                if diff != 0:
                    event_date = event_date_func(current_event.event_ts)

                    if current_event.event_name in {
                        'BUY TO CLOSE',
                        'CUSTOM',
                        'CUSTOM CLOSE',
                        'FIG LEAF CLOSE',
                        'IRON CONDOR CLOSE',
                        'LONG CALL CLOSE',
                        'LONG CALL SPREAD CLOSE',
                        'LONG PUT CLOSE',
                        'LONG PUT SPREAD CLOSE',
                        'OPTION EXPIRATION',
                        'ROLLING SHORT CALL SPREAD',
                        'SHORT CALL SPREAD CLOSE',
                        'SHORT PUT SPREAD CLOSE',
                    }:
                        option_profit[event_date] += diff
                    elif current_event.event_name in {
                        'CALL ASSIGNMENT',
                        'LIMIT SELL',
                        'MARKET SELL',
                    }:
                        stock_profit[event_date] += diff
                    else:
                        raise Exception(f'Unrecognized event name: {current_event.event_name}')

        all_dates: Set[str] = set()
        for event_date in stock_profit.keys():
            all_dates.add(event_date)
        for event_date in option_profit.keys():
            all_dates.add(event_date)

        for event_date in sorted(list(all_dates)):
            total_profit = stock_profit[event_date] + option_profit[event_date]
            data.append([
                event_date,
                format_price(stock_profit[event_date]),
                format_price(option_profit[event_date]),
                format_price(total_profit),
            ])

        return data
