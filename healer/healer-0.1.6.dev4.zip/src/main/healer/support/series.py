"""
Time series operations
"""

from __future__ import annotations

import array
import enum
import math
from dataclasses import dataclass
from dataclasses import field
from typing import List

from healer.support.typing import AutoNameEnum


@dataclass(frozen=True)
class StateTuple:
    state_past:bool = False
    state_next:bool = False

    def has_change(self) -> bool:
        return self.state_past != self.state_next

    def has_positive(self) -> bool:
        return not self.state_past and self.state_next

    def has_negative(self) -> bool:
        return self.state_past and not self.state_next

    def rotate(self, state_next:bool) -> StateTuple:
        return StateTuple(state_past=self.state_next, state_next=state_next)


@dataclass
class MovingAverage:
    "exponential moving average"

    average:float = 0.0  # current average
    target:float = 0.0  # target average for match

    delta:float = 0.01  # margin gap

    period:int = 10  # exponential decay window
    factor:float = field(init=False)  # exponential decay factor

    def __post_init__(self):
        assert self.delta > 0, f"need delta>0: {self.delta}"
        assert self.period > 0, f"need period>0: {self.period}"
        self.factor = 2 / (self.period + 1)

    def update(self, value:float) -> float:
        "update moving average with new measurment"
        self.average = float(self.average + self.factor * (value - self.average))
        return self.average

    def has_delta(self, value:float=None, delta:float=None) -> bool:
        "verify current average against the target value"
        value = value or self.target
        delta = delta or self.delta
        return math.fabs(value - self.average) < delta


@enum.unique
class MotionState(AutoNameEnum):
    "detected trigger state"

    UNKNOWN = enum.auto()
    INCREASE = enum.auto()
    DECREASE = enum.auto()
    FLATLINE = enum.auto()


@dataclass(frozen=True)
class MotionTuple:
    "state transition detector"

    state_past:MotionState = MotionState.UNKNOWN
    state_next:MotionState = MotionState.UNKNOWN

    def has_any(self) -> bool:
        if self.state_past == MotionState.UNKNOWN:
            return False
        if self.state_next == MotionState.UNKNOWN:
            return False
        return True

    def has_change(self) -> bool:
        if self.has_any():
            return self.state_past != self.state_next
        else:
            return False

    def has_increase(self) -> bool:
        return self.has_change() and self.state_next == MotionState.INCREASE

    def has_decrease(self) -> bool:
        return self.has_change() and self.state_next == MotionState.DECREASE

    def has_flatline(self) -> bool:
        return self.has_change() and self.state_next == MotionState.FLATLINE

    def rotate(self, state_next:MotionTuple) -> MotionTuple:
        return MotionTuple(state_past=self.state_next, state_next=state_next)


@dataclass(init=False)
class MotionTrigger:
    "fast vs slow moving average trigger"

    motion_fast:MovingAverage
    motion_slow:MovingAverage
    delta:float
    count:int
    limit:int

    def __init__(self,
            period_fast:float=5,
            period_slow:float=10,
            delta:float=1.0,
        ) -> None:
        assert delta > 0, f"need match > 0: {delta}"
        assert period_fast < period_slow, f"wrong fast/slow: {period_fast} vs {period_slow}"
        self.motion_fast = MovingAverage(period=period_fast, delta=delta,)
        self.motion_slow = MovingAverage(period=period_slow, delta=delta,)
        self.delta = delta
        self.count = 0
        self.limit = int((period_fast + period_slow) * 0.7)

    @property
    def delta_abs(self) -> float:
        "report fast vs slow absolute average difference"
        average_fast = self.motion_fast.average
        average_slow = self.motion_slow.average
        return average_fast - average_slow

    @property
    def delta_rel(self) -> float:
        "report fast vs slow relative average difference"
        return self.delta_absolute / math.fabs(self.motion_fast.average)

    @property
    def state(self) -> MotionState:
        "report motion trigger state"
        if self.count <= self.limit:
            return MotionState.UNKNOWN
        if self.delta_abs > +self.delta:
            return MotionState.INCREASE
        if self.delta_abs < -self.delta:
            return MotionState.DECREASE
        return MotionState.FLATLINE

    def update(self, value:float) -> float:
        "update moving average with new measurment"
        self.motion_fast.update(value)
        self.motion_slow.update(value)
        self.count += 1
        return self.delta_abs


@dataclass(init=False)
class MotionDelta:
    "motion direction trigger"

    index:int
    count:int
    period:int

    change:float
    value:float
    delta_list:array.array[float] = field(repr=False)

    def __init__(self, period:int=10, change:float=0.5):
        ""
        assert period > 0, f"need period > 0: {period}"
        assert change > 0, f"need change > 0: {change}"
        self.index = 0
        self.count = 0
        self.value = 0
        self.period = period
        self.change = change
        self.delta_list = array.array('d', [0.0 for _ in range(period)])

    def update(self, value:float) -> float:
        "update with new measurment"
        delta = value - self.value
        self.value = value
        self.delta_list[self.index] = delta
        self.count += 1
        self.index = self.count % self.period
        return delta

    @property
    def delta_abs(self) -> float:
        return sum(map(math.fabs, self.delta_list))

    @property
    def delta_rel(self) -> float:
        return sum(self.delta_list)

    @property
    def delta_change(self) -> float:
        return self.delta_rel / self.period

    @property
    def state(self) -> MotionState:
        ""
        if self.count < self.period:
            return MotionState.UNKNOWN
        delta_change = self.delta_change
        if delta_change > +self.change:
            return MotionState.INCREASE
        if delta_change < -self.change:
            return MotionState.DECREASE
        return MotionState.FLATLINE
