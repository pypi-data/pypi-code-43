from typing import Any
from typing import Dict
from typing import List

from robinhood.lib.account.optionorder.optionlegexecution import option_leg_execution_from_data
from robinhood.lib.account.optionorder.optionlegexecution import OptionLegExecution
from robinhood.lib.marketplace.optioninstrument import option_instrument_from_url
from robinhood.lib.marketplace.optioninstrument import OptionInstrument


class OptionLeg(object):

    def __init__(
        self,
        leg_id: str,
        option_instrument_url: str,
        side: str,
        position_effect: str,
        ratio_quantity: int,
        executions: List[OptionLegExecution],
    ) -> None:
        self._leg_id = leg_id
        self._option_instrument_url = option_instrument_url
        self._side = side
        self._position_effect = position_effect
        self._ratio_quantity = ratio_quantity
        self._executions = executions

    @property
    def option_instrument(self) -> OptionInstrument:
        return option_instrument_from_url(url=self._option_instrument_url)

    @property
    def is_call(self) -> bool:
        return self.option_instrument.is_call

    @property
    def is_put(self) -> bool:
        return self.option_instrument.is_put

    @property
    def quantity(self) -> float:
        total_quantity = 0.0
        for ex in self._executions:
            total_quantity += ex.quantity
        return total_quantity

    @property
    def ratio_quantity(self) -> int:
        return self._ratio_quantity

    @property
    def unit_price(self) -> float:
        total_price = 0.0
        for ex in self._executions:
            total_price += ex.quantity * ex.price
        return total_price / self.quantity

    @property
    def position_effect(self) -> str:
        return self._position_effect

    @property
    def is_open(self) -> bool:
        return self.position_effect == 'open'

    @property
    def is_close(self) -> bool:
        return self.position_effect == 'close'

    @property
    def side(self) -> str:
        return self._side

    @property
    def is_buy(self) -> bool:
        return self.side == 'buy'

    @property
    def is_sell(self) -> bool:
        return self.side == 'sell'

    @property
    def is_sell_to_open(self) -> bool:
        return self.is_sell and self.is_open

    @property
    def is_sell_to_close(self) -> bool:
        return self.is_sell and self.is_close

    @property
    def is_buy_to_open(self) -> bool:
        return self.is_buy and self.is_open

    @property
    def is_buy_to_close(self) -> bool:
        return self.is_buy and self.is_close

    @property
    def executions(self) -> List[OptionLegExecution]:
        return self._executions


def option_leg_from_data(data: Dict[str, Any]) -> OptionLeg:
    executions = [
        option_leg_execution_from_data(data=row)
        for row in data['executions']
    ]
    return OptionLeg(
        leg_id=data['id'],
        option_instrument_url=data['option'],
        side=data['side'],
        position_effect=data['position_effect'],
        ratio_quantity=int(data['ratio_quantity']),
        executions=executions,
    )
