import logging

from arps.core.abstract_resource import AbstractResource
from arps.core.simulator.resource import (TrackedValue,
                                          EvtType)


class TouchPoint:
    '''
    Base class that represents a touchpoint

    It offers a method to read the current touchpoint's state
    '''

    def __init__(self, resource: AbstractResource):
        '''
        Initializes the class setting its resource

        Args:
        - resource: resource to be read or set
        '''
        self.logger = logging.getLogger(self.__class__.__name__)

        self._resource = resource
        self.logger.debug(f'TouchPoint created, type: {self.resource_name}')

    def read(self):
        '''
        Returns the content of the touchpoint
        Do not assume any format, it can be str or a dict for example
        '''
        return self._resource.value

    @property
    def resource(self):
        return self._resource

    @property
    def resource_name(self):
        return self._resource.__class__.__name__

    def __repr__(self):
        return f'{self.__class__.__name__}({self.resource})'


class Sensor(TouchPoint):
    '''
    Base class for sensor
    '''


class Actuator(TouchPoint):
    '''
    Base class for actuator
    '''

    def set(self, **parameters):
        '''
        Modifies the actuator state

        Args:
        - parameters: keyword arguments. Expected value, epoch, and identifier of who is modifying
        '''

        tracked_value = TrackedValue(parameters['value'], parameters['epoch'],
                                     parameters['identifier'], EvtType.mas)
        self._set(tracked_value)

    def _set(self, tracked_value: TrackedValue):
        '''
        Just set the current resource state

        This method can be inherited if more elaborated assignment need be done
        '''
        self.resource.value = tracked_value
