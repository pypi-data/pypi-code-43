import logging
from itertools import (takewhile,
                       islice,
                       tee)
import asyncio
from typing import List

from arps.core.clock import Clock, EpochTime
from arps.core.resources_table import ResourcesTable
from arps.core.simulator.estimators_table import EstimatorsTable


class SimTask:
    '''
    Class that represents a task to be executed during the simulation
    '''

    def __init__(self, identifier, *, resources_table: ResourcesTable = None,
                 estimators_table: EstimatorsTable = None) -> None:
        '''
        Args
        - identifier : unique identifier
        - resources_table: a table containing available resources to be modified.
        - estimators_table: a table containing available estimators to modify resources.
        '''
        self.identifier = identifier
        self.resources_table = resources_table
        self.estimators_table = estimators_table

    def main_task(self, epoch: EpochTime) -> bool:
        '''
        This method is executed every tick

        Args:
        - epoch: the current epoch when the main_task is executed
        '''
        return True

    def pos(self, epoch : EpochTime) -> None:
        '''
        This method is executed after the task is finished

        Args:
        - epoch: the current epoch when the main_task is executed
        '''


class SimEvent:
    '''
    Class that represents simulations event
    '''

    def __init__(self, *, arrival_time: int, remaining_time: int, task) -> None:
        '''
        Initializes event arrival time, remaining time, and task to be performed

        Args:
        - arrival_time : event arrival time on the system
        - remaining_time : how many cycles til finishes executions
        - task : simulation task (SimTask instance)
        '''
        assert isinstance(arrival_time, int) and isinstance(remaining_time, int)
        self._arrival_time = arrival_time
        self._task = task
        self._original_remaining_time = remaining_time
        self._remaining_time = remaining_time
        self.logger = logging.getLogger(SimEvent.__name__)

    @property
    def arrival_time(self):
        '''
        Returns event arrival time
        '''
        return self._arrival_time

    def process(self, epoch):
        '''
        Executes task

        Args:
        - param : task dependent parameter
        - epoch : current epoch
        '''
        self.logger.debug('Processing task %s', self._task.identifier)
        if self._task.main_task(epoch):
            self.logger.debug('Consume task %s', self._task.identifier)
            self._consume()

    def _consume(self):
        '''
        Consume task while there are operations to be performed by it
        '''
        if not self.finished:
            self._remaining_time -= 1


    def pos(self, epoch):
        '''
        Executes pos if task is finished

        Args:
        - param : task dependent parameter
        - epoch : current epoch
        '''
        if self.finished:
            self._task.pos(epoch)

    @property
    def finished(self):
        '''
        Return True if taks is finished, False otherwise
        '''
        return self._remaining_time == 0

    def reset(self):
        '''
        Reset the event but does not undo the possible modifications done by the task
        '''
        self._remaining_time = self._original_remaining_time

    def __str__(self):
        return '(Arrival Time {}, Remaining Time {}, Taks {})'.format(self.arrival_time, self._remaining_time, self._task.identifier)


class Simulator:
    '''
    Discrete event simulator
    '''

    def __init__(self, event_queue, clock: Clock) -> None:
        '''
        Args:
        - event_queue : event queue, not format defined yet
        - clock : instance of Clock
        '''
        self._clock = clock
        self._finished = asyncio.Event()
        self._event_queue = event_queue
        self._event_gen = self._event_queue()
        self._current_events: List[SimEvent] = list()
        self.logger = logging.getLogger(Simulator.__name__)

    @property
    def has_events(self):
        return not self._finished.is_set()

    @has_events.setter
    def has_events(self, stil_running):
        if not stil_running:
            self._finished.set()

    def step(self, time_event):
        '''
        Process events that are in the current epoch. Only process events if the epoch
        changed

        Return if there are more events in the event queue
        '''

        current_time = time_event.value
        self.logger.debug('running step at epoch time %s', current_time)
        events, self._event_gen, events_available = self.next_events(self._event_gen, current_time)
        self._current_events.extend(events)

        finalized_events = [
            event for event in self._current_events if event.finished]

        for event in finalized_events:
            event.pos(current_time)

        self._current_events = [
            event for event in self._current_events if not event.finished]

        for event in self._current_events:
            self.logger.debug('processing events at epoch time %s', current_time)
            event.process(current_time)

        self.has_events = events_available or len(self._current_events) > 0

    def reset(self):
        '''
        Reset simulator attributes needed to run simulator from scratch

        '''
        self._event_gen = self._event_queue()

        self._finished.clear()

    def next_events(self, events_gen, current_time):
        '''
        Returns events that arrived at the current epoch,
        if there are more events, and updated generator of events

        Args:
        - events_gen: current generator of events
        '''
        current_events_it, next_event_it, has_next_it = tee(events_gen, 3)
        current_event_predicate = lambda event: event.arrival_time == current_time
        current_events = list(takewhile(current_event_predicate, current_events_it))
        event_gen = islice(next_event_it, len(current_events), None)
        has_more = True
        try:
            next(has_next_it)
        except StopIteration:
            has_more = False

        return current_events, event_gen, has_more
