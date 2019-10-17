from collections import defaultdict
from collections import OrderedDict
from concurrent.futures import as_completed
from concurrent.futures import ThreadPoolExecutor
from typing import Any
from typing import DefaultDict
from typing import Dict
from typing import Iterator
from typing import List
from typing import Optional
from typing import Tuple

from asciitree import LeftAligned
from termcolor import colored
from terminaltables import AsciiTable

from data.watchlist import ALL_REVERSED
from report.symbolhistory.symbolhistorycontext import SymbolHistoryContext
from report.symbolhistory.symbolhistoryevent import symbol_history_event_from_option_event
from report.symbolhistory.symbolhistoryevent import symbol_history_event_from_option_order
from report.symbolhistory.symbolhistoryevent import symbol_history_event_from_stock_order
from report.symbolhistory.symbolhistoryevent import SymbolHistoryEvent
from robinhood.lib.account.account import account
from robinhood.lib.account.optionevent.optionevent import OptionEvent
from robinhood.lib.account.optionorder.optionleg import OptionLeg
from robinhood.lib.account.optionorder.optionorder import OptionOrder
from robinhood.lib.account.stockorder.stockorder import StockOrder
from robinhood.lib.helpers import format_optional_greek
from robinhood.lib.helpers import format_optional_price
from robinhood.lib.helpers import format_percentage
from robinhood.lib.helpers import format_price
from robinhood.lib.helpers import format_quantity
from robinhood.lib.marketplace.equity import Equity
from robinhood.lib.marketplace.marketplace import marketplace
from robinhood.lib.marketplace.optioninstrument import OptionInstrument
from robinhood.lib.marketplace.optionmarketdata import OptionMarketData
from robinhood.lib.robinhoodclient import rhc


T = Tuple[str, 'OrderedDict[str, Any]', OptionInstrument, Optional[OptionMarketData], int, float]


class SymbolHistory(object):

    def __init__(
        self,
        stock_orders: List[StockOrder],
        option_orders: List[OptionOrder],
        option_events: List[OptionEvent],
    ) -> None:
        self._events_by_symbol = self._load_events_by_symbol(
            stock_orders=stock_orders,
            option_orders=option_orders,
            option_events=option_events,
        )

    @property
    def events_by_symbol(self) -> DefaultDict[str, List[SymbolHistoryEvent]]:
        return self._events_by_symbol

    def get_events(self, symbol: str) -> List[SymbolHistoryEvent]:
        return self._events_by_symbol[symbol]

    def show_current_positions(self) -> None:
        active_symbol = account.active_symbols
        equaities = marketplace.get_equities(symbols=active_symbol)

        with ThreadPoolExecutor() as executor:
            futures = [
                executor.submit(
                    self.get_current_position_report,
                    symbol=symbol,
                    equity=equaities[symbol],
                )
                for symbol in active_symbol
            ]

        reports_by_symbol: Dict[str, str] = {}
        total_profit = 0.0
        total_profit_by_exp_date: DefaultDict[str, float] = defaultdict(float)
        for future in as_completed(futures):
            symbol, report, profit_by_exp_date = future.result()
            reports_by_symbol.update({symbol: report})
            for exp_date, profit in profit_by_exp_date.items():
                total_profit_by_exp_date[exp_date] += profit
                total_profit += profit

        color = 'green' if total_profit >= 0 else 'red'
        total_profit_key = f'Total Profit: {colored(format_price(total_profit), color)}'
        profit_by_exp_date_tree: OrderedDict[str, Any] = OrderedDict()
        for exp_date in sorted(total_profit_by_exp_date.keys()):
            profit = total_profit_by_exp_date[exp_date]
            color = 'green' if profit >= 0 else 'red'
            profit_by_exp_date_tree[f'By {exp_date}: {colored(format_price(profit), color)}'] = {}
        profit_tree = {total_profit_key: profit_by_exp_date_tree}
        tree = LeftAligned()
        print(tree(profit_tree))
        print()

        for symbol in sorted(reports_by_symbol.keys()):
            print(reports_by_symbol[symbol])
            print()

    def get_current_position_report(self, symbol: str, equity: Equity) -> Tuple[str, str, Dict[str, float]]:
        events = self.get_events(symbol=symbol)
        if len(events) == 0:
            report = f'No event for {symbol}...'
            return (symbol, report, {})

        event = events[-1]

        # Stock
        symbol_with_price = '{symbol} {last_price} {dod_change}'.format(
            symbol=symbol,
            last_price=format_price(equity.last_price),
            dod_change=format_percentage(equity.dod_percentage),
        )
        symbol_data: OrderedDict[str, Any] = OrderedDict()

        stock_key, stock_details = self._get_current_stock_holding(
            event=event,
            last_price=equity.last_price,
        )
        symbol_data[stock_key] = stock_details

        # Option Buy and Sell
        option_holding_data: List[T] = []
        for buy_or_sell in ['Buy', 'Sell']:
            option_holding_data.extend(
                self._get_current_option_buy_or_sell_holding(
                    event=event,
                    last_price=equity.last_price,
                    buy_or_sell=buy_or_sell,
                ),
            )

        total_profit_by_exp_date: DefaultDict[str, float] = defaultdict(float)
        exp_dates = sorted(list({
            option_instrument.exp_date
            for _, _, option_instrument, _, _, _ in option_holding_data
        }))
        for exp_date in exp_dates:
            days_to_expire: Optional[int] = None
            current_exp_date_data: List[T] = []
            for option_key, option_details, option_instrument, market_data, quantity, profit in option_holding_data:
                if option_instrument.exp_date == exp_date:
                    current_exp_date_data.append(
                        (
                            option_key,
                            option_details,
                            option_instrument,
                            market_data,
                            quantity,
                            profit,
                        ),
                    )
                    days_to_expire = option_instrument.days_to_expire

            assert days_to_expire is not None
            option_exp_date_key = 'Option Holding w/ Exp Date: {exp_date} ({days_to_expire})'.format(
                exp_date=exp_date,
                days_to_expire=days_to_expire,
            )

            current_option_holding: OrderedDict[str, Any] = OrderedDict()

            # Profit
            subtotal_profit = 0.0
            for _, _, _, _, _, profit in current_exp_date_data:
                subtotal_profit += profit
            color = 'green' if subtotal_profit >= 0 else 'red'
            subtotal_profit_key = f'Total Profit: {colored(format_price(subtotal_profit), color)}'
            current_option_holding[subtotal_profit_key] = {}
            total_profit_by_exp_date[exp_date] += subtotal_profit

            # Overall Greeks
            if market_data is not None:
                theta_total = 0.0
                delta_total = 0.0
                gamma_total = 0.0
                vega_total = 0.0
                rho_total = 0.0
                total_quantity = 0
                for _, _, _, market_data, quantity, _ in current_exp_date_data:
                    if market_data is None:
                        continue
                    if market_data.theta is None:
                        continue
                    if market_data.delta is None:
                        continue
                    if market_data.gamma is None:
                        continue
                    if market_data.vega is None:
                        continue
                    if market_data.rho is None:
                        continue

                    theta_total = market_data.theta * quantity
                    delta_total = market_data.delta * quantity
                    gamma_total = market_data.gamma * quantity
                    vega_total = market_data.vega * quantity
                    rho_total = market_data.rho * quantity
                    total_quantity += quantity

                if total_quantity > 0:
                    overall_greek_key = 'Theta: {theta} Delta: {delta} Gamma: {gamma} Vega: {vega} Rho: {rho}'.format(
                        theta=format_optional_greek(theta_total / total_quantity),
                        delta=format_optional_greek(delta_total / total_quantity),
                        gamma=format_optional_greek(gamma_total / total_quantity),
                        vega=format_optional_greek(vega_total / total_quantity),
                        rho=format_optional_greek(rho_total / total_quantity),
                    )
                    current_option_holding[overall_greek_key] = {}

            # Invidual Holding
            for option_key, option_details, _, _, _, _ in sorted(
                current_exp_date_data,
                key=lambda x: x[2].strike_price,
                reverse=True,
            ):
                current_option_holding[option_key] = option_details

            symbol_data[option_exp_date_key] = current_option_holding

        data = {symbol_with_price: symbol_data}

        tree = LeftAligned()
        return (symbol, tree(data), total_profit_by_exp_date)

    def _get_current_stock_holding(
        self,
        event: SymbolHistoryEvent,
        last_price: float,
    ) -> 'Tuple[str, OrderedDict[str, Any]]':
        stock_quantity = event.context.stock_holding.quantity
        stock_avg_price = event.context.stock_holding.avg_unit_price
        stock_total_value = stock_quantity * stock_avg_price
        if stock_quantity == 0:
            stock_holding = 'none'
        else:
            stock_holding = '{quantity} x {avg_price} = {total_value}'.format(
                quantity=stock_quantity,
                avg_price=format_price(stock_avg_price),
                total_value=format_price(stock_total_value),
            )
        stock_key = f'Stock Holding: {stock_holding}'
        stock_details: OrderedDict[str, Any] = OrderedDict()

        if stock_quantity > 0:
            current_value = last_price * stock_quantity
            stock_details['Current Value: {value} ({change})'.format(
                value=format_price(current_value),
                change=format_percentage(current_value / stock_total_value - 1),
            )] = {}

        return (stock_key, stock_details)

    def _get_current_option_buy_or_sell_holding(
        self,
        event: SymbolHistoryEvent,
        last_price: float,
        buy_or_sell: str,
    ) -> 'Iterator[T]':
        if buy_or_sell == 'Buy':
            holding_dict = event.context.option_buy_holding
        else:
            holding_dict = event.context.option_sell_holding

        for _, item in holding_dict.items():
            total_base_price = item.avg_unit_price * item.quantity * 100
            if item.option_instrument.instrument_type == 'call':
                if last_price > item.option_instrument.strike_price:
                    diff = last_price - item.option_instrument.strike_price
                    above_or_below = 'above'
                    breached = colored('BREACHED', 'red')
                else:
                    diff = item.option_instrument.strike_price - last_price
                    above_or_below = 'below'
                    breached = colored('NOT BREACHED', 'green')
            else:
                assert item.option_instrument.instrument_type == 'put'
                if last_price < item.option_instrument.strike_price:
                    diff = item.option_instrument.strike_price - last_price
                    above_or_below = 'below'
                    breached = colored('BREACHED', 'red')
                else:
                    diff = last_price - item.option_instrument.strike_price
                    above_or_below = 'above'
                    breached = colored('NOT BREACHED', 'green')
            breached_key = '{breached} - {above_or_below} strike price {diff_dollar} or {diff_percentage}'.format(
                above_or_below=above_or_below,
                diff_dollar=format_price(diff),
                diff_percentage=format_percentage(diff / last_price),
                breached=breached,
            )

            option_sell_key = (
                '{buy_or_sell} {call_or_put} {strike_price}: {quantity} x {avg_price} = {base_price}'.format(
                    buy_or_sell=buy_or_sell,
                    strike_price=format_price(item.option_instrument.strike_price),
                    call_or_put=item.option_instrument.instrument_type.upper(),
                    exp_date=item.option_instrument.exp_date,
                    quantity=item.quantity,
                    avg_price=format_price(item.avg_unit_price),
                    base_price=format_price(total_base_price),
                )
            )
            market_data = item.option_instrument.market_data
            if market_data is None:
                current_price = '-'
                profit_value = 0.0
                profit = '-'
                theta = '-'
                delta = '-'
                gamma = '-'
                vega = '-'
                rho = '-'
            else:
                current_price = format_optional_price(market_data.medium_fill_rate_sell_price)
                if market_data.medium_fill_rate_sell_price is None:
                    profit = '-'
                else:
                    if buy_or_sell == 'Sell':
                        profit_value = (
                            (item.avg_unit_price - market_data.medium_fill_rate_sell_price) * item.quantity * 100
                        )
                        color = 'red' if market_data.medium_fill_rate_sell_price > item.avg_unit_price else 'green'
                    else:
                        assert buy_or_sell == 'Buy'
                        profit_value = (
                            (market_data.medium_fill_rate_sell_price - item.avg_unit_price) * item.quantity * 100
                        )
                        color = 'green' if market_data.medium_fill_rate_sell_price > item.avg_unit_price else 'red'
                    abs_diff = abs(market_data.medium_fill_rate_sell_price - item.avg_unit_price)
                    profit = colored(format_price(abs_diff * item.quantity * 100), color)
                theta = format_optional_greek(market_data.theta)
                delta = format_optional_greek(market_data.delta)
                gamma = format_optional_greek(market_data.gamma)
                vega = format_optional_greek(market_data.vega)
                rho = format_optional_greek(market_data.rho)

            current_price_key = f'Current Price: {current_price}, Profit: {profit}'
            greek_key = f'Theta: {theta} Delta: {delta} Gamma: {gamma} Vega: {vega} Rho: {rho}'

            option_sell_details: OrderedDict[str, Any] = OrderedDict()
            option_sell_details[current_price_key] = {}
            option_sell_details[breached_key] = {}
            option_sell_details[greek_key] = {}

            yield (
                option_sell_key,
                option_sell_details,
                item.option_instrument,
                market_data,
                item.quantity,
                profit_value,
            )

    def show(self, symbol: str, last_n_events: Optional[int] = 10) -> None:
        data = self._gen_ascii_tbl_data(symbol=symbol)
        if last_n_events is None:
            applicable_data = data
        else:
            data_no_head = data[1:]
            applicable_data = [data[0]] + data_no_head[-last_n_events - 1:]
        t = AsciiTable(applicable_data)
        t.inner_column_border = True
        t.inner_footing_row_border = False
        t.inner_heading_row_border = True
        t.inner_row_border = False
        t.outer_border = False
        t.justify_columns = {
            0: 'center',
            1: 'center',
            2: 'center',
            3: 'right',
            4: 'right',
            5: 'right',
            6: 'right',
            7: 'right',
        }
        print(t.table)

    def show_holdings_by_events(self, symbol: str) -> None:
        events = self.get_events(symbol=symbol)
        for event in events:
            print(event.event_name)
            quantity = event.context.stock_holding.quantity
            avg_price = event.context.stock_holding.avg_unit_price
            print('>>> Stock Holding: {quantity} x {avg_price} = {total_value}'.format(
                quantity=format_quantity(quantity),
                avg_price=format_price(avg_price),
                total_value=format_price(quantity * avg_price),
            ))

            for _, item in event.context.option_buy_holding.items():
                print('>>> Option Buy Holding: {quantity} x {avg_price} = {total_value}'.format(
                    quantity=format_quantity(item.quantity),
                    avg_price=format_price(item.avg_unit_price),
                    total_value=format_price(item.quantity * item.avg_unit_price),
                ))

            for _, item in event.context.option_sell_holding.items():
                print('>>> Option Sell Holding: {quantity} x {avg_price} = {total_value}'.format(
                    quantity=format_quantity(item.quantity),
                    avg_price=format_price(item.avg_unit_price),
                    total_value=format_price(item.quantity * item.avg_unit_price),
                ))

            print()

    def _gen_ascii_tbl_data(self, symbol: str) -> List[List[str]]:
        data = [[
            'Date',
            'Event',
            'Symbol',
            'Quantity',
            'Price',
            '# of Shares',
            'Avg Price',
            'Cumulative Profit',
        ]]

        for event in self._events_by_symbol[symbol]:
            # could be option legs from vertical
            if event.context is None:
                continue

            data.append(
                [
                    event.formatted_ts,
                    event.event_name,
                    event.symbol,
                    format_quantity(event.quantity),
                    format_optional_price(event.unit_price),
                    format_quantity(event.context.stock_holding.quantity),
                    format_price(event.context.stock_holding.avg_unit_price),
                    format_price(event.context.profit),
                ],
            )

        return data

    def _load_events_by_symbol(
        self,
        stock_orders: List[StockOrder],
        option_orders: List[OptionOrder],
        option_events: List[OptionEvent],
    ) -> DefaultDict[str, List[SymbolHistoryEvent]]:
        events_by_symbol: DefaultDict[str, List[SymbolHistoryEvent]] = defaultdict(list)

        self._convert_stock_orders_to_symbol_history_events(
            stock_orders=stock_orders,
            events_by_symbol=events_by_symbol,
        )

        self._convert_option_orders_to_symbol_history_events(
            option_orders=option_orders,
            events_by_symbol=events_by_symbol,
        )

        self._convert_option_events_to_symbol_history_events(
            option_events=option_events,
            events_by_symbol=events_by_symbol,
        )

        for symbol, symbol_events in events_by_symbol.items():
            events_by_symbol[symbol] = sorted(symbol_events, key=lambda e: e.event_ts)

        for symbol, symbol_events in events_by_symbol.items():
            context = SymbolHistoryContext(symbol=symbol)
            for event in symbol_events:
                if event.event_name in ('SHORT PUT', 'SHORT CALL'):
                    assert event.unit_price is not None
                    assert event.option_order.num_of_legs == 1
                    leg = event.option_order.legs[0]
                    context.sell_to_open(
                        symbol=event.symbol,
                        quantity=int(event.quantity) * leg.ratio_quantity,
                        unit_price=abs(event.unit_price),
                        option_instrument=leg.option_instrument,
                    )
                elif event.event_name in ('LONG PUT', 'LONG CALL'):
                    assert event.unit_price is not None
                    assert len(event.option_order.opening_legs) == 1
                    context.buy_to_open(
                        symbol=event.symbol,
                        quantity=int(event.quantity),
                        unit_price=event.unit_price,
                        option_instrument=event.option_order.legs[0].option_instrument,
                    )
                elif event.event_name in {'ROLLING CALL', 'ROLLING PUT'}:
                    assert event.unit_price is not None
                    closing_option_instrument = event.option_rolling_order.closing_leg.option_instrument
                    unit_price = context.option_sell_holding[closing_option_instrument.symbol].avg_unit_price
                    context.buy_to_close(
                        symbol=closing_option_instrument.symbol,
                        quantity=int(event.quantity),
                        unit_price=unit_price,
                    )

                    leg = event.option_rolling_order.opening_leg
                    context.sell_to_open(
                        symbol=leg.option_instrument.symbol,
                        quantity=int(event.quantity) * leg.ratio_quantity,
                        unit_price=unit_price - event.unit_price,
                        option_instrument=leg.option_instrument,
                    )
                elif event.event_name == 'SHORT CALL SPREAD':
                    for leg in event.option_order.legs:
                        if leg.side == 'buy':
                            context.buy_to_open(
                                symbol=leg.option_instrument.symbol,
                                quantity=int(leg.quantity),
                                unit_price=leg.unit_price,
                                option_instrument=leg.option_instrument,
                            )
                        else:
                            context.sell_to_open(
                                symbol=leg.option_instrument.symbol,
                                quantity=int(leg.quantity),
                                unit_price=leg.unit_price,
                                option_instrument=leg.option_instrument,
                            )
                elif event.event_name == 'OPTION EXPIRATION':
                    context.option_expire(
                        symbol=event.symbol,
                        quantity=int(event.quantity),
                    )
                elif event.event_name == 'BUY TO CLOSE':
                    assert event.unit_price is not None
                    context.buy_to_close(
                        symbol=event.symbol,
                        quantity=int(event.quantity),
                        unit_price=event.unit_price,
                    )
                elif event.event_name == 'SELL TO CLOSE':
                    assert event.unit_price is not None
                    context.sell_to_close(
                        symbol=event.symbol,
                        quantity=int(event.quantity),
                        unit_price=event.unit_price,
                    )
                elif event.event_name == 'CALL ASSIGNMENT':
                    assert event.unit_price is not None
                    context.call_assignment(
                        symbol=event.symbol,
                        quantity=int(event.quantity),
                        price=event.unit_price,
                    )
                elif event.event_name == 'PUT ASSIGNMENT':
                    instrument = event.option_event.option_instrument
                    assert event.unit_price is not None
                    context.put_asignment(
                        symbol=event.symbol,
                        quantity=int(event.quantity),
                        price=event.unit_price,
                        strike_price=instrument.strike_price,
                    )
                elif event.event_name == 'OPTION EXERCISE':
                    option_instrument = event.option_event.option_instrument
                    option_avg_price = context.option_buy_holding[event.symbol].avg_unit_price
                    event.unit_price = option_instrument.strike_price + option_avg_price
                    context.call_exercise(
                        symbol=event.symbol,
                        quantity=int(event.quantity),
                        price=option_avg_price,
                        strike_price=option_instrument.strike_price,
                    )
                elif event.event_name in ('LIMIT BUY', 'MARKET BUY'):
                    assert event.unit_price is not None
                    context.limit_or_market_buy_stock(
                        quantity=int(event.quantity),
                        price=event.unit_price,
                    )
                elif event.event_name in ('LIMIT SELL', 'MARKET SELL'):
                    assert event.unit_price is not None
                    context.limit_or_market_sell_stock(
                        quantity=int(event.quantity),
                        price=event.unit_price,
                    )
                elif event.event_name in {
                    'FIG LEAF',
                    'LONG CALL SPREAD',
                    'LONG PUT SPREAD',
                    'SHORT PUT SPREAD',
                    'CUSTOM',
                    'IRON CONDOR',
                    'FIG LEAF CLOSE',
                    'LONG CALL SPREAD CLOSE',
                    'LONG CALL CLOSE',
                    'LONG PUT CLOSE',
                    'LONG PUT SPREAD CLOSE',
                    'SHORT PUT SPREAD CLOSE',
                    'CUSTOM CLOSE',
                    'IRON CONDOR CLOSE',
                    'SHORT CALL SPREAD CLOSE',
                }:
                    for leg in event.option_order.legs:
                        quantity = int(event.option_order.processed_quantity) * leg.ratio_quantity
                        if leg.is_buy and leg.is_open:
                            context.buy_to_open(
                                symbol=leg.option_instrument.symbol,
                                quantity=quantity,
                                unit_price=leg.unit_price,
                                option_instrument=leg.option_instrument,
                            )
                        elif leg.is_buy and leg.is_close:
                            context.buy_to_close(
                                symbol=leg.option_instrument.symbol,
                                quantity=quantity,
                                unit_price=leg.unit_price,
                            )
                        elif leg.is_sell and leg.is_open:
                            context.sell_to_open(
                                symbol=leg.option_instrument.symbol,
                                quantity=quantity,
                                unit_price=leg.unit_price,
                                option_instrument=leg.option_instrument,
                            )
                        elif leg.is_sell and leg.is_close:
                            context.sell_to_close(
                                symbol=leg.option_instrument.symbol,
                                quantity=quantity,
                                unit_price=leg.unit_price,
                            )
                elif event.event_name in {
                    'ROLLING SHORT CALL SPREAD',
                    'ROLLING SHORT PUT SPREAD',
                }:
                    assert event.option_order.num_of_legs == 4

                    stc_leg: Optional[OptionLeg] = None
                    btc_leg: Optional[OptionLeg] = None
                    sto_leg: Optional[OptionLeg] = None
                    bto_leg: Optional[OptionLeg] = None

                    for leg in event.option_order.legs:
                        if leg.is_sell_to_close:
                            stc_leg = leg
                        elif leg.is_buy_to_close:
                            btc_leg = leg
                        elif leg.is_sell_to_open:
                            sto_leg = leg
                        else:
                            assert leg.is_buy_to_open
                            bto_leg = leg

                    assert stc_leg is not None
                    assert btc_leg is not None
                    assert sto_leg is not None
                    assert bto_leg is not None

                    stc_symbol = stc_leg.option_instrument.symbol
                    original_bto_unit_price = context.option_buy_holding[stc_symbol].avg_unit_price
                    original_bto_profit = stc_leg.unit_price - original_bto_unit_price
                    bto_price = bto_leg.unit_price - original_bto_profit

                    context.sell_to_close(
                        symbol=stc_symbol,
                        quantity=int(event.quantity) * stc_leg.ratio_quantity,
                        unit_price=original_bto_unit_price,
                    )
                    context.buy_to_open(
                        symbol=bto_leg.option_instrument.symbol,
                        quantity=int(event.quantity) * bto_leg.ratio_quantity,
                        unit_price=bto_price,
                        option_instrument=bto_leg.option_instrument,
                    )

                    btc_symbol = btc_leg.option_instrument.symbol
                    original_sto_unit_price = context.option_sell_holding[btc_symbol].avg_unit_price
                    original_sto_profit = original_sto_unit_price - btc_leg.unit_price
                    sto_price = sto_leg.unit_price + original_sto_profit

                    context.buy_to_close(
                        symbol=btc_symbol,
                        quantity=int(event.quantity) * btc_leg.ratio_quantity,
                        unit_price=original_sto_unit_price,
                    )
                    context.sell_to_open(
                        symbol=sto_leg.option_instrument.symbol,
                        quantity=int(event.quantity) * sto_leg.ratio_quantity,
                        unit_price=sto_price,
                        option_instrument=sto_leg.option_instrument,
                    )
                else:
                    raise NotImplementedError(event.event_name)

                snapshot = context.take_snapshot()
                event.add_context(symbol_history_context_snapshot=snapshot)

        return events_by_symbol

    def _convert_stock_orders_to_symbol_history_events(
        self,
        stock_orders: List[StockOrder],
        events_by_symbol: DefaultDict[str, List[SymbolHistoryEvent]],
    ) -> None:
        for stock_order in stock_orders:
            if stock_order.instrument_id not in ALL_REVERSED:
                data = rhc.get_url(stock_order.instrument_url)
                for k, v in data.items():
                    print(f'{k}: {v}')

            symbol = ALL_REVERSED[stock_order.instrument_id]
            symbol_history_event = symbol_history_event_from_stock_order(
                symbol=symbol,
                stock_order=stock_order,
            )
            if symbol_history_event is not None:
                events_by_symbol[symbol].append(symbol_history_event)

    def _convert_option_orders_to_symbol_history_events(
        self,
        option_orders: List[OptionOrder],
        events_by_symbol: DefaultDict[str, List[SymbolHistoryEvent]],
    ) -> None:
        for option_order in option_orders:
            symbol = option_order.chain_symbol
            symbol_history_event = symbol_history_event_from_option_order(
                symbol=symbol,
                option_order=option_order,
            )
            if symbol_history_event is not None:
                events_by_symbol[symbol].append(symbol_history_event)

    def _convert_option_events_to_symbol_history_events(
        self,
        option_events: List[OptionEvent],
        events_by_symbol: DefaultDict[str, List[SymbolHistoryEvent]],
    ) -> None:
        for option_event in option_events:
            symbol = option_event.option_instrument.chain_symbol
            symbol_history_event = symbol_history_event_from_option_event(option_event=option_event)
            if symbol_history_event is not None:
                events_by_symbol[symbol].append(symbol_history_event)
