from typing import Optional
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from robinhood.lib.account.optionorder.optionleg import OptionLeg
    from robinhood.lib.account.optionorder.optionorder import OptionOrder


class OptionRollingOrder(object):

    def __init__(
        self,
        option_order: 'OptionOrder',
        closing_leg: 'OptionLeg',
        opening_leg: 'OptionLeg',
    ) -> None:
        self._option_order = option_order
        self._closing_leg = closing_leg
        self._opening_leg = opening_leg

    @property
    def symbol(self) -> str:
        _ri = self._opening_leg.option_instrument
        return self._option_order.get_two_leg_symbol(
            left_symbol=self._closing_leg.option_instrument.symbol,
            right_exp_date=_ri.formatted_exp_date,
            right_instrument_type=_ri.instrument_type_short,
            right_strike_price=_ri.strike_price,
        )

    @property
    def call_or_put(self) -> str:
        return self._closing_leg.option_instrument.instrument_type_full

    @property
    def closing_leg(self) -> 'OptionLeg':
        return self._closing_leg

    @property
    def opening_leg(self) -> 'OptionLeg':
        return self._opening_leg


def derive_option_rolling_order(option_order: 'OptionOrder') -> Optional[OptionRollingOrder]:
    # Rolling must involve two legs.
    if option_order.num_of_legs != 2:
        return None

    num_of_buy_to_close = 0
    num_of_sell_to_open = 0
    for leg in option_order.legs:
        if leg.is_buy and leg.is_close:
            num_of_buy_to_close += 1
            continue

        if leg.is_sell and leg.is_open:
            num_of_sell_to_open += 1
            continue

    if num_of_buy_to_close != 1 or num_of_sell_to_open != 1:
        return None

    closing_leg: 'Optional[OptionLeg]' = None
    opening_leg: 'Optional[OptionLeg]' = None
    for i in range(len(option_order.legs)):
        leg = option_order.legs[i]
        if leg.is_open:
            opening_leg = leg
        else:
            closing_leg = leg

    assert closing_leg is not None
    assert opening_leg is not None
    return OptionRollingOrder(
        option_order=option_order,
        closing_leg=closing_leg,
        opening_leg=opening_leg,
    )
