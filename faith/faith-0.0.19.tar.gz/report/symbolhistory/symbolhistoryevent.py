from datetime import datetime
from typing import Optional

from report.symbolhistory.symbolhistorycontextsnapshot import SymbolHistoryContextSnapshot
from robinhood.lib.account.optionevent.optionevent import OptionEvent
from robinhood.lib.account.optionorder.optionorder import OptionOrder
from robinhood.lib.account.optionorder.optionrollingorder import OptionRollingOrder
from robinhood.lib.account.stockorder.stockorder import StockOrder


class SymbolHistoryEvent(object):

    def __init__(
        self,
        event_ts: datetime,
        event_name: str,
        symbol: str,
        quantity: float,
        unit_price: Optional[float],
        stock_order: Optional[StockOrder] = None,
        option_order: Optional[OptionOrder] = None,
        option_rolling_order: Optional[OptionRollingOrder] = None,
        option_event: Optional[OptionEvent] = None,
    ):
        self._event_ts = event_ts
        self._event_name = event_name
        self._symbol = symbol
        self._quantity = quantity
        self._unit_price = unit_price
        self._stock_order = stock_order
        self._option_order = option_order
        self._option_rolling_order = option_rolling_order
        self._option_event = option_event

        self._context: Optional[SymbolHistoryContextSnapshot] = None

    @property
    def event_name(self) -> str:
        return self._event_name

    @property
    def event_ts(self) -> datetime:
        return self._event_ts

    @property
    def symbol(self) -> str:
        return self._symbol

    @property
    def quantity(self) -> float:
        return self._quantity

    @property
    def unit_price(self) -> Optional[float]:
        return self._unit_price

    @unit_price.setter
    def unit_price(self, unit_price: float) -> None:
        """
        Why do we need to set unit price?
        """
        self._unit_price = unit_price

    @property
    def stock_order(self) -> StockOrder:
        assert self._stock_order is not None
        return self._stock_order

    @property
    def option_order(self) -> OptionOrder:
        assert self._option_order is not None
        return self._option_order

    @property
    def option_event(self) -> OptionEvent:
        assert self._option_event is not None
        return self._option_event

    @property
    def option_rolling_order(self) -> OptionRollingOrder:
        assert self._option_rolling_order is not None
        return self._option_rolling_order

    @property
    def context(self) -> SymbolHistoryContextSnapshot:
        assert self._context is not None
        return self._context

    @property
    def formatted_ts(self) -> str:
        return self.event_ts.strftime('%m/%d/%Y %H:%M')

    def add_context(
        self,
        symbol_history_context_snapshot: SymbolHistoryContextSnapshot,
    ) -> None:
        self._context = symbol_history_context_snapshot


def symbol_history_event_from_stock_order(symbol: str, stock_order: StockOrder) -> Optional[SymbolHistoryEvent]:
    if stock_order.state != 'filled':
        return None

    assert stock_order.average_price is not None

    return SymbolHistoryEvent(
        event_ts=stock_order.updated_at,
        event_name=stock_order.symbol_event_name,
        symbol=symbol,
        quantity=stock_order.quantity,
        unit_price=stock_order.average_price,
        stock_order=stock_order,
    )


def symbol_history_event_from_option_order(
    symbol: str,
    option_order: OptionOrder,
) -> Optional[SymbolHistoryEvent]:
    if not (
        option_order.state == 'filled'
        or (option_order.state == 'cancelled' and option_order.processed_quantity > 0)
    ):
        return None

    option_rolling_order = option_order.rolling_order
    if option_rolling_order is not None:
        call_or_put = option_rolling_order.call_or_put.upper()
        event_name = f'ROLLING {call_or_put}'
        symbol = option_rolling_order.symbol
        quantity = option_order.processed_quantity
        return SymbolHistoryEvent(
            event_ts=option_order.updated_at,
            event_name=event_name,
            symbol=symbol,
            quantity=quantity,
            unit_price=option_order.price,
            option_rolling_order=option_rolling_order,
        )

    if option_order.is_rolling_short_spread:
        call_or_put = option_order.legs[0].option_instrument.instrument_type.upper()
        event_name = f'ROLLING SHORT {call_or_put} SPREAD'
        return SymbolHistoryEvent(
            event_ts=option_order.updated_at,
            event_name=event_name,
            symbol=option_order.concatenated_symbol,
            quantity=option_order.processed_quantity,
            unit_price=option_order.price,
            option_order=option_order,
        )

    if option_order.is_buy_to_close:
        event_name = 'BUY TO CLOSE'
        symbol = option_order.legs[0].option_instrument.symbol
        quantity = option_order.processed_quantity
        return SymbolHistoryEvent(
            event_ts=option_order.updated_at,
            event_name=event_name,
            symbol=symbol,
            quantity=quantity,
            unit_price=option_order.price,
            option_order=option_order,
        )

    if option_order.opening_strategy in {
        'short_call',
        'short_put',
        'long_call',
        'long_put',
    }:
        assert option_order.opening_strategy_name is not None
        assert len(option_order.opening_legs) == 1
        assert option_order.num_of_legs == 1
        event_name = option_order.opening_strategy_name
        symbol = option_order.opening_legs[0].option_instrument.symbol
        quantity = option_order.processed_quantity
        return SymbolHistoryEvent(
            event_ts=option_order.updated_at,
            event_name=event_name,
            symbol=symbol,
            quantity=quantity,
            unit_price=option_order.price,
            option_order=option_order,
        )

    if option_order.opening_strategy in {
        'long_call_spread',
        'long_put_spread',
        'short_call_spread',
        'short_put_spread',
    }:
        assert option_order.opening_strategy_name is not None
        assert option_order.num_of_legs == 2
        return SymbolHistoryEvent(
            event_ts=option_order.updated_at,
            event_name=option_order.opening_strategy_name,
            symbol=option_order.spread_symbol,
            quantity=option_order.processed_quantity,
            unit_price=option_order.price,
            option_order=option_order,
        )

    if option_order.closing_strategy in {
        'short_call_spread',
    }:
        assert option_order.closing_strategy is not None
        assert option_order.num_of_legs == 2
        return SymbolHistoryEvent(
            event_ts=option_order.updated_at,
            event_name=f'{option_order.closing_strategy_name} CLOSE',
            symbol=option_order.spread_symbol,
            quantity=option_order.processed_quantity,
            unit_price=option_order.price,
            option_order=option_order,
        )

    if option_order.is_fig_leaf_open:
        return SymbolHistoryEvent(
            event_ts=option_order.updated_at,
            event_name='FIG LEAF',
            symbol=option_order.fig_leaf_symbol,
            quantity=option_order.processed_quantity,
            unit_price=option_order.price,
            option_order=option_order,
        )

    if option_order.is_fig_leaf_close:
        return SymbolHistoryEvent(
            event_ts=option_order.updated_at,
            event_name='FIG LEAF CLOSE',
            symbol=option_order.fig_leaf_symbol,
            quantity=option_order.processed_quantity,
            unit_price=option_order.price,
            option_order=option_order,
        )

    if option_order.closing_strategy in {
        'long_call_spread',
        'long_put_spread',
        'short_put_spread',
    }:
        if option_order.price is None:
            unit_price = 0.0
            for leg in option_order.legs:
                multiplier = -1 if leg.side == 'buy' else 1
                for ex in leg.executions:
                    unit_price += multiplier * ex.price
        else:
            unit_price = option_order.price

        return SymbolHistoryEvent(
            event_ts=option_order.updated_at,
            event_name=f'{option_order.closing_strategy_name} CLOSE',
            symbol=option_order.spread_symbol,
            quantity=option_order.processed_quantity,
            unit_price=unit_price,
            option_order=option_order,
        )

    if option_order.closing_strategy in {
        'long_call',
        'long_put',
    }:
        return SymbolHistoryEvent(
            event_ts=option_order.updated_at,
            event_name=f'{option_order.closing_strategy_name} CLOSE',
            symbol=option_order.legs[0].option_instrument.symbol,
            quantity=option_order.processed_quantity,
            unit_price=option_order.price,
            option_order=option_order,
        )

    if option_order.opening_strategy in {
        'custom',
        'iron_condor',
    }:
        assert option_order.opening_strategy_name is not None

        event_name = option_order.opening_strategy_name
        symbol = option_order.concatenated_symbol
        quantity = option_order.processed_quantity
        return SymbolHistoryEvent(
            event_ts=option_order.updated_at,
            event_name=event_name,
            symbol=symbol,
            quantity=quantity,
            unit_price=option_order.price,
            option_order=option_order,
        )

    if option_order.closing_strategy in {
        'custom',
        'iron_condor',
    }:
        return SymbolHistoryEvent(
            event_ts=option_order.updated_at,
            event_name=f'{option_order.closing_strategy_name} CLOSE',
            symbol=option_order.concatenated_symbol,
            quantity=option_order.processed_quantity,
            unit_price=option_order.price,
            option_order=option_order,
        )

    print(
        f'{option_order.order_id}: {option_order.chain_symbol} '
        f'Open: {option_order.opening_strategy}: '
        f'{option_order.num_of_legs} {option_order.legs[0].side} {option_order.legs[0].position_effect}',
    )
    print(
        f'{option_order.order_id}: {option_order.chain_symbol} '
        f'Close: {option_order.closing_strategy}: '
        f'{option_order.direction}',
    )
    raise Exception('Unrecognized Option Order')


def symbol_history_event_from_option_event(option_event: OptionEvent) -> Optional[SymbolHistoryEvent]:
    if option_event.state not in {'confirmed', 'pending'}:
        return None

    if option_event.event_type == 'expiration':
        return SymbolHistoryEvent(
            event_ts=option_event.created_at,
            event_name=f'option {option_event.event_type}'.upper(),
            symbol=option_event.option_instrument.symbol,
            quantity=option_event.quantity,
            unit_price=0.0,
            option_event=option_event,
        )

    if option_event.event_type == 'assignment':
        if option_event.direction == 'credit':
            option_type = 'call'
        else:
            option_type = 'put'

        return SymbolHistoryEvent(
            event_ts=option_event.created_at,
            event_name=f'{option_type} {option_event.event_type}'.upper(),
            symbol=option_event.option_instrument.symbol,
            quantity=option_event.quantity,
            unit_price=option_event.option_instrument.strike_price,
            option_event=option_event,
        )

    return SymbolHistoryEvent(
        event_ts=option_event.created_at,
        event_name=f'option {option_event.event_type}'.upper(),
        symbol=option_event.option_instrument.symbol,
        quantity=option_event.quantity,
        unit_price=option_event.option_instrument.strike_price,
        option_event=option_event,
    )
