"""
Basic event stream processor
"""

from __future__ import annotations

import collections
import enum
import functools
import math
import threading
from typing import Any
from typing import Callable
from typing import List
from typing import Mapping
from typing import Set
from typing import Type

import numpy
from scipy import interpolate

from healer.support.parser import convert_camel_under
from healer.support.typing import AutoNameEnum
from healer.support.typing import override
from healer.support.wheel_timer import SystemWheelTimer
from healer.support.wheel_timer import TimerEntry


@enum.unique
class Trend(AutoNameEnum):
    "function motion detection trend"

    UNKNOWN = enum.auto()
    INCREASE = enum.auto()
    DECREASE = enum.auto()
    FLATLINE = enum.auto()


class Stream:
    "base type of event stream processor"

    Trend = Trend

    name:str  # node name

    params:dict  # mapper parameters
    function:Callable  # mapper function

    source_list:List  # upstream nodes
    target_list:List  # downstream nodes

    def __init__(self, **kwargs) -> None:

        self.name = kwargs.pop('name', None)
        self.function = kwargs.pop('fun', Stream.identity)
        source = kwargs.pop('source', None)
        source_list = kwargs.pop('source_list', None)
        target = kwargs.pop('target', None)
        target_list = kwargs.pop('target_list', None)

        self.params = kwargs  # function invocation

        self.source_list = list()
        self.target_list = list()

        if source:
            self.source_list.append(source)
        if source_list:
            self.source_list.extend(source_list)
        if target:
            self.target_list.append(target)
        if target_list:
            self.target_list.extend(target_list)

        assert self not in self.source_list, f"self in sources: {self.source_list}"
        assert self not in self.target_list, f"self in targets: {self.target_list}"

        for source in self.source_list:
            source.target_list.append(self)

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self.name})"

    def reset(self) -> None:
        "reset stream state"

    def start(self) -> None:
        for source in self.source_list:
            source.start()

    def stop(self) -> None:
        for source in self.source_list:
            source.stop()

    def insert(self, value:Any) -> Any:
        "propagate event into downstream targets"
        result_list = []
        for target in self.target_list:
            result = target.update(value, source=self)
            if result is not None:
                if type(result) is list:
                    result_list.extend(result)
                else:
                    result_list.append(result)
        return result_list

    def update(self, value:Any, source:Stream=None) -> Any:
        "propagate event from upstream source"
        return self.insert(value)

    @staticmethod
    def identity(value:Any) -> Any:
        return value

    #
    # stream factory
    #

    @staticmethod
    def from_list(**kwargs) -> FlowFromList:
        return FlowFromList(**kwargs)

    @staticmethod
    def ticker(**kwargs) -> FlowTicker:
        return FlowTicker(**kwargs)

    @staticmethod
    def source(**kwargs) -> FlowSource:
        return FlowSource(**kwargs)

    @staticmethod
    def combo_latest(**kwargs) -> FlowComboLatest:
        return FlowComboLatest(**kwargs)

    @staticmethod
    def combo_paired(**kwargs) -> FlowComboPaired:
        return FlowComboPaired(**kwargs)

    def target(self, **kwargs) -> FlowTarget:
        return FlowTarget(source=self, **kwargs)

    def select(self, **kwargs) -> FlowSelect:
        return FlowSelect(source=self, **kwargs)

    def calc_avg(self, **kwargs) -> FlowCalcAvg:
        return FlowCalcAvg(source=self, **kwargs)

    def calc_min(self, **kwargs) -> FlowCalcMin:
        return FlowCalcMin(source=self, **kwargs)

    def calc_max(self, **kwargs) -> FlowCalcMax:
        return FlowCalcMax(source=self, **kwargs)

    def constant(self, **kwargs) -> FlowConstant:
        return FlowConstant(source=self, **kwargs)

    def detain(self, **kwargs) -> FlowDetain:
        return FlowDetain(source=self, **kwargs)

    def expose(self, **kwargs) -> FlowExpose:
        return FlowExpose(source=self, **kwargs)

    def base_map(self, **kwargs) -> FlowBaseMap:
        return FlowBaseMap(source=self, **kwargs)

    def flat_map(self, **kwargs) -> FlowFlatMap:
        return FlowFlatMap(source=self, **kwargs)

    def record(self, **kwargs) -> FlowRecord:
        return FlowRecord(source=self, **kwargs)

    def sample(self, **kwargs) -> FlowSample:
        return FlowSample(source=self, **kwargs)

    def window(self, **kwargs) -> FlowWindow:
        return FlowWindow(source=self, **kwargs)

    def trig_change(self, **kwargs) -> FlowTrigChange:
        return FlowTrigChange(source=self, **kwargs)

    def trig_delta(self, **kwargs) -> FlowTrigDelta:
        return FlowTrigDelta(source=self, **kwargs)

    def trig_trend(self, **kwargs) -> FlowTrigTrend:
        return FlowTrigTrend(source=self, **kwargs)

    def pattern(self, **kwargs) -> FlowPattern:
        return FlowPattern(source=self, **kwargs)

    def wavelet(self, **kwargs) -> FlowWavelet:
        return FlowWavelet(source=self, **kwargs)


class Build:
    ""

    def source_attach(self, source:Stream) -> None:
        self.source_list.add(source)

    def source_detach(self, source:Stream) -> None:
        self.source_list.remove(source)

    def target_attach(self, target:Stream) -> None:
        self.target_list.add(target)

    def target_detach(self, target:Stream) -> None:
        self.target_list.remove(target)

    @staticmethod
    def register_method(modifier:Callable=Stream.identity) -> Callable:

        def class_wrapper(stream_class:Type[Stream]):

            assert issubclass(stream_class, Stream), f"wrong stream_class: {stream_class}"

            @functools.wraps(stream_class)
            def produce_instance(*args, **kwargs):
                return stream_class(*args, **kwargs)

            method_name = convert_camel_under(stream_class.__name__)
            assert not hasattr(Stream, method_name), f"need unique: method_name: {method_name}"
            setattr(Stream, method_name, modifier(produce_instance))
            return stream_class

        return class_wrapper

    @staticmethod
    def locate_root(stream:Stream) -> Set[Stream]:
        root_set = set()
        if stream.source_list:
            for source in stream.source_list:
                root_set.update(Build.locate_root(source))
        else:
            root_set.add(stream)
        return root_set

#
#
#


class FlowSource(Stream):
    "initial event producer"


class FlowTarget(Stream):
    "terminal event consumer"

    def update(self, value:Any, source:Stream=None) -> None:
        self.function(value, **self.params)


class FlowFromList(Stream):
    "produce stream from iterable"

    def __init__(self, **kwargs):
        self.value_list = kwargs.pop('value_list')
        super().__init__(**kwargs)

    @override
    def start(self):
        super().start()
        for value in self.value_list:
            self.insert(value)

    @override
    def stop(self):
        super().stop()


class FlowTicker(Stream):
    "periodic value source"

    system_timer = SystemWheelTimer.instance()
    timer_entry:TimerEntry = None

    def __init__(self, **kwargs):
        self.period = kwargs.pop('period')
        super().__init__(**kwargs)

    def ticker_task(self) -> None:
        "produce stream value"
        value = self.function(**self.params)
        self.insert(value)

    @override
    def start(self):
        if not self.timer_entry:
            self.timer_entry = self.system_timer.schedule_periodic(
                timer_task=self.ticker_task, delay_milli=self.period, period_milli=self.period,
            )

    @override
    def stop(self):
        if self.timer_entry:
            self.timer_entry.issue_cancel()
            self.timer_entry = None


class FlowDetain(Stream):
    "event stream delay"

    system_timer = SystemWheelTimer.instance()

    def __init__(self, **kwargs):
        self.delay = kwargs.pop('delay')
        super().__init__(**kwargs)

    @override
    def update(self, value:Any, source:Stream=None) -> TimerEntry:
        timer_task = lambda : self.insert(self.function(value, **self.params))
        timer_entry = self.system_timer.schedule_single(
            timer_task=timer_task, delay_milli=self.delay,
        )
        return timer_entry


class FlowBaseMap(Stream):
    "direct event mapper"

    def update(self, value:Any, source:Stream=None) -> Any:
        value = self.function(value, **self.params)
        return self.insert(value)


class FlowFlatMap(Stream):
    "TODO"

    def update(self, value:Any, source:Stream=None) -> Any:
        value = self.function(value, **self.params)
        return self.insert(value)


class FlowExpose(Stream):
    "expose current value"

    value:Any = None

    def apply(self, function:Callable) -> Any:
        if self.value is None:
            return None
        else:
            return function(self.value)

    def update(self, value:Any, source:Stream=None) -> Any:
        self.value = value
        return self.insert(value)


class FlowCalcAvg(Stream):
    "current average value"

    value:float = None

    def __init__(self, **kwargs):
        self.size = kwargs.pop('size')
        self.factor = 2 / (self.size + 1)
        super().__init__(**kwargs)

    @override
    def reset(self) -> None:
        self.value = None

    @override
    def update(self, value:Any, source:Stream=None) -> Any:
        value = self.function(value, **self.params)
        assert isinstance(value, (int, float)), f"need number: {value}"
        if self.value is None:
            self.value = value
        else:
            self.value += self.factor * (value - self.value)
        return self.insert(self.value)


class FlowCalcDot(Stream):
    "current extreme value"

    value:float = None
    has_run:bool = False
    use_run:bool = False

    def __init__(self, **kwargs):
        self.use_run = kwargs.pop('use_run', False)
        super().__init__(**kwargs)

    def has_state(self, value:float) -> bool:
        raise NotImplemented()

    def apply(self, value:float) -> Any:
        self.value = value
        return self.insert(value)

    @override
    def reset(self) -> None:
        self.stop()
        self.value = None

    @override
    def start(self):
        self.has_run = True

    @override
    def stop(self):
        self.has_run = False

    @override
    def update(self, value:Any, source:Stream=None) -> Any:
        if self.use_run and not self.has_run:
            return
        value = self.function(value, **self.params)
        assert isinstance(value, (int, float)), f"need number: {value}"
        if self.value is None:
            return self.apply(value)
        else:
            if self.has_state(value):
                return self.apply(value)
            else:
                return None


class FlowCalcMin(FlowCalcDot):
    "current minimum value"

    @override
    def has_state(self, value:float) -> bool:
        return value < self.value


class FlowCalcMax(FlowCalcDot):
    "current maximum value"

    @override
    def has_state(self, value:float) -> bool:
        return value > self.value


class FlowSelect(Stream):
    "value select filter"

    @override
    def update(self, value:Any, source:Stream=None) -> Any:
        state = self.function(value, **self.params)
        if state is True:
            return self.insert(value)
        else:
            return None


class FlowWindow(Stream):
    "sliding window buffer"

    size:int
    use_part:bool
    buffer:collections.deque

    def __init__(self, **kwargs):
        self.size = kwargs.pop('size')
        self.use_part = kwargs.pop('use_part', False)
        super().__init__(**kwargs)
        self.buffer = collections.deque(maxlen=self.size)

    @override
    def update(self, value:Any, source:Stream=None) -> List[Any]:
        value = self.function(value, **self.params)
        self.buffer.append(value)
        if self.use_part or len(self.buffer) >= self.size:
            return self.insert(tuple(self.buffer))
        else:
            return []


class FlowTrigChange(Stream):
    "value change detector"

    value:float = None

    @override
    def update(self, value:Any, source:Stream=None) -> Any:
        value = self.function(value, **self.params)
        if self.value is None:
            self.value = value
            return None
        change = value - self.value
        self.value = value
        if change == 0:
            return None
        else:
            return self.insert(value)


class FlowTrigDelta(Stream):
    "value delta detector"

    value:float = None  # target value
    delta:float = None  # value deviation
    use_init:bool = None  # propagate inital state
    has_delta:bool = None  # previous delta state

    def __init__(self, **kwargs):
        self.value = kwargs.pop('value')
        self.delta = kwargs.pop('delta')
        self.use_init = kwargs.pop('use_init', True)
        assert self.value is not None, f"need value: {self.value}"
        assert self.delta > 0, f"need delta>0: {self.delta}"
        super().__init__(**kwargs)

    @override
    def update(self, value:Any, source:Stream=None) -> Any:
        value = self.function(value, **self.params)
        assert isinstance(value, (int, float)), f"need number: {value}"
        has_delta = math.fabs(value - self.value) <= self.delta
        if self.has_delta is None:
            self.has_delta = has_delta
            if self.use_init:  # propagate inital state
                return self.insert(has_delta)
            else:
                return None
        elif bool(has_delta) ^ bool(self.has_delta):  # propagate state change
            self.has_delta = has_delta
            return self.insert(has_delta)
        else:
            return None


class FlowTrigTrend(Stream):
    "trend change detector"

    value:float = None  # previous value
    state:Stream.Trend = None  # prevous trend state

    def __init__(self, **kwargs):
        self.size = kwargs.pop('size')
        self.delta = kwargs.pop('delta')
        assert self.size > 1, f"need size>1: {self.size}"
        assert self.delta > 0, f"need delta>0: {self.delta}"
        self.buffer = collections.deque(maxlen=self.size)
        super().__init__(**kwargs)

    @override
    def reset(self) -> None:
        "force event detect now"
        self.state = Stream.Trend.UNKNOWN

    def trend_delta(self) -> float:
        "calculate trend deviation"
        return sum(self.buffer) / self.size

    def trend_state(self) -> Stream.Trend:
        "detect current trend state"
        if len(self.buffer) < self.size:
            return Stream.Trend.UNKNOWN
        delta = self.trend_delta()
        if delta >= +self.delta:
            return Stream.Trend.INCREASE
        if delta <= -self.delta:
            return Stream.Trend.DECREASE
        return Stream.Trend.FLATLINE

    @override
    def update(self, value:Any, source:Stream=None) -> Any:
        value = self.function(value, **self.params)
        assert isinstance(value, (int, float)), f"need number: {value}"
        if self.value is None:
            self.value = value
        delta = value - self.value
        self.value = value
        self.buffer.append(delta)
        state = self.trend_state()
        if state != self.state:  # propagate trend change
            self.state = state
            return self.insert(state)


class FlowRecord(Stream):
    "stored record of stream values"

    size:int  # store limit
    buffer:collections.deque  # stored record

    def __init__(self, **kwargs):
        self.size = kwargs.pop('size')
        assert self.size > 0, f"need size>0: {self.size}"
        super().__init__(**kwargs)
        self.buffer = collections.deque(maxlen=self.size)

    @override
    def reset(self) -> None:
        self.buffer.clear()

    @override
    def update(self, value:Any, source:Stream=None) -> Any:
        value = self.function(value, **self.params)
        self.buffer.append(value)
        return self.insert(value)


class FlowSample(Stream):
    "periodic value sample"

    cycle:int = None  # sample period
    count:int = 0  # running value count

    def __init__(self, **kwargs):
        self.cycle = kwargs.pop('cycle')
        assert self.cycle > 0, f"need cycle>0: {self.cycle}"
        super().__init__(**kwargs)

    @override
    def update(self, value:Any, source:Stream=None) -> Any:
        has_sample = (self.count % self.cycle) == 0
        self.count += 1
        if has_sample:
            value = self.function(value, **self.params)
            return self.insert(value)
        else:
            return None


class FlowComboLatest(Stream):
    "combine latest values from multiple sources"

    use_none:bool  # permit missing stream values
    value_store:Mapping[Stream, Any]  # stored latest values

    def __init__(self, **kwargs):
        self.use_none = kwargs.pop('use_none', False)
        super().__init__(**kwargs)
        assert len(self.source_list) >= 2, f"need many sources: {self.source_list}"
        assert self.function == Stream.identity, f"no use function: {self.function}"
        self.value_store = dict()
        for source in self.source_list:
            self.value_store[source] = None  # start with missing values

    def has_none(self) -> bool:
        "detect any missing values"
        for value in self.value_store.values():
            if value is None:
                return True
        return False

    @override
    def update(self, value:Any, source:Stream=None) -> Any:
        "insert combo with values from upstream"
        self.value_store[source] = value
        if not self.use_none and self.has_none():
            return None
        else:
            combo = tuple(self.value_store.values())  # ordered as sources
            return self.insert(combo)


class FlowComboPaired(Stream):
    "combine paired values from multiple sources"

    size:int  # stored queue limit
    store_lock:threading.Condition  # full store block
    value_store:Mapping[Stream, collections.deque]  # stored latest values

    def __init__(self, **kwargs):
        self.size = kwargs.pop('size', 100)
        super().__init__(**kwargs)
        assert len(self.source_list) >= 2, f"need many sources: {self.source_list}"
        assert self.function == Stream.identity, f"no use function: {self.function}"
        self.value_store = dict()
        self.store_lock = threading.Condition()
        for source in self.source_list:
            self.value_store[source] = collections.deque()  # start with empty store

    @override
    def update(self, value:Any, source:Stream=None) -> Any:
        "insert combo with values from upstream"
        value_stream = self.value_store[source]
        if len(value_stream) >= self.size:
            with self.store_lock:
                self.store_lock.wait()  # block untill notify
        value_stream.append(value)
        if not all(self.value_store.values()):
            return None
        combo = tuple(# ordered as sources
            self.value_store[source].popleft()
            for source in self.source_list
        )
        with self.store_lock:
            self.store_lock.notify_all()  # release pending updates
        return self.insert(combo)


class FlowConstant(Stream):
    "ensure stable value level"

    system_timer = SystemWheelTimer.instance()
    timer_entry:TimerEntry = None  # pending insert
    timeout:int = None  # silence period, millis

    use_run:bool = False  # use start/stop
    has_run:bool = False  # start/stop state

    def __init__(self, **kwargs):
        self.use_run = kwargs.pop('use_run', False)
        self.timeout = kwargs.pop('timeout')
        super().__init__(**kwargs)

    @override
    def reset(self) -> None:
        if self.timer_entry:
            self.timer_entry.issue_cancel()
            self.timer_entry = None

    @override
    def start(self) -> None:
        self.reset()
        self.has_run = True

    @override
    def stop(self) -> None:
        self.reset()
        self.has_run = False

    @override
    def update(self, value:Any, source:Stream=None) -> None:
        "schedule insert after a window of silence"
        if self.use_run and not self.has_run:
            return
        self.reset()
        value = self.function(value, **self.params)
        insert_value = lambda : self.insert(value)
        self.timer_entry = self.system_timer.schedule_single(
            timer_task=insert_value, delay_milli=self.timeout,
        )


class WaveData:
    "single wavelet level"

    entry_list:collections.deque[float]  # average
    delta_list:collections.deque[float]  # difference

    value:float  # past value

    def __init__(self, maxlen:int):
        self.entry_list = collections.deque(maxlen=maxlen)
        self.delta_list = collections.deque(maxlen=maxlen)
        self.value = None

    def reset(self) -> None:
        self.entry_list.clear()
        self.delta_list.clear()

    def length(self) -> int:
        return len(self.entry_list)

    def update(self, value:float) -> float:
        "apply filter bank calculation"
        if value is None:
            return None
        if self.value is None:
            self.value = value
            return None
        entry = (value + self.value) / 2
        delta = (value - self.value)
        self.value = None
        self.entry_list.append(entry)
        self.delta_list.append(delta)
        return entry


class FlowWavelet(Stream):
    "signal wavelet decomposition"

    value_store:Mapping[int, WaveData]

    def __init__(self, **kwargs):
        self.depth = kwargs.pop('depth', 4)
        self.length = kwargs.pop('length', 512)
        assert self.depth >= 1, f"need depth>=1: {self.depth}"
        assert self.length >= 8, f"need length>=8: {self.length}"
        super().__init__(**kwargs)
        self.value_store = dict()
        for level in range(self.depth):
            block = 2 ** level
            length = int(self.length / block)
            self.value_store[level] = WaveData(length)

    def resolve_index(self, index:int=None) -> int:
        if index is None:
            return self.depth - 1
        else:
            return index

    def entry_list(self, index:int=None) -> List[float]:
        index = self.resolve_index(index)
        return self.value_store[index].entry_list

    def delta_list(self, index:int=None) -> List[float]:
        index = self.resolve_index(index)
        return self.value_store[index].delta_list

    @override
    def update(self, value:Any, source:Stream=None) -> Any:
        "produce signal decomposition"
        entry = self.function(value, **self.params)
        for level in range(self.depth):
            value_store = self.value_store[level]
            entry = value_store.update(entry)
            if entry is None:
                break
        if entry is not None:
            return self.insert(entry)  # slowest average


class Signal:
    "function measure support"

    @staticmethod
    def revalue(signal:numpy.array) -> numpy.array:
        "place signal into 0...1 value range"
        signal_lower = signal.min()
        signal_upper = signal.max()
        signal_range = signal_upper - signal_lower
        if signal_range == 0:
            return signal
        return (signal - signal_lower) / signal_range

    @staticmethod
    def resample(signal:numpy.array, size:int, kind:str='linear') -> numpy.array:
        "contract/expand signal into given length"
        if signal.size == size:
            return signal
        inter_func = interpolate.interp1d(numpy.linspace(0, 1, signal.size), signal, kind)
        return inter_func(numpy.linspace(0, 1, size))

    @staticmethod
    def distance(sig_one:numpy.array, sig_two:numpy.array) -> float:
        "measure distance between signals"
        assert sig_one.size == sig_two.size, f"need same size: {sig_one} vs {sig_two}"
        delta = numpy.abs(sig_one - sig_two)  # point manhattan
        distance = numpy.sum(delta) / sig_one.size
        return distance

    @staticmethod
    def distance2(sig_one:numpy.array, sig_two:numpy.array) -> float:
        "measure distance between signals"  # TODO
        assert sig_one.size == sig_two.size, f"need same size: {sig_one} vs {sig_two}"
        delta = numpy.abs(sig_one - sig_two)  # point manhattan
        value = 0.5 * numpy.abs(sig_one + sig_two)  # point average
        outer = numpy.zeros(sig_one.size)
        ratio = numpy.divide(delta, value, out=outer, where=value != 0)
        distance = numpy.sum(ratio) / sig_one.size  # normalized proportional manhattan
        return distance


class FlowPattern(Stream):
    "signal pattern detector"

    minlen:int  # shortest pattern to test
    maxlen:int  # buffer queue upper boundary

    signal:numpy.array  # reference function
    buffer:collections.deque  # measured function

    def __init__(self, **kwargs):
        signal = kwargs.pop('signal')
        self.minlen = kwargs.pop('minlen')
        self.maxlen = kwargs.pop('maxlen')
        super().__init__(**kwargs)
        self.signal = self.normal(signal)
        self.buffer = collections.deque(maxlen=self.maxlen)

    def normal(self, buffer:List[float]) -> numpy.array:
        "provide proper signal representation"
        signal = numpy.array(buffer)  # proper form
        signal = Signal.revalue(signal=signal)  # vertical norm
        signal = Signal.resample(signal=signal, size=self.maxlen)  # horizontal norm
        return signal

    @override
    def reset(self) -> None:
        self.buffer.clear()

    @override
    def update(self, value:Any, source:Stream=None) -> Any:
        "produce distance between measured and reference signal"
        value = self.function(value, **self.params)
        self.buffer.append(value)
        if len(self.buffer) < self.minlen:
            return None
        signal = self.normal(self.buffer)
        distance = Signal.distance(sig_one=signal, sig_two=self.signal)
        return self.insert(distance)
