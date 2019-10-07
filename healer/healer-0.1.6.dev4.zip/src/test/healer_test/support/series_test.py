"""
"""

import math

from healer.support.series import *


def test_motion_tuple():
    print()

    source = MotionTuple(MotionState.DECREASE, MotionState.INCREASE)
    target = source.rotate(MotionState.INCREASE)
    assert target == MotionTuple(MotionState.INCREASE, MotionState.INCREASE)


def test_moving_average():
    print()

    unit_one = MovingAverage()

    unit_one.update(1)
    unit_one.update(2)
    unit_one.update(3)

    print(unit_one)
    assert unit_one.has_delta(value=0.964)

    unit_one.update(3)
    unit_one.update(3)
    unit_one.update(3)

    print(unit_one)
    assert unit_one.has_delta(value=1.885)

    unit_two = MovingAverage(delta=3, period=3, target=100)
    for index in range(100):
        unit_two.update(index)
    print(unit_two)
    assert unit_two.has_delta()


def test_motion_trigger():
    print()

    window = 10

    trigger = MotionTrigger(period_fast=3, period_slow=5, delta=0.7)

    def report(index:float) -> None:
        trigger.update(index)
        print(f"index={index} delta={trigger.delta_abs} state={trigger.state}")

    print(f"--- setup ---")

    for index in range(1, window, +1):
        report(window / 3)

    print(f"--- increase ---")

    for index in range(1, window, +1):
        report(index)

    print(f"--- flatline ---")

    for index in range(1, window, +1):
        index = window
        report(index)

    print(f"--- decrease ---")

    for index in range(window, 1, -1):
        report(index)


def xtest_motion_delta():
    print()

    window = 15

    trigger = MotionDelta(period=5, change=0.5)

    def report(index:float) -> None:
        trigger.update(index)
        print(f"index={index} delta={trigger.delta_change} state={trigger.state}")

    for index in range(1, window, +1):
        report(0)

    print(f"--- increase ---")

    for index in range(1, window, +1):
        report(index)

    print(f"--- flatline ---")

    for index in range(1, window, +1):
        index = window
        report(index)

    print(f"--- decrease ---")

    for index in range(window, 1, -1):
        report(index)
