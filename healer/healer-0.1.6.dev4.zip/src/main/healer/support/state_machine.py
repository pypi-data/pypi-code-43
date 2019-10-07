"""
Enum based finate state machine
"""

from __future__ import annotations

import enum
import functools
import inspect
import logging
import traceback
from builtins import isinstance
from collections import defaultdict
from dataclasses import dataclass
from types import FunctionType
from typing import Any
from typing import List
from typing import Mapping
from typing import Type

from healer.support.typing import render_error_trace
from healer.support.wheel_timer import SystemWheelTimer
from healer.support.wheel_timer import TimerEntry
from healer.support.wheel_timer import WheelTimer

logger = logging.getLogger(__name__)


class ArkonEnum(enum.Enum):
    """
    Enum where name=value
    """

    @staticmethod
    def _generate_next_value_(name, *_):
        return name

    def __repr__(self):
        return self.name


class EventEnum(ArkonEnum):
    """
    Base type for FSM events
    """

    def when_any(self, state_class:Type[StateEnum]) -> EventSource:
        assert issubclass(state_class, StateEnum), f"Wrong source type: {state_class}"
        return self.when(*list(state_class))

    def when_not(self, *source:StateEnum) -> EventSource:
        total_list = list(type(source[0]))
        removed_list = list(source)
        selected_list = [item for item in total_list if item not in removed_list]
        return self.when(*selected_list)

    def when(self, *source:StateEnum) -> EventSource:
        source_list = list(source)
        for source in source_list:
            assert isinstance(source, StateEnum), f"Wrong source type: {source}"
        return EventSource(self, source_list)


class StateEnum(ArkonEnum):
    """
    Base type for FSM states
    """


@dataclass
class EventSource():
    """
    transition builder
    """
    event:EventEnum
    source:List[StateEnum]

    def then(self, target:StateEnum, failure:StateEnum=None) -> EventSourceTarget:
        assert isinstance(target, StateEnum), f"Wrong target type: {target}"
        if failure:
            assert isinstance(failure, StateEnum), f"Wrong failure type: {failure}"
        return EventSourceTarget(self.event, self.source, target, failure)


@dataclass
class EventSourceTarget():
    """
    transition builder
    """
    event:EventEnum
    source:List[StateEnum]
    target:StateEnum
    failure:StateEnum

    def invoke(self, method:FunctionType) -> None:
        assert inspect.isfunction(method), f"Wrong method type: {method}"
        invoke_entry = InvokeEntry(
            self.event,
            self.source,
            self.target,
            self.failure,
            method,
        )
        MachineSupport.register_invoke(invoke_entry)


@dataclass
class InvokeEntry():
    """
    transition builder
    """
    event:EventEnum
    source:List[StateEnum]
    target:StateEnum
    failure:StateEnum
    method:FunctionType


@dataclass
class TransitionTable():
    """
    Machine state transition sparse matrix
    """

    # state -> event -> action
    state_mapper:Mapping[StateEnum, Mapping[EventEnum, InvokeEntry]]

    def find_entry(self, state:StateEnum, event:EventEnum) -> InvokeEntry:
        event_mapper = self.state_mapper.get(state)
        if event_mapper:
            invoke_entry = event_mapper.get(event)
            if invoke_entry:
                return invoke_entry
        return None


class MachineBase:
    """
    Base type for enum finate state machine
    """

    @classmethod
    def __init_subclass__(cls, **kwargs):
        "track derived state machines"
        super().__init_subclass__(**kwargs)
        MachineSupport.register_machine(cls)

    machine_state:StateEnum
    machine_table:TransitionTable

    machine_wheel_timer:WheelTimer = SystemWheelTimer.instance()
    machine_timeout_entry:TimerEntry = None
    machine_timeout_event:EventEnum = None
    machine_timeout_time_secs:int = None

    def __init__(self, state:StateEnum, **kwargs):
        super().__init__(**kwargs)
        assert isinstance(state, StateEnum), f"wrong state type: {state}"
        self.machine_state = state
        self.machine_table = MachineSupport.produce_table(type(self), type(state))

    def machine_config_timeout(self, event:EventEnum=None, time_secs:int=30) -> None:
        "setup post machine_fire_event timeout timer task"
        self.machine_cancel_timeout_task()
        if event:
            assert isinstance(event, EventEnum), f"wrong event type: {event}"
            assert time_secs > 0, f"wrong time_secs: {time_secs}"
            self.machine_timeout_event = event
            self.machine_timeout_time_secs = time_secs
        else:
            self.machine_timeout_event = None
            self.machine_timeout_time_secs = None

    def machine_fire_timeout_event(self):
        if self.machine_timeout_event:
            self.machine_fire_event(self.machine_timeout_event)

    def machine_cancel_timeout_task(self):
        if self.machine_timeout_entry:
            self.machine_timeout_entry.issue_cancel()
            self.machine_timeout_entry = None

    def machine_restart_timeout_task(self):
        self.machine_cancel_timeout_task()
        if self.machine_timeout_event:
            self.machine_timeout_entry = self.machine_wheel_timer.schedule_single(
                self.machine_fire_timeout_event, self.machine_timeout_time_secs * 1000,
            )

    def machine_fire_event(self, event:EventEnum) -> Any:
        logger.debug(f"@ {self}: {event}")
        assert self.machine_table, f"need __init__()"
        assert isinstance(event, EventEnum), f"wrong event type: {event}"
        invoke_entry = self.machine_table.find_entry(self.machine_state, event)
        if invoke_entry:
            try:
                # remove timeout timer
                self.machine_cancel_timeout_task()
                # invoke event reactor
                return self.machine_invoke_entry(invoke_entry)
            finally:
                # resume timeout timer, expected to be cleared by the next event
                self.machine_restart_timeout_task()
        else:
            return self.machine_react_invalid_event(event)

    def machine_invoke_entry(self, invoke_entry:InvokeEntry) -> Any:
        try:
            result = invoke_entry.method(self)
            self.machine_state = invoke_entry.target
            return result
        except Exception as error:
            if invoke_entry.failure:
                self.machine_state = invoke_entry.failure
            else:
                self.machine_react_invoke_error(invoke_entry.event, error)
            return None

    def machine_react_invoke_error(self, event:EventEnum, error:Exception) -> Any:
        "react when proper transition failed during execution"
        tracer = render_error_trace(error)
        logger.error(f"@ {self}: {event}: {error}: {tracer}")

    def machine_react_invalid_event(self, event:EventEnum) -> Any:
        "react when transition table has no state->event definition"
        logger.debug(f"@ {self}: {event}")


class MachineSupport:
    """
    """

    machine_type_list:List[Type[MachineBase]] = list()

    invoke_entry_list:List[InvokeEntry] = list()

    @staticmethod
    def method_list(machine_type:Type[MachineBase]) -> List[FunctionType]:
        return [
            value for key, value in machine_type.__dict__.items()
            if type(value) == FunctionType
        ]

    @staticmethod
    @functools.lru_cache()
    def produce_table(machine_type:Type[MachineBase], state_type:Type[StateEnum]) -> TransitionTable:
        table_maker = defaultdict(dict)
        method_dict = MachineSupport.method_list(machine_type)
        for invoke_entry in MachineSupport.invoke_entry_list:
            for method in method_dict:
                if invoke_entry.method == method:
                    target = invoke_entry.target
                    if target:
                        assert isinstance(target, state_type), f"wrong target type: {target}"
                    failure = invoke_entry.failure
                    if failure:
                        assert isinstance(failure, state_type), f"wrong failure type: {failure}"
                    for source in invoke_entry.source:
                        assert isinstance(source, state_type), f"wrong source type: {source}"
                        table_maker[source][invoke_entry.event] = invoke_entry
        table = dict(table_maker)
        return TransitionTable(table)

    @staticmethod
    def register_machine(machine_type:Type[MachineBase]):
        assert not machine_type in MachineSupport.machine_type_list, f"need unique: {machine_type}"
        MachineSupport.machine_type_list.append(machine_type)

    @staticmethod
    def register_invoke(invoke_entry: InvokeEntry) -> None:
        assert not invoke_entry in MachineSupport.invoke_entry_list, f"need unique: {invoke_entry}"
        MachineSupport.invoke_entry_list.append(invoke_entry)

    @staticmethod
    def member_type(outer_type:Type, inner_type:Type) -> Type:
        member_type_list = [
            entry for entry in outer_type.__dict__.values()
            if inspect.isclass(entry) and issubclass(entry, inner_type)
        ]
        assert len(member_type_list) == 1, f"{outer_type} need solo {inner_type}"
        return member_type_list[0]
