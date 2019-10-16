from typing import Dict


class MinTicks(object):
    def __init__(
        self,
        cutoff_price: float,
        below_tick: float,
        above_tick: float,
    ) -> None:
        self._cutoff_price = cutoff_price
        self._below_tick = below_tick
        self._above_tick = above_tick

    @property
    def cutoff_price(self) -> float:
        return self._cutoff_price

    @property
    def below_tick(self) -> float:
        return self._below_tick

    @property
    def above_tick(self) -> float:
        return self._above_tick

    def get_min_tick_price_round_up(self, price: float) -> float:
        return self._get_min_tick_price(price=price, up_or_down='up')

    def get_min_tick_price_round_down(self, price: float) -> float:
        return self._get_min_tick_price(price=price, up_or_down='down')

    def _get_min_tick_price(self, price: float, up_or_down: str) -> float:
        if up_or_down not in {'up', 'down'}:
            raise ValueError(f'Incorret parameter `up_or_down`: {up_or_down}')

        if price == self._cutoff_price:
            return price

        if price < self._cutoff_price:
            tick = self._below_tick
        else:
            tick = self._above_tick

        price100 = price * 100
        tick100 = tick * 100

        if price100 % tick100 == 0:
            return price

        _n = price100 // tick100
        if up_or_down == 'up':
            _n += 1

        return _n * tick100 / 100


def min_ticks_from_data(data: Dict[str, str]) -> MinTicks:
    return MinTicks(
        cutoff_price=float(data['cutoff_price']),
        below_tick=float(data['below_tick']),
        above_tick=float(data['above_tick']),
    )
