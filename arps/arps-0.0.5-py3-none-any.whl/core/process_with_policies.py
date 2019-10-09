import sys
import asyncio
from functools import partial, update_wrapper
import logging
from typing import List
from collections import deque

from arps.core.clock import Clock
from arps.core.policy import (ActionType,
                              ReflexPolicy,
                              PeriodicPolicy)
from arps.core.payload_factory import (Payload,
                                       create_periodic_action)


class ProcessWithPolicies:

    def __init__(self, policies=None, epoch_time=None):
        '''
        Initializes process that deal with policies

        Keyword Args:
        - policies: list of policies that will be used to evaluate received events
        - epoch_time: epoch time to provide info when an event was processed
        '''
        self._policies = policies or list()
        self._epoch_time = epoch_time
        self._events_received: List[Payload] = list()
        self.policy_action_results = deque(maxlen=50)
        self.logger = logging.getLogger(self.__class__.__name__)
        self.host = None

    def receive(self, event: Payload):
        '''
        Receive event to be added into the event loop

        Keyword parameters:
        - event : event received in PayloadFactory message format

        '''
        assert self.host
        self.logger.info('event received %s by agent %s', event, self.host.identifier)

        self._events_received.append(event)

    def add_policy(self, policy: ReflexPolicy):
        '''
        Append policy into current policies

        Args:
        - policy: policy instance
        '''
        if self.host:
            self.host.update_touchpoints(
                policy.required_sensors(),
                policy.required_actuators())
        self._policies.append(policy)

    def remove_policy(self, policy_identifier):
        '''
        Removes policy from current policies

        Keyword parameters:
        - policy_identifier: policy's name
        '''

        instance = {
            policy.__class__.__name__: policy for policy in self._policies}
        self._policies.remove(instance[policy_identifier])

    @property
    def policies_name(self):
        return [policy.__class__.__name__ for policy in self._policies]

    def required_sensors(self):
        '''
        Returns required sensors according to the current policies
        '''
        sensors = [policy.required_sensors() for policy in self._policies]
        return sum(sensors, [])

    def required_actuators(self):
        '''
        Returns required actuators according to the current policies
        '''
        actuators = [policy.required_actuators() for policy in self._policies]
        return sum(actuators, [])

    async def run(self):
        '''event to be called by event loop

        Depending on the type of event:
        - an action can be executed
        - a result can be stored to be retrieve later accessing
          policy_action_results
        '''
        policies_result = self._policies_result()
        await self._process_results(policies_result)

    def _policies_result(self):
        '''
        Collect events received and run against current policies

        Returns policies result
        '''
        policies_result = list()

        self.logger.debug(f'checking for events received: {len(self._events_received)}')
        while self._events_received:
            event_received = self._events_received.pop()
            self.logger.debug('Running event %s on: %s', event_received, self._policies)
            policies_result.extend([
                policy.event(
                    event=event_received,
                    host=self.host,
                    epoch=self._epoch_time.epoch) for policy in self._policies])

        return [result for result in policies_result if result]

    async def _process_results(self, policies_result):
        '''
        Process results according to their types

        Event will be execute while an event will be stored
        '''

        while policies_result:
            (action_type, content) = policies_result.pop()
            self.logger.debug('action type to process: {}'.format(action_type.name))

            if action_type == ActionType.event:
                try:
                    self.logger.debug('Content {}'.format(content))
                    if asyncio.iscoroutinefunction(content):
                        await content()
                    elif asyncio.iscoroutine(content):
                        await content
                    else:
                        content()
                    self.logger.debug('action type event executed')
                except GeneratorExit:
                    # ignoring error; should this be done?
                    # I've seen only in tests where this doesn't matter
                    self.logger.error(f'Generator Exit: generator/coroutine was closed while awaiting')
                except Exception as e:
                    self.logger.error('Exception: {}'.format(e))
                    raise e
                except:
                    message = f'Unexpected error: {sys.exc_info()[0]}'
                    raise RuntimeError(message)
                    self.logger.error(message)

            if action_type == ActionType.result:
                self.policy_action_results.append(content)

    def __repr__(self):
        return repr([policy for policy in self._policies])


class ProcessWithEvents(ProcessWithPolicies):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.periodic_events = list()

    def _receive_periodic_events(self, periodic_event, time_event):
        self.logger.debug('Periodic event executed on {}'.format(time_event.value))
        self.periodic_events.append(periodic_event)

    async def run(self):
        for periodic_event in self.periodic_events:
            self.receive(periodic_event)
        self.periodic_events.clear()
        await super().run()


def build_process(policies: List[ReflexPolicy], clock: Clock) -> ProcessWithPolicies:
    '''
    Build process based on its periodicity.

    Args:
    - policies: List containing policies
    - clock: instance of Clock
    '''

    periodic_policies = [policy for policy in policies if isinstance(policy, PeriodicPolicy)]
    if not any(periodic_policies):
        return ProcessWithPolicies(policies=policies, epoch_time=clock.epoch_time)

    process = ProcessWithEvents(policies=policies, epoch_time=clock.epoch_time)

    for policy in periodic_policies:
        periodic_event = create_periodic_action(id(policy))
        receive_periodic_events = partial(process._receive_periodic_events, periodic_event)
        update_wrapper(receive_periodic_events, process._receive_periodic_events)

        clock.add_listener(receive_periodic_events,
                           predicate=lambda event, period=policy.period: event.value % period == 0)

    return process
