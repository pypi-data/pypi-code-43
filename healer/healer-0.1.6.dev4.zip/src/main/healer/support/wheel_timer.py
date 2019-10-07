"""
Hashed wheel timer
"""

from __future__ import annotations

import abc
import logging
import threading
import time
from dataclasses import dataclass
from dataclasses import field
from queue import Queue
from typing import Callable
from typing import Tuple

from healer.support.typing import render_error_trace

logger = logging.getLogger(__name__)


class TimerClock:
    "timer clock interface"

    def nano_time(self) -> int:
        return time.time_ns()


class TimerSupport:
    "timer support operations"

    DEFAULT_RESOLUTION = 10  # time tick, millis
    DEFAULT_WHEEL_SIZE = 100  # time tick entries, number
    DEFAULT_JOIN_TIME = 1.0  # time to join worker theads, seconds

    @staticmethod
    def milli_to_micro(time_milli:int) -> int:
        return time_milli * 1000

    @staticmethod
    def milli_to_nano(time_milli:int) -> int:
        return time_milli * 1000000

    @staticmethod
    def terminate_thread(thread:threading.Thread, join_time:int) -> int:
        try:
            thread.join(join_time)
            return 1
        except:
            logger.warning(f"join failure: {thread}")
            return 0


@dataclass
class TimerEntry(abc.ABC):
    "base type for a timer tracker"

    is_cancelled:bool = field(init=False, default=False)  # user cancel status

    is_started:bool = field(init=False, default=False)  # worker process status
    is_finished:bool = field(init=False, default=False)  # worker process status
    is_exception:bool = field(init=False, default=False)  # worker process status

    timer_task:Callable  # assigned runnable function

    wheel_count:int  # pending wheel rounds
    wheel_index:int  # bucket address on the wheel

    @property
    def task_name(self) -> str:
        "extract attached function name"
        return self.timer_task.__name__

    @property
    def has_cancel(self) -> bool:
        "verify timer cancelation status"
        return self.is_cancelled

    @property
    def has_start(self) -> bool:
        "verify if worker started timer task"
        return self.is_started

    @property
    def has_finish(self) -> bool:
        "verify if timer task invocation was a success"
        return self.is_finished

    @property
    def has_exeception(self) -> bool:
        "verify if timer task invocation was a failure"
        return self.is_exception

    @property
    def has_trigger(self) -> bool:
        "check if timer is ready for traworker"
        return self.wheel_count <= 0

    def issue_cancel(self) -> None:
        "user timer terminate command, removes timer from wheel"
        self.is_cancelled = True

    def wheel_apply_round(self) -> None:
        "decrement timer wheel round count, used only by wheel"
        self.wheel_count -= 1

    @abc.abstractmethod
    def wheel_produce_next(self) -> TimerEntry:
        "optionally allow to produce timer chain, used only by wheel"


@dataclass
class TimerSingleEntry(TimerEntry):
    "one-shot timer, trigger once after a delay"

    def wheel_produce_next(self) -> TimerEntry:
        "one-shot timer has no chain"
        return None


@dataclass
class TimerPeriodicEntry(TimerEntry):
    "periodic timer, initiate sequence after a delay"

    period_steps:int  # period duration in ticks
    wheel_size:int = field(repr=False)  # param for remap

    def wheel_produce_next(self) -> TimerEntry:
        "timer chain: generate next position in the wheel"
        self.wheel_count = int(self.period_steps / self.wheel_size)
        self.wheel_index = (self.wheel_index + self.period_steps + 1) % self.wheel_size
        return self


@dataclass
class TimerBucket:
    "entry list with thread safe locking"

    wheel_index:int  # bucket position in the wheel
    entry_lock:threading.Lock = field(init=False, repr=False, default_factory=threading.RLock)
    entry_list:List[TimerEntry] = field(init=False, default_factory=list)


@dataclass
class WheelTimer:
    "hashed wheel timer with clock scaner and task worker"

    wheel_clock:TimerClock = field(default_factory=TimerClock, repr=False)  # timing device
    wheel_tick:int = TimerSupport.DEFAULT_RESOLUTION  # tick duration, millis
    wheel_size:int = TimerSupport.DEFAULT_WHEEL_SIZE  # number of buckets in the wheel
    thread_join_time:int = TimerSupport.DEFAULT_JOIN_TIME  # worker threat termination timeout

    wheel_index:int = field(init=False, repr=False)  # current cursor in the wheel
    state_event:threading.Event = field(init=False, repr=False)  # start/stop lifesize
    bucket_list:List[TimerBucket] = field(init=False, repr=False)  # timer wheel representation
    worker_queue:Queue[TimerEntry] = field(init=False, repr=False)  # scanner/worker timer task queue

    def __post_init__(self):
        self.setup_wheel()

    def setup_wheel(self):
        "configure timer from scratch"
        self.wheel_index = 0  # initial wheel cursor
        self.state_event = None  # must be set by self.start()
        self.bucket_list = [ TimerBucket(index) for index in range(self.wheel_size) ]
        self.worker_queue = Queue()  # unbounded queue

    def setup_thread(self):
        "configure timer threads from scratch"
        self.scaner_thread = threading.Thread(
            name="wheel-timer/scaner", target=self.scaner_task, daemon=True,
        )
        self.worker_thread = threading.Thread(
            name="wheel-timer/worker", target=self.worker_task, daemon=True,
        )

    def scaner_task(self) -> None:
        "wheel watcher thread: manage timer entry expiration"
        logger.debug(f"init @ {self}")
        #
        wheel_tick = TimerSupport.milli_to_nano(self.wheel_tick)
        wheel_time = self.wheel_clock.nano_time()  # wheel time epoch
        #
        while not self.state_event.is_set():
            # expire timers
            self.process_bucket()
            # apply time tick
            wheel_time += wheel_tick  # next deadline
            clock_time = self.wheel_clock.nano_time()  # system time
            sleep_time = wheel_time - clock_time  # time to sleep till deadline
            if sleep_time > 0:  # slow scanner vs fast system time overrun protecton
                sleep_secs = sleep_time / 1000000000.0  # from nano time
                time.sleep(sleep_secs)
            # move cusor around
            self.update_cursor()

    def update_cursor(self) -> None:
        "rotate bucket index"  # the only place to update the cursor
        self.wheel_index = (self.wheel_index + 1) % self.wheel_size

    def process_bucket(self) -> None:
        "process pending timers"
        bucket = self.bucket_list[self.wheel_index]
        entry_list = bucket.entry_list
        if not entry_list:
            return
        with bucket.entry_lock:
            create_list = list()  # timer entires to re-schedule
            delete_list = list()  # timer entries to remove from wheel
            for timer_entry in entry_list:
                if timer_entry.has_cancel:  # only delete
                    delete_list.append(timer_entry)
                elif timer_entry.has_trigger:  # optionally create
                    delete_list.append(timer_entry)
                    self.worker_queue.put(timer_entry, block=False)
                    timer_entry_next = timer_entry.wheel_produce_next()  # timer chain
                    if timer_entry_next:
                        create_list.append(timer_entry_next)
                else:
                    timer_entry.wheel_apply_round()
            for timer_entry in delete_list:  # delete first
                entry_list.remove(timer_entry)
            for timer_entry in create_list:  # create second
                self.schedule_entry(timer_entry)

    def worker_task(self) -> None:
        "queue worker thread: execute timer entry tasks"
        logger.debug(f"init @ {self}")
        #
        while not self.state_event.is_set():
            timer_entry = self.worker_queue.get(block=True)  # wait for task
            if timer_entry.has_cancel:
                continue
            try:
                timer_entry.is_started = True
                timer_entry.is_finished = False
                timer_entry.is_exception = False
                #
                timer_entry.timer_task()  # invoke proper
                #
                timer_entry.is_finished = True
            except Exception as error:
                timer_entry.is_exception = True
                tracer = render_error_trace(error, limit=5)
                logger.error(f"task: {timer_entry.task_name} error: {tracer}")
                time.sleep(0.1)  # throttle error spin

    def start(self) -> None:
        "initiate timer threads"
        if self.state_event is None:
            logger.debug(f"@ {self}")
            self.state_event = threading.Event()
            self.setup_thread()
            self.scaner_thread.start()
            self.worker_thread.start()

    def stop(self) -> None:
        "terminate timer threads"
        if self.state_event and not self.state_event.is_set():
            logger.debug(f"@ {self}")
            self.state_event.set()
            terminate_count = 0
            terminate_count += TimerSupport.terminate_thread(self.scaner_thread, self.thread_join_time)
            terminate_count += TimerSupport.terminate_thread(self.worker_thread, self.thread_join_time)
            if terminate_count == 2:
                self.state_event = None
                self.scaner_thread = None
                self.worker_thread = None

    def schedule_entry(self, timer_entry:TimerEntry) -> None:
        "register timer task into wheel bucket"
        bucket = self.bucket_list[timer_entry.wheel_index]
        with bucket.entry_lock:
            bucket.entry_list.append(timer_entry)

    def resolve_delay(self, delay_milli:int) -> Tuple[int, int]:
        "resolve user delay into wheel count and wheel index"
        assert delay_milli > self.wheel_tick, f"too small delay: {delay_milli}"
        delay_steps = int(delay_milli / self.wheel_tick)
        wheel_count = int(delay_steps / self.wheel_size)
        wheel_index = (self.wheel_index + delay_steps + 1) % self.wheel_size
        return (wheel_count, wheel_index)

    def schedule_single(self,
            # invoke this task after a delay
            timer_task:Callable,
            # task delay, milliseconds
            delay_milli:int=1000,
        ) -> TimerEntry:
        "register one-shot task with timer wheel"
        wheel_count, wheel_index = self.resolve_delay(delay_milli)
        timer_entry = TimerSingleEntry(
            timer_task=timer_task,
            wheel_index=wheel_index, wheel_count=wheel_count,
        )
        self.schedule_entry(timer_entry)
        return timer_entry

    def resolve_period(self, period_milli:int) -> Tuple[int, int]:
        "resolve user period into wheel tick steps"
        assert period_milli > self.wheel_tick, f"too small period: {period_milli}"
        period_steps = int(period_milli / self.wheel_tick)
        return (period_steps, None)

    def schedule_periodic(self,
            # invoke this task after a delay, then invoke periodically
            timer_task:Callable,
            # initial task delay, milliseconds
            delay_milli:int=1000,
            # following task period, milliseconds
            period_milli:int=1000,
        ) -> TimerEntry:
        "register periodic task with timer wheel"
        wheel_count, wheel_index = self.resolve_delay(delay_milli)
        period_steps, _ = self.resolve_period(period_milli)
        timer_entry = TimerPeriodicEntry(
            timer_task=timer_task,
            wheel_index=wheel_index, wheel_count=wheel_count,
            period_steps=period_steps, wheel_size=self.wheel_size,
        )
        self.schedule_entry(timer_entry)
        return timer_entry


class SystemWheelTimer:
    "global shared timer instance"

    instance_lock:threading.Lock = threading.RLock()
    instance_value:WheelTimer = None

    @staticmethod
    def instance() -> WheelTimer:
        "global shared timer instance"
        with SystemWheelTimer.instance_lock:
            if not SystemWheelTimer.instance_value:
                SystemWheelTimer.instance_value = WheelTimer(wheel_tick=100, wheel_size=20)
                SystemWheelTimer.instance_value.start()
            return SystemWheelTimer.instance_value
