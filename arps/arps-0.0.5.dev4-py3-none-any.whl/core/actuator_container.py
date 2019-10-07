import logging

from arps.core.touchpoint import Actuator
from arps.core.touchpoint_container import TouchPointContainer

class ActuatorContainer(TouchPointContainer):
    '''
    Class that offers an interface to read and control actuators
    '''

    def __init__(self, actuators):
        '''
        Arguments:
        - actuators : list containing instances from Actuator class
        '''
        super().__init__(actuators, Actuator)
        self.logger = logging.getLogger(self.__class__.__name__)
        self.logger.debug(
            'Creating interface to manipulate the following actuators: {}'.format(
                self._touchpoints))

    def set(self, actuator_category, **actuator_attributes):
        '''
        Modify touchpoint using named parameters

        Arguments:
        - actuator_category : category belonging to ActuatorType class
        - actuator_attributes : attributes from actuator. See Actuator class to check required parameters
        '''
        assert actuator_category in self._touchpoints
        self.logger.debug('Modifying actuator: %s attributes %s',
                          actuator_category, actuator_attributes)
        self._touchpoints[actuator_category].set(**actuator_attributes)
