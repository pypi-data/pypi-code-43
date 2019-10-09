import pathlib
import os
from typing import Callable, Any

from arps.core.simulator.event_factory import EventFactory


class EventQueueLoader:

    def queue(self):
        '''
        Returns a new queue generator
        '''
        return self._load_queue

    def _load_queue(self):
        '''
        Generator to load new events
        '''


class FileEventQueueLoader(EventQueueLoader):
    '''This class loads the queue that will contain events.

    This class assumes that the events are ordered by arrival time.

    '''

    def __init__(self, path: pathlib.Path, event_factory: EventFactory) -> None:
        '''Args:
        - path: where the event queue file is loacated
        - event_factory: instance that builds events based on each entry
          in the event queue file
        '''
        self.path = path
        self.event_factory = event_factory

    def _load_queue(self):
        '''
        Load queue from one or more files
        '''
        if not os.path.getsize(self.path):
            return

        with open(self.path) as event_queue_fh:
            for line in event_queue_fh:
                if not line:
                    continue
                event_params = line.strip('\n').split(' ')
                yield self.event_factory(*event_params)


class RandomEventQueueLoader(EventQueueLoader):

    def __init__(self, event_factory: EventFactory,
                 random_params: Callable[[], Any], limit: int = None) -> None:
        '''
        Args:
        - events_loader: sequence of EventLoader
        - event_factory: instance that builds events based on each entry
          in the event queue file
        '''
        self.limit = limit
        self.event_factory = event_factory
        self.random_params = random_params

    def _load_queue(self):
        '''
        Load queue from one or more files
        '''

        for _ in range(self.limit):
            yield self.event_factory(*self.random_params())
