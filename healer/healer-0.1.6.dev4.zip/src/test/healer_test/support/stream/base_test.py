"""
"""

from __future__ import annotations

import time

from healer.support.stream.base import *


def test_signal_revalue():
    print()

    origin = numpy.array([
        1, 2, 3, 4, 5, 4, 3, 2, 1,
    ])

    result_list = Signal.revalue(signal=origin)
    print(f"result_list: {result_list}")


def test_signal_distance():
    print()
    sig_one = numpy.array([1, 2, 3, 4])
    sig_two = numpy.array([1.1, 2.2, 3.3, 4.4])
    distance = Signal.distance(sig_one, sig_two)
    print(f"distance={distance}")


def test_signal_resample():
    print()

    origin = numpy.array([
        1, 2, 3, 4, 5, 4, 3, 2, 1,
    ])

    result_decr = Signal.resample(signal=origin, size=3)
    print(f"result_decr: {result_decr}")

    result_incr = Signal.resample(signal=origin, size=15)
    print(f"result_incr: {result_incr}")


def test_wavelet():
    print()

    source = Stream.source(name='one')
    source.target(fun=lambda x: print(f"one: {x}"))

    wavelet = source.wavelet(name='wav', depth=2, length=8)
    wavelet.target(fun=lambda x: print(f"wav: {x}"))

    print(wavelet)

    for value in range(1, 21):
        source.insert(value)


def test_combo_paired():
    print()

    source_one = Stream.source(name='one')
    source_one.target(fun=lambda x: print(f"one: {x}"))

    source_two = Stream.source(name='two')
    source_two.target(fun=lambda x: print(f"two: {x}"))

    result_list = []

    combo = Stream.combo_paired(source_list=[source_one, source_two])
    combo.target(fun=lambda x: print(f"com: {x}"))
    combo.target(fun=lambda x: result_list.append(x))

    for one in ['a', 'b', 'c']:
        source_one.insert(one)
        for two in [1, 2, 3]:
            source_two.insert(two)

    print(f"result_list: {result_list}")
    assert result_list == [('a', 1), ('b', 2), ('c', 3)]


def test_combo_latest():
    print()

    source_one = Stream.source(name='one')
    source_one.target(fun=lambda x: print(f"one: {x}"))

    source_two = Stream.source(name='two')
    source_two.target(fun=lambda x: print(f"two: {x}"))

    result_list = []

    combo = Stream.combo_latest(source_list=[source_one, source_two])
    combo.target(fun=lambda x: print(f"com: {x}"))
    combo.target(fun=lambda x: result_list.append(x))

    for one in ['a', 'b', 'c']:
        source_one.insert(one)
        for two in [1, 2, 3]:
            source_two.insert(two)

    print(f"result_list: {result_list}")

    assert result_list == [('a', 1), ('a', 2), ('a', 3), ('b', 3), ('b', 1), ('b', 2), ('b', 3), ('c', 3), ('c', 1), ('c', 2), ('c', 3)]


def test_trig_trend():
    print()

    result_list = []

    def target_task(state):
        nonlocal result_list
        result_list.append(state)
        print(f"state: {state}")

    list_beg = Stream.from_list(value_list=[0, 0, 0, 0])
    list_inc = Stream.from_list(value_list=[1, 2, 3, 4])
    list_top = Stream.from_list(value_list=[4, 4, 4, 4])
    list_dec = Stream.from_list(value_list=[4, 3, 2, 1])
    list_end = Stream.from_list(value_list=[0, 0, 0, 0])

    source_list = [
        list_beg,
        list_inc,
        list_top,
        list_dec,
        list_end,
    ]

    source = Stream.source(source_list=source_list)

    source.target(fun=print)

    trig_trend = source.trig_trend(size=4, delta=0.5)
    trig_trend.target(fun=target_task)

    for source in source_list:
        source.start()

    print(f"result_list: {result_list}")

    assert result_list == ['UNKNOWN', 'FLATLINE', 'INCREASE', 'FLATLINE', 'DECREASE', 'FLATLINE']


def test_trig_delta():
    print()

    result_list = []

    def target_task(state):
        nonlocal result_list
        result_list.append(state)
        print(f"state: {state}")

    source = Stream.from_list(value_list=range(1, 9, 1))
    source.target(fun=print)
    trig_delta = source.trig_delta(value=5, delta=1)
    trig_delta.target(fun=target_task)

    source.start()

    assert result_list == [False, True, False]


def test_stream_filter():
    print()

    index = 10

    def event_task() -> Any:
        nonlocal index
        index += 1
        print(f"task index: {index}")
        return index

    def event_filter(value:int) -> bool:
        return value % 2 == 0

    period = Stream.ticker(fun=event_task, period=200, name="timer")
    select = period.select(fun=event_filter, name="select")
    print_sel = select.target(fun=lambda x: print(f"select: {x}"), name="printer-1")

    calc_min = period.calc_min(name="minimum")
    print_min = calc_min.target(fun=lambda x: print(f"calc-min: {x}"), name="printer-min")

    calc_max = period.calc_max(name="maximum")
    print_max = calc_max.target(fun=lambda x: print(f"calc-max: {x}"), name="printer-max")

    calc_avg = period.calc_avg(size=3, name="average")
    print_avg = calc_avg.target(fun=lambda x: print(f"calc-avg: {x}"), name="printer-avg")

    print(period)
    print(select)
    print(calc_avg)
    print(calc_min)
    print(calc_max)
    print(print_sel)
    print(print_min)
    print(print_max)
    print(print_avg)

    period.start()
    time.sleep(2)
    period.stop()


def test_stream_window():
    print()

    def event_task() -> Any:
        print(f"task")
        return time.time_ns()

    period = Stream.ticker(fun=event_task, period=200, name="timer")
    window = period.window(size=3, use_part=True, name="window")
    print_1 = window.target(fun=print, name="printer-1")

    print(period)
    print(window)
    print(print_1)

    period.start()
    time.sleep(2)
    period.stop()


def test_stream_periodic():
    print()

    def event_task() -> Any:
        print(f"task")
        return time.time()

    period = Stream.ticker(fun=event_task, period=200, name="timer")
    detain = period.detain(delay=300, name="delayer")
    print_1 = period.target(fun=print, name="printer-1")
    print_2 = detain.target(fun=print, name="printer-2")

    print(period)
    print(detain)
    print(print_1)
    print(print_2)

    period.start()
    time.sleep(2)
    period.stop()
    time.sleep(1)


def test_stream_mapper():
    print()

    stream = Stream.source(name="base")

    print_1 = stream.target(fun=print, name="print_1")
    print_2 = stream.base_map(fun=lambda x : x * 2).target(fun=print, name="print_2")
    print_3 = stream.base_map(fun=lambda x : x + 10).target(fun=print, name="print_3")

    print(stream)
    print(print_1)
    print(print_2)
    print(print_3)

    stream.insert(123)

    root_set = Build.locate_root(stream)
    print(f"root_set: {root_set}")
