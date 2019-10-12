from datetime import datetime
from typing import Any
from typing import Dict
from typing import List
from typing import Optional

from robinhood.lib.account.optionorder.optionleg import option_leg_from_data
from robinhood.lib.account.optionorder.optionleg import OptionLeg
from robinhood.lib.account.optionorder.optionrollingorder import derive_option_rolling_order
from robinhood.lib.account.optionorder.optionrollingorder import OptionRollingOrder
from robinhood.lib.helpers import parse_datetime_with_microsecond
from robinhood.lib.helpers import parse_optional_float


class OptionOrder(object):

    def __init__(
        self,
        order_id: str,
        order_type: str,
        ref_id: str,
        state: str,
        trigger: str,
        chain_symbol: str,
        chain_id: str,
        opening_strategy: Optional[str],
        closing_strategy: Optional[str],
        direction: str,
        response_category: str,
        time_in_force: str,
        premium: Optional[float],
        processed_premium: float,
        price: Optional[float],
        stop_price: Optional[float],
        quantity: float,
        pending_quantity: float,
        processed_quantity: float,
        canceled_quantity: float,
        legs: List[OptionLeg],
        created_at: datetime,
        updated_at: datetime,
    ) -> None:
        self._order_id = order_id
        self._order_type = order_type
        self._ref_id = ref_id
        self._state = state
        self._trigger = trigger
        self._chain_symbol = chain_symbol
        self._chain_id = chain_id
        self._opening_strategy = opening_strategy
        self._closing_strategy = closing_strategy
        self._direction = direction
        self._response_category = response_category
        self._time_in_force = time_in_force
        self._premium = premium
        self._processed_premium = processed_premium
        self._price = price
        self._stop_price = stop_price
        self._quantity = quantity
        self._pending_quantity = pending_quantity
        self._processed_quantity = processed_quantity
        self._canceled_quantity = canceled_quantity
        self._legs = legs
        self._created_at = created_at
        self._updated_at = updated_at

    @property
    def order_id(self) -> str:
        return self._order_id

    @property
    def chain_symbol(self) -> str:
        return self._chain_symbol

    @property
    def state(self) -> str:
        return self._state

    @property
    def direction(self) -> str:
        return self._direction

    @property
    def opening_strategy(self) -> Optional[str]:
        if self._opening_strategy is None:
            return self._opening_strategy

        if self._opening_strategy not in {
            'short_call',
            'short_put',
            'long_call',
            'long_put',
        }:
            return self._opening_strategy

        if self.num_of_legs == 1:
            return self._opening_strategy

        return 'custom'

    @property
    def closing_strategy(self) -> Optional[str]:
        return self._closing_strategy

    @property
    def opening_strategy_name(self) -> Optional[str]:
        if self.opening_strategy is None:
            return None

        return self.opening_strategy.replace('_', ' ').upper()

    @property
    def closing_strategy_name(self) -> Optional[str]:
        if self._closing_strategy is None:
            return None

        return self._closing_strategy.replace('_', ' ').upper()

    @property
    def legs(self) -> List[OptionLeg]:
        return self._legs

    @property
    def opening_legs(self) -> List[OptionLeg]:
        return [
            leg for leg in self.legs
            if leg.position_effect == 'open'
        ]

    @property
    def quantity(self) -> float:
        return self._quantity

    @property
    def processed_quantity(self) -> float:
        return self._processed_quantity

    @property
    def price(self) -> Optional[float]:
        if self._price is None:
            return None

        sign = 1 if self._direction == 'debit' else -1
        return self._price * sign

    @property
    def updated_at(self) -> datetime:
        return self._updated_at

    @property
    def rolling_order(self) -> Optional[OptionRollingOrder]:
        return derive_option_rolling_order(option_order=self)

    @property
    def num_of_legs(self) -> int:
        return len(self._legs)

    @property
    def is_buy_to_close(self) -> bool:
        return (
            self.direction == 'debit'
            and len(self.legs) == 1
            and self.legs[0].side == 'buy'
            and self.legs[0].position_effect == 'close'
        )

    @property
    def is_fig_leaf_open(self) -> bool:
        if not self.is_custom_open_strategy:
            return False

        if self.num_of_legs != 2:
            return False

        buy_leg = None
        sell_leg = None
        for leg in self.legs:
            if not leg.is_open:
                return False

            if leg.is_buy:
                buy_leg = leg

            if leg.is_sell:
                sell_leg = leg

        if buy_leg is None or sell_leg is None:
            return False

        return buy_leg.option_instrument.exp_date > sell_leg.option_instrument.exp_date

    @property
    def is_fig_leaf_close(self) -> bool:
        if not self.is_custom_close_strategy:
            return False

        if self.num_of_legs != 2:
            return False

        buy_leg = None
        sell_leg = None
        for leg in self.legs:
            if not leg.is_close:
                return False

            if leg.is_buy:
                buy_leg = leg

            if leg.is_sell:
                sell_leg = leg

        if buy_leg is None or sell_leg is None:
            return False

        return buy_leg.option_instrument.exp_date < sell_leg.option_instrument.exp_date

    @property
    def is_custom_open_strategy(self) -> bool:
        return self.opening_strategy == 'custom'

    @property
    def is_custom_close_strategy(self) -> bool:
        return self.closing_strategy == 'custom'

    @property
    def fig_leaf_symbol(self) -> str:
        assert self.is_fig_leaf_open or self.is_fig_leaf_close

        buy_leg = None
        sell_leg = None
        for leg in self.legs:
            if leg.is_buy:
                buy_leg = leg

            if leg.is_sell:
                sell_leg = leg

        assert buy_leg is not None
        assert sell_leg is not None
        if self.is_fig_leaf_open:
            near_term_symbol = sell_leg.option_instrument.symbol
            far_term_strike_price = buy_leg.option_instrument.strike_price
            far_term_exp_date = buy_leg.option_instrument.formatted_exp_date
        else:
            near_term_symbol = buy_leg.option_instrument.symbol
            far_term_strike_price = sell_leg.option_instrument.strike_price
            far_term_exp_date = sell_leg.option_instrument.formatted_exp_date

        return self.get_two_leg_symbol(
            left_symbol=near_term_symbol,
            right_exp_date=far_term_exp_date,
            right_instrument_type='C',
            right_strike_price=far_term_strike_price,
        )

    @property
    def spread_symbol(self) -> str:
        if self.num_of_legs != 2:
            raise ValueError('Spread must have two legs.')

        buy_leg = None
        sell_leg = None
        for leg in self.legs:
            if leg.is_buy:
                buy_leg = leg
            else:
                sell_leg = leg
        if buy_leg is None or sell_leg is None:
            raise ValueError('Spread must have one leg buy and one leg sell.')

        buy_strike_type = buy_leg.option_instrument.instrument_type_short
        sell_strike_type = sell_leg.option_instrument.instrument_type_short
        if buy_strike_type != sell_strike_type:
            raise TypeError('Spread must have the same instrument type.')
        instrument_type = buy_strike_type
        buy_strike_price = buy_leg.option_instrument.strike_price
        sell_strike_price = sell_leg.option_instrument.strike_price
        if buy_strike_price == sell_strike_price:
            raise TypeError('Spread must have two legs with different strike price.')

        if instrument_type == 'C' and buy_strike_price < sell_strike_price:
            _left = buy_leg
            _right = sell_leg
        elif instrument_type == 'C' and buy_strike_price > sell_strike_price:
            _left = sell_leg
            _right = buy_leg
        elif instrument_type == 'P' and buy_strike_price < sell_strike_price:
            _left = sell_leg
            _right = buy_leg
        elif instrument_type == 'P' and buy_strike_price > sell_strike_price:
            _left = buy_leg
            _right = sell_leg

        return self.get_two_leg_symbol(
            left_symbol=_left.option_instrument.symbol,
            right_exp_date=_right.option_instrument.formatted_exp_date,
            right_instrument_type=instrument_type,
            right_strike_price=_right.option_instrument.strike_price,
        )

    @property
    def concatenated_symbol(self) -> str:
        components: List[str] = []
        for leg in self.legs:
            if leg.is_buy:
                direction = ''
            else:
                assert leg.is_sell
                direction = '-'

            if leg.is_open:
                open_or_close = ''
            else:
                assert leg.is_close
                open_or_close = '-'

            symbol = leg.option_instrument.symbol
            ratio = '' if leg.ratio_quantity == 1 else f'x{leg.ratio_quantity}'
            components.append(f'{direction}{symbol}{ratio}{open_or_close}')

        components.sort()
        return '/'.join(components)

    @property
    def is_rolling_short_spread(self) -> bool:
        if self.num_of_legs != 4:
            return False

        instrument_type = self.legs[0].option_instrument.instrument_type
        assert instrument_type in {'call', 'put'}
        num_of_buy_to_close = 0
        num_of_sell_to_close = 0
        num_of_sell_to_open = 0
        num_of_buy_to_open = 0
        for leg in self.legs:
            if leg.option_instrument.instrument_type != instrument_type:
                return False

            if leg.is_buy and leg.is_close:
                num_of_buy_to_close += 1
                continue

            if leg.is_sell and leg.is_close:
                num_of_sell_to_close += 1
                continue

            if leg.is_sell and leg.is_open:
                num_of_sell_to_open += 1
                continue

            if leg.is_buy and leg.is_open:
                num_of_buy_to_open += 1
                continue

        return (
            num_of_buy_to_close == 1
            and num_of_sell_to_close == 1
            and num_of_sell_to_open == 1
            and num_of_buy_to_open == 1
        )

    def get_two_leg_symbol(
        self,
        left_symbol: str,
        right_exp_date: str,
        right_instrument_type: str,
        right_strike_price: float,
    ) -> str:
        return (
            f'{left_symbol}/'
            f'{right_exp_date}{right_instrument_type}{right_strike_price}'
        )


def option_order_from_data(data: Dict[str, Any]) -> OptionOrder:
    legs = [
        option_leg_from_data(data=row)
        for row in data['legs']
    ]
    return OptionOrder(
        order_id=data['id'],
        order_type=data['type'],
        ref_id=data['ref_id'],
        state=data['state'],
        trigger=data['trigger'],
        chain_symbol=data['chain_symbol'],
        chain_id=data['chain_id'],
        opening_strategy=data['opening_strategy'],
        closing_strategy=data['closing_strategy'],
        direction=data['direction'],
        response_category=data['response_category'],
        time_in_force=data['time_in_force'],
        premium=parse_optional_float(data['premium']),
        processed_premium=float(data['processed_premium']),
        price=parse_optional_float(data['price']),
        stop_price=parse_optional_float(data['stop_price']),
        quantity=float(data['quantity']),
        pending_quantity=float(data['pending_quantity']),
        processed_quantity=float(data['processed_quantity']),
        canceled_quantity=float(data['canceled_quantity']),
        legs=legs,
        created_at=parse_datetime_with_microsecond(data['created_at']),
        updated_at=parse_datetime_with_microsecond(data['updated_at']),
    )
