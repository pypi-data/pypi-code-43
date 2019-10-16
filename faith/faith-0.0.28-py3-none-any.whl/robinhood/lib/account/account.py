from concurrent.futures import as_completed
from concurrent.futures import Future
from concurrent.futures import ThreadPoolExecutor
from typing import Any
from typing import List
from typing import Optional
from typing import Set

from robinhood.lib.account.accountobj import account_obj_from_data
from robinhood.lib.account.accountobj import AccountObj
from robinhood.lib.account.optionevent.optionevent import OptionEvent
from robinhood.lib.account.optionorder.optionorder import OptionOrder
from robinhood.lib.account.optionposition.optionposition import OptionPosition
from robinhood.lib.account.stockorder.stockorder import StockOrder
from robinhood.lib.account.stockposition.stockposition import StockPosition
from robinhood.lib.robinhoodclient import rhc


class Account(object):

    ENDPOINT = 'https://api.robinhood.com/accounts/'

    def __init__(self) -> None:
        self._account_obj: Optional[AccountObj] = None
        self._stock_orders: Optional[List[StockOrder]] = None
        self._stock_positions: Optional[List[StockPosition]] = None
        self._option_orders: Optional[List[OptionOrder]] = None
        self._option_positions: Optional[List[OptionPosition]] = None
        self._option_events: Optional[List[OptionEvent]] = None

    @property
    def account_obj(self) -> AccountObj:
        if self._account_obj is None:
            self._account_obj = self._get_account_obj()

        return self._account_obj

    @property
    def margin_used(self) -> float:
        if self.account_obj.cash >= 0:
            margin_used = 0.0
        else:
            margin_used = -self.account_obj.cash

        return margin_used

    @property
    def buying_power(self) -> float:
        return self.account_obj.margin_balance.overnight_buying_power * 2

    @property
    def account_type(self) -> str:
        return self.account_obj.account_type

    @property
    def stock_orders(self) -> List[StockOrder]:
        if self._stock_orders is None:
            self._stock_orders = self.get_stock_orders()

        return self._stock_orders

    @property
    def stock_positions(self) -> List[StockPosition]:
        if self._stock_positions is None:
            self._stock_positions = self.get_stock_positions()

        return self._stock_positions

    @property
    def option_orders(self) -> List[OptionOrder]:
        if self._option_orders is None:
            self._option_orders = self.get_option_orders()

        return self._option_orders

    @property
    def option_positions(self) -> List[OptionPosition]:
        if self._option_positions is None:
            self._option_positions = self.get_option_positions()

        return self._option_positions

    @property
    def option_events(self) -> List[OptionEvent]:
        if self._option_events is None:
            self._option_events = self.get_option_events()

        return self._option_events

    @property
    def active_symbols(self) -> Set[str]:
        return self._get_active_symbols()

    def get_stock_orders(self) -> List[StockOrder]:
        return self.account_obj.get_stock_orders()

    def get_stock_positions(self) -> List[StockPosition]:
        return self.account_obj.get_stock_positions()

    def get_option_orders(self) -> List[OptionOrder]:
        return self.account_obj.get_option_orders()

    def get_option_positions(self) -> List[OptionPosition]:
        return self.account_obj.get_option_positions()

    def get_option_events(self) -> List[OptionEvent]:
        return self.account_obj.get_option_events()

    def update_in_parallel(
        self,
        update_stock_orders: bool = True,
        update_stock_positions: bool = True,
        update_option_orders: bool = True,
        update_option_positions: bool = True,
        update_option_events: bool = True,
    ) -> None:
        if self._account_obj is None:
            self._account_obj = self._get_account_obj()

        with ThreadPoolExecutor() as executor:
            futures: List[Future[List[Any]]] = []

            if update_stock_orders:
                futures.append(executor.submit(self.get_stock_orders))

            if update_stock_positions:
                futures.append(executor.submit(self.get_stock_positions))

            if update_option_orders:
                futures.append(executor.submit(self.get_option_orders))

            if update_option_positions:
                futures.append(executor.submit(self.get_option_positions))

            if update_option_events:
                futures.append(executor.submit(self.get_option_events))

        for future in as_completed(futures):
            results = future.result()
            if len(results) == 0:
                continue

            if isinstance(results[0], StockOrder):
                self._stock_orders = results
            elif isinstance(results[0], StockPosition):
                self._stock_positions = results
            elif isinstance(results[0], OptionOrder):
                self._option_orders = results
            elif isinstance(results[0], OptionPosition):
                self._option_positions = results
            elif isinstance(results[0], OptionEvent):
                self._option_events = results

    def _get_account_obj(self) -> AccountObj:
        account_obj: AccountObj = rhc.get_object(
            url=self.ENDPOINT,
            callback=account_obj_from_data,
            result_key='results',
        )
        return account_obj

    def _get_active_symbols(self) -> Set[str]:
        active_symbols: Set[str] = set()

        for stock_position in self.stock_positions:
            active_symbols.add(stock_position.symbol)

        for option_position in self.option_positions:
            if option_position.active_quantity > 0:
                active_symbols.add(option_position.chain_symbol)

        return active_symbols


account = Account()
