from datetime import datetime
from typing import Any

from robinhood.lib.helpers import parse_datetime_with_microsecond


class MarginBalance(object):

    def __init__(
        self,
        start_of_day_dtbp: float,
        outstanding_interest: float,
        gold_equity_requirement: float,
        created_at: datetime,
        updated_at: datetime,
        cash: float,
        cash_held_for_options_collateral: float,
        cash_held_for_orders: float,
        cash_held_for_dividends: float,
        cash_held_for_nummus_restrictions: float,
        cash_held_for_restrictions: float,
        cash_pending_from_options_events: float,
        cash_available_for_withdrawal: float,
        unallocated_margin_cash: float,
        pending_deposit: float,
        uncleared_deposits: float,
        uncleared_nummus_deposits: float,
        day_trade_ratio: float,
        day_trades_protection: bool,
        day_trade_buying_power: float,
        day_trade_buying_power_held_for_orders: float,
        overnight_ratio: float,
        overnight_buying_power: float,
        overnight_buying_power_held_for_orders: float,
        start_of_day_overnight_buying_power: float,
        sma: int,
        settled_amount_borrowed: float,
        unsettled_debit: float,
        unsettled_funds: float,
        crypto_buying_power: float,
    ) -> None:
        self._start_of_day_dtbp = start_of_day_dtbp
        self._outstanding_interest = outstanding_interest
        self._gold_equity_requirement = gold_equity_requirement
        self._created_at = created_at
        self._updated_at = updated_at
        self._cash = cash
        self._cash_held_for_options_collateral = cash_held_for_options_collateral
        self._cash_held_for_orders = cash_held_for_orders
        self._cash_held_for_dividends = cash_held_for_dividends
        self._cash_held_for_nummus_restrictions = cash_held_for_nummus_restrictions
        self._cash_held_for_restrictions = cash_held_for_restrictions
        self._cash_pending_from_options_events = cash_pending_from_options_events
        self._cash_available_for_withdrawal = cash_available_for_withdrawal
        self._unallocated_margin_cash = unallocated_margin_cash
        self._pending_deposit = pending_deposit
        self._uncleared_deposits = uncleared_deposits
        self._uncleared_nummus_deposits = uncleared_nummus_deposits
        self._day_trade_ratio = day_trade_ratio
        self._day_trades_protection = day_trades_protection
        self._day_trade_buying_power = day_trade_buying_power
        self._day_trade_buying_power_held_for_orders = day_trade_buying_power_held_for_orders
        self._overnight_ratio = overnight_ratio
        self._overnight_buying_power = overnight_buying_power
        self._overnight_buying_power_held_for_orders = overnight_buying_power_held_for_orders
        self._start_of_day_overnight_buying_power = start_of_day_overnight_buying_power
        self._sma = sma
        self._settled_amount_borrowed = settled_amount_borrowed
        self._unsettled_debit = unsettled_debit
        self._unsettled_funds = unsettled_funds
        self._crypto_buying_power = crypto_buying_power

    @property
    def overnight_buying_power(self) -> float:
        return self._overnight_buying_power


def margin_balance_from_data(data: Any) -> MarginBalance:
    return MarginBalance(
        start_of_day_dtbp=float(data['start_of_day_dtbp']),
        outstanding_interest=float(data['outstanding_interest']),
        gold_equity_requirement=float(data['gold_equity_requirement']),
        created_at=parse_datetime_with_microsecond(data['created_at']),
        updated_at=parse_datetime_with_microsecond(data['updated_at']),
        cash=float(data['cash']),
        cash_held_for_options_collateral=float(data['cash_held_for_options_collateral']),
        cash_held_for_orders=float(data['cash_held_for_orders']),
        cash_held_for_dividends=float(data['cash_held_for_dividends']),
        cash_held_for_nummus_restrictions=float(data['cash_held_for_nummus_restrictions']),
        cash_held_for_restrictions=float(data['cash_held_for_restrictions']),
        cash_pending_from_options_events=float(data['cash_pending_from_options_events']),
        cash_available_for_withdrawal=float(data['cash_available_for_withdrawal']),
        unallocated_margin_cash=float(data['unallocated_margin_cash']),
        pending_deposit=float(data['pending_deposit']),
        uncleared_deposits=float(data['uncleared_deposits']),
        uncleared_nummus_deposits=float(data['uncleared_nummus_deposits']),
        day_trade_ratio=float(data['day_trade_ratio']),
        day_trades_protection=data['day_trades_protection'],
        day_trade_buying_power=float(data['day_trade_buying_power']),
        day_trade_buying_power_held_for_orders=float(data['day_trade_buying_power_held_for_orders']),
        overnight_ratio=float(data['overnight_ratio']),
        overnight_buying_power=float(data['overnight_buying_power']),
        overnight_buying_power_held_for_orders=float(data['overnight_buying_power_held_for_orders']),
        start_of_day_overnight_buying_power=float(data['start_of_day_overnight_buying_power']),
        sma=int(data['sma']),
        settled_amount_borrowed=float(data['settled_amount_borrowed']),
        unsettled_debit=float(data['unsettled_debit']),
        unsettled_funds=float(data['unsettled_funds']),
        crypto_buying_power=float(data['crypto_buying_power']),
    )
