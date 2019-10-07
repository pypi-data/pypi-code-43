import logging
from typing import Union
from random import randrange

from arps.core.simulator.simulator import SimEvent, SimTask
from arps.core.simulator.resource import (TrackedValue,
                                          EvtType)
from arps.core.resources_table import ResourcesTable
from arps.core.simulator.estimators_table import EstimatorsTable
from arps.core.simulator.event_factory import EventFactory

from arps.test_resources.dummies.dummy_estimators import dummy_main_estimator, dummy_pos_estimator

estimators_table = EstimatorsTable()
estimators_table.add_estimator(0, 'main_estimate', dummy_main_estimator)
estimators_table.add_estimator(0, 'pos_estimate', dummy_pos_estimator)


class DummyTask(SimTask):
    def __init__(self, identifier, resources_table: ResourcesTable,
                 estimators_table: EstimatorsTable, modifier: int) -> None:
        self.modifier = modifier
        self.original = modifier
        self.is_resource_modified = False
        super().__init__(identifier, resources_table=resources_table,
                         estimators_table=estimators_table)
        self.logger = logging.getLogger(self.__class__.__name__)

    def main_task(self, epoch):
        if not self.is_resource_modified:
            categories = self.resources_table.categories(environment=0)
            resource = categories.resource_by_identifier('DR1')
            try:
                resource.value = TrackedValue(estimators_table[0].main_estimate(resource.value, self.modifier),
                                              epoch, self.identifier, EvtType.des_main)
                self.is_resource_modified = True
            except ValueError as err:
                self.logger.warn(f'Error while modifying resource: {err}')
        return True

    def pos(self, epoch):
        categories = self.resources_table.categories(environment=0)
        resource = categories.resource_by_identifier('DR1')
        resource.value = TrackedValue(estimators_table[0].pos_estimate(resource.value, self.modifier),
                                      epoch, self.identifier, EvtType.des_pos)


class DummyEventFactory(EventFactory):
    def __call__(self, identifier: Union[str, int], arrival_time: Union[str, int],
                 remaining_time: Union[str, int], modifier: Union[str, int]) -> SimEvent:
        '''
        Parse an entry from a file.

        Args:
        - line: a line containing 4 items, an identifier, arrival time, remaining_time, and op_value (the value that will change the resource)
        '''

        return SimEvent(arrival_time=int(arrival_time),
                        remaining_time=int(remaining_time),
                        task=DummyTask(int(identifier), self.resources_table,
                                       self.estimators_table, int(modifier)))


class DummyEventParamsGenerator:

    def __init__(self) -> None:
        self.arrival_time = 1
        self.task_id = 0

    def __call__(self):
        self.arrival_time += randrange(0, 4)
        self.task_id += 1
        remaining_time = randrange(1, 3)
        modifier = randrange(1, 30)
        return self.task_id, self.arrival_time, remaining_time, modifier
