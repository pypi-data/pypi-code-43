from arps.core.touchpoint import Sensor
from arps.core.touchpoint import Actuator
from arps.test_resources.dummies.dummy_resource import ResourceA, ResourceB

class SensorA(Sensor):

    _category = 'SensorA'

    def __init__(self, resource=None):
        resource = resource or ResourceA(environment_identifier=0, identifier='ForSensorA', value=10)
        super().__init__(resource)

    def __repr__(self):
        return 'Sensor A on resource {}'.format(self.resource)


class SensorB(Sensor):

    _category = 'SensorB'

    def __init__(self, resource=None):
        resource = resource or ResourceB(environment_identifier=0, identifier='ForSensorB', value='ON')
        super().__init__(resource)

    def __repr__(self):
        return 'Sensor B on resource {}'.format(self.resource)


class ActuatorA(Actuator):

    _category = 'ActuatorA'

    def __init__(self, resource=None):
        resource = resource or ResourceA(environment_identifier=0, identifier='ForActuatorA', value=0)
        super().__init__(resource)

    def __repr__(self):
        return 'Actuator A on resource {}'.format(self.resource)

class ActuatorB(Actuator):

    _category = 'ActuatorB'

    def __init__(self, resource=None):
        resource = resource or ResourceB(environment_identifier=0, identifier='ForActuatorB', value="ON")
        super().__init__(resource)

    def __repr__(self):
        return 'Actuator B on resource {}'.format(self.resource)
