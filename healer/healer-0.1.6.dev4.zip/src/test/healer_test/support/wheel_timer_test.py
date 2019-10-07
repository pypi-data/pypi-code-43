
import math
import time

from healer.support.wheel_timer import *


def test_wheel_timer_single():
    print()

    wheel_tick = 10
    wheel_size = 10
    delay_one = 451
    delay_two = 725

    timer = WheelTimer(wheel_tick=wheel_tick, wheel_size=wheel_size)

    timer.start()

    time_start = time.time_ns()
    time_finish_one = None
    time_finish_two = None

    def task_one():
        nonlocal time_finish_one
        time_finish_one = time.time_ns()
        print(f"one @ thread: {threading.current_thread()}")

    def task_two():
        nonlocal time_finish_two
        time_finish_two = time.time_ns()
        print(f"two @ thread: {threading.current_thread()}")

    entry_one = timer.schedule_single(timer_task=task_one, delay_milli=delay_one,)
    entry_two = timer.schedule_single(timer_task=task_two, delay_milli=delay_two,)

    print(f"entry_one: {entry_one}")
    print(f"entry_two: {entry_two}")

    print(f"bucket_list: {timer.bucket_list}")

    time.sleep(1.5)

    time_diff_one = (time_finish_one - time_start) / 1000000
    time_diff_two = (time_finish_two - time_start) / 1000000

    print(f"time_diff_one: {time_diff_one}")
    print(f"time_diff_two: {time_diff_two}")

    assert math.fabs(time_diff_one - delay_one) <= wheel_tick
    assert math.fabs(time_diff_two - delay_two) <= wheel_tick

    timer.stop()


def pair_diff(data_list:list) -> list:
    return [ int((y - x) / 1000000) for x, y in zip(data_list , data_list [1:]) ]


def test_wheel_timer_periodic():
    print()

    wheel_tick = 10
    wheel_size = 10

    delay_one = 543
    period_one = 234

    delay_two = 234
    period_two = 543

    timer = WheelTimer(wheel_tick=wheel_tick, wheel_size=wheel_size)

    timer.start()

    time_list_one = [time.time_ns()]
    time_list_two = [time.time_ns()]

    def task_one():
        nonlocal time_list_one
        time_list_one.append(time.time_ns())
        print(f"one @ thread: {threading.current_thread()}")

    def task_two():
        nonlocal time_list_two
        time_list_two.append(time.time_ns())
        print(f"two @ thread: {threading.current_thread()}")

    entry_one = timer.schedule_periodic(
        timer_task=task_one, delay_milli=delay_one, period_milli=period_one,
    )

    entry_two = timer.schedule_periodic(
        timer_task=task_two, delay_milli=delay_two, period_milli=period_two,
    )

    print(f"entry_one: {entry_one}")
    print(f"entry_two: {entry_two}")

    time.sleep(2)

    source_diff_one = pair_diff(time_list_one)
    target_diff_one = [delay_one, period_one, period_one, period_one, period_one, period_one, period_one, period_one, period_one, period_one, ]
    print(f"source_diff_one: {source_diff_one}")
    print(f"target_diff_one: {target_diff_one}")
    result_zip_one = zip(source_diff_one, target_diff_one)
    assert all([math.fabs(x - y) <= wheel_tick for x, y in result_zip_one])

    source_diff_two = pair_diff(time_list_two)
    target_diff_two = [delay_two, period_two, period_two, period_two, period_two, period_two, period_two, period_two, period_two, period_two, ]
    print(f"source_diff_two: {source_diff_two}")
    print(f"target_diff_two: {target_diff_two}")
    result_zip_two = zip(source_diff_two, target_diff_two)
    assert all([math.fabs(x - y) <= wheel_tick for x, y in result_zip_two])

    timer.stop()


def test_wheel_timer_system():
    print()

    instance = SystemWheelTimer.instance()

    assert instance is not None
    assert instance.state_event is not None

    instance.stop()
