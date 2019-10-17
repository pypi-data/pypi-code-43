from datetime import datetime
from typing import Any
from typing import List

from robinhood.lib.account.marginbalance import margin_balance_from_data
from robinhood.lib.account.marginbalance import MarginBalance
from robinhood.lib.account.optionevent.optionevent import option_event_from_data
from robinhood.lib.account.optionevent.optionevent import OptionEvent
from robinhood.lib.account.optionorder.optionorder import option_order_from_data
from robinhood.lib.account.optionorder.optionorder import OptionOrder
from robinhood.lib.account.optionposition.optionposition import option_position_from_data
from robinhood.lib.account.optionposition.optionposition import OptionPosition
from robinhood.lib.account.stockorder.stockorder import stock_order_from_data
from robinhood.lib.account.stockorder.stockorder import StockOrder
from robinhood.lib.account.stockposition.stockposition import stock_position_from_data
from robinhood.lib.account.stockposition.stockposition import StockPosition
from robinhood.lib.helpers import parse_datetime_with_microsecond
from robinhood.lib.robinhoodclient import rhc


class AccountObj(object):

    def __init__(
        self,
        buying_power: float,
        crypto_buying_power: float,
        margin_balance: MarginBalance,
        cash: float,
        cash_held_for_orders: float,
        cash_available_for_withdrawal: float,
        portfolio_url: str,
        positions_url: str,
        url: str,
        user_url: str,
        state: str,
        account_type: str,
        option_level: int,
        locked: bool,
        deactivated: bool,
        permanently_deactivated: bool,
        rhs_account_number: int,
        account_number: str,
        active_subscription_id: str,
        withdrawal_halted: bool,
        sma: int,
        sweep_enabled: bool,
        deposit_halted: bool,
        max_ach_early_access_amount: float,
        only_position_closing_trades: bool,
        sma_held_for_orders: int,
        unsettled_debit: float,
        is_pinnacle_account: bool,
        uncleared_deposits: float,
        unsettled_funds: float,
        created_at: datetime,
        updated_at: datetime,
    ) -> None:
        self._buying_power = buying_power
        self._crypto_buying_power = crypto_buying_power
        self._margin_balance = margin_balance
        self._cash = cash
        self._cash_held_for_orders = cash_held_for_orders
        self._cash_available_for_withdrawal = cash_available_for_withdrawal
        self._portfolio_url = portfolio_url
        self._positions_url = positions_url
        self._url = url
        self._user_url = user_url
        self._state = state
        self._account_type = account_type
        self._option_level = option_level
        self._locked = locked
        self._deactivated = deactivated
        self._permanently_deactivated = permanently_deactivated
        self._rhs_account_number = rhs_account_number
        self._account_number = account_number
        self._active_subscription_id = active_subscription_id
        self._withdrawal_halted = withdrawal_halted
        self._sma = sma
        self._sweep_enabled = sweep_enabled
        self._deposit_halted = deposit_halted
        self._max_ach_early_access_amount = max_ach_early_access_amount
        self._only_position_closing_trades = only_position_closing_trades
        self._sma_held_for_orders = sma_held_for_orders
        self._unsettled_debit = unsettled_debit
        self._is_pinnacle_account = is_pinnacle_account
        self._uncleared_deposits = uncleared_deposits
        self._unsettled_funds = unsettled_funds
        self._created_at = created_at
        self._updated_at = updated_at

    @property
    def cash(self) -> float:
        return self._cash

    @property
    def account_type(self) -> str:
        return self._account_type

    @property
    def margin_balance(self) -> MarginBalance:
        return self._margin_balance

    def get_stock_orders(self) -> List[StockOrder]:
        return rhc.get_objects(
            url='https://api.robinhood.com/orders/',
            callback=stock_order_from_data,
            result_key='results',
        )

    def get_stock_positions(self) -> List[StockPosition]:
        return rhc.get_objects(
            url='https://api.robinhood.com/positions/?nonzero=true',
            callback=stock_position_from_data,
            result_key='results',
        )

    def get_option_orders(self) -> List[OptionOrder]:
        return rhc.get_objects(
            url='https://api.robinhood.com/options/orders/',
            callback=option_order_from_data,
            result_key='results',
        )

    def get_option_positions(self) -> List[OptionPosition]:
        return rhc.get_objects(
            url='https://api.robinhood.com/options/positions/',
            callback=option_position_from_data,
            result_key='results',
        )

    def get_option_events(self) -> List[OptionEvent]:
        return rhc.get_objects(
            url='https://api.robinhood.com/options/events/',
            callback=option_event_from_data,
            result_key='results',
        )


def account_obj_from_data(data: Any) -> AccountObj:
    return AccountObj(
        buying_power=float(data['buying_power']),
        crypto_buying_power=float(data['crypto_buying_power']),
        margin_balance=margin_balance_from_data(data=data['margin_balances']),
        cash=float(data['cash']),
        cash_held_for_orders=float(data['cash_held_for_orders']),
        cash_available_for_withdrawal=float(data['cash_available_for_withdrawal']),
        portfolio_url=data['portfolio'],
        positions_url=data['positions'],
        url=data['url'],
        user_url=data['user'],
        state=data['state'],
        account_type=data['type'],
        option_level=data['option_level'],
        locked=data['locked'],
        deactivated=data['deactivated'],
        permanently_deactivated=data['permanently_deactivated'],
        rhs_account_number=int(data['rhs_account_number']),
        account_number=data['account_number'],
        active_subscription_id=data['active_subscription_id'],
        withdrawal_halted=data['withdrawal_halted'],
        sma=int(data['sma']),
        sweep_enabled=data['sweep_enabled'],
        deposit_halted=data['deposit_halted'],
        max_ach_early_access_amount=float(data['max_ach_early_access_amount']),
        only_position_closing_trades=data['only_position_closing_trades'],
        sma_held_for_orders=int(data['sma_held_for_orders']),
        unsettled_debit=float(data['unsettled_debit']),
        is_pinnacle_account=data['is_pinnacle_account'],
        uncleared_deposits=float(data['uncleared_deposits']),
        unsettled_funds=float(data['unsettled_funds']),
        created_at=parse_datetime_with_microsecond(data['created_at']),
        updated_at=parse_datetime_with_microsecond(data['updated_at']),
    )
