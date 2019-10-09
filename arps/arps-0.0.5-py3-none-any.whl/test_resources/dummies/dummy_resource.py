from enum import unique
import uuid

from arps.core.simulator.resource import (Resource,
                                          TrackedValue,
                                          EvtType)
from arps.core.resource_category import ResourceCategory, ValueType


@unique
class DummyCategory(ResourceCategory):
    Range = (uuid.uuid1(), (0, 100), ValueType.int)
    Togglable = (uuid.uuid1(), ('ON', 'OFF'), ValueType.descriptive)
    Counter = (uuid.uuid1(), (0, float('inf')), ValueType.int)
    Any = (uuid.uuid1(), None, ValueType.complex)


class ResourceA(Resource):

    def __init__(self, *, environment_identifier, identifier, value=None):
        super().__init__(environment_identifier=environment_identifier,
                         identifier=identifier, value=value, category=DummyCategory.Range)

    def _affect_resource(self, epoch):
        if not self._affected_resource:
            return

        new_value = 'ON' if self.value > 60 else 'OFF'
        if self._affected_resource.value == new_value:
            return

        self._affected_resource.value = TrackedValue(new_value,
                                                     epoch,
                                                     self.identifier,
                                                     EvtType.rsc_indirect)


class ResourceB(Resource):

    def __init__(self, *, environment_identifier, identifier, value=None):
        super().__init__(environment_identifier=environment_identifier,
                         identifier=identifier, value=value, category=DummyCategory.Togglable)

class ResourceC(Resource):

    def __init__(self, *, environment_identifier, identifier, value=None):
        super().__init__(environment_identifier=environment_identifier,
                         identifier=identifier, value=value, category=DummyCategory.Range)


class ReceivedMessagesResource(Resource):

    def __init__(self, *, environment_identifier, identifier):
        super().__init__(environment_identifier=environment_identifier,
                         identifier=identifier, value=0,
                         category=DummyCategory.Counter)

    def __repr__(self):
        return f'ReceivedMessagesResource({self.identifier})'
