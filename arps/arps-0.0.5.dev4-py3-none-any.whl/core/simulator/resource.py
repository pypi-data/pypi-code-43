import asyncio
import copy
import logging
from enum import Enum, auto
from typing import NamedTuple, Any

from arps.core.abstract_resource import AbstractResource
from arps.core.simulator.resource_event import ResourceEvent
from arps.core.observable_mixin import ObservableMixin
from arps.core.resource_category import ResourceCategory


class EvtType(Enum):
    '''enum that contains the actions that can trigger resource modification

    - des_main: the discrete event main_task from SimTask modified the resource
    - des_pos: the discrete event pos from SimTask modified the resource
    - mas: an agent modified the resource
    - rsc_indirect: another resource caused the resource to be modified
    - none: none of the above categories
    '''
    des_main = auto()
    des_pos = auto()
    mas = auto()
    rsc_indirect = auto()
    none = auto()


class TrackedValue(NamedTuple):
    '''
    Class to agreggate parameters of values that represents the current resource state
    and are tracked

    Params:
    - value: the new state the resource will be
    - epoch: when the resource is modified
    - modifier_id: who modified the resource
    - event_type: what kind of event caused the modification
    '''
    value: Any
    epoch: int
    modifier_id: str
    event_type: EvtType


class Resource(AbstractResource, ObservableMixin):
    '''
    Class Resource that represents an abstraction to a resource in the environment

    Listeners can be attached to listen when the resource is modified
    '''

    def __init__(self, *, environment_identifier, identifier,
                 category: ResourceCategory, value=None) -> None:
        '''
        Args:
        - environment_identifier: environment identifier where the resource is available
        - identifier: resource unique identifier within the environment
        - value: value to be read/modified
        - category: what type of resource it is
        '''
        AbstractResource.__init__(self, environment_identifier,
                                  identifier, category)
        self._value = value
        assert self.category.is_valid(value)
        self._original_value = copy.deepcopy(value)
        self._affected_resource = None
        self.logger = logging.getLogger(self.__class__.__name__)

        ObservableMixin.__init__(self)

    def affects(self, affected_resource):
        '''
        Set resource that will be indirected affect by this resource
        '''
        self._affected_resource = affected_resource

    def _affect_resource(self, epoch):
        '''
        Execute process to change affected resource value.
        The behavior is dependent on each implementation

        Args:
        - epoch: when the resource was modified
        '''

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, tracked_value: TrackedValue) -> None:
        '''
        Change value and tracks who and when this value was changed

        Args
        - tracked_value: tuple containing value, epoch, who is modifying the value respectively,
        and what kind of event modified the resource
        '''
        value, epoch, modifier_id, evt_type = tracked_value
        if not self.category.is_valid(value):
            raise ValueError("Value type expected ", self.category.value_type.name,
                             "in range", str(self.category.valid_range))

        self.logger.debug('Setting new resource state to %s', value)
        self._value = value
        assert isinstance(evt_type, EvtType)

        self.logger.debug('Notify resource modification')
        event = ResourceEvent.from_resource(self, epoch, modifier_id, evt_type)
        asyncio.ensure_future(self.notify(event))

        self.logger.debug('Notify affected resource')
        self._affect_resource(epoch)

    def add_listener(self, listen, predicate=None):
        super().add_listener(listen, predicate=lambda event: event.identifier == self.identifier)
        event = ResourceEvent.from_resource(self, 0, str(None), EvtType.none)
        asyncio.ensure_future(self.notify(event))

    def reset(self):
        '''
        Set the resource to its original value
        Remove all listeners
        '''
        self._value = self._original_value
        super().clear()

    def __repr__(self):
        return f'Resource(id={self.identifier}, env={self.environment_identifier}, value={self.value})'
