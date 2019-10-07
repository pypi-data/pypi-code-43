from typing import List, Union

from arps.core.touchpoint import Sensor
from arps.core.touchpoint import Actuator

TouchPoint = Union[Sensor, Actuator]


class TouchPointContainer:

    def __init__(self, touchpoints, touchpoint_cls):
        '''
        Args:
        - touchpoint_cls: class that will be handled by TouchPointContainer derived classes (Sensor or Actuator)
        '''
        self._touchpoint_cls = touchpoint_cls

        if not self._valid(touchpoints):
            raise ValueError(
                'Invalid touchpoints on initialization: {}. Check if touchpoint is a sensor and is place in the correct place inside the configuration file, the sensor section. The same applies to actuators.'.format(touchpoints))
        self._touchpoints = {
            touchpoint.category(): touchpoint for touchpoint in touchpoints}

        self.logger = None

    def _valid(self, touchpoints: List[TouchPoint]) -> bool:
        '''
        Return True if touchpoints is a list of instances of touchpoint_cls class, False otherwise

        Keyword parameters:
        - touchpoints : list containing instances from touchpoint_cls class
        - touchpoint_cls: class expected
        '''
        return (isinstance(touchpoints, list) and all(
            [isinstance(touchpoint, self._touchpoint_cls) for touchpoint in touchpoints]))

    def categories(self) -> List[str]:
        '''
        Returns a list containing all available touchpoints in this class (only Sensor or only Actuator)
        '''
        return list(self._touchpoints.keys())

    def add(self, touchpoints):
        '''
        Add new touchpoint instances

        If sensor.category from touchpoints is already in the list, the list will be updated with the new instance

        Keyword parameters:
        - touchpoints : list containing instances from touchpoint_cls class

        Raises:
        - ValueError if any touchpoint is not a instance of touchpoint_cls class
        '''
        if not self._valid(touchpoints):
            raise ValueError(
                'Invalid touchpoints being added: {}.'.format(touchpoints))

        self._touchpoints.update(
            {touchpoint.category(): touchpoint for touchpoint in touchpoints})

    def read(self, touchpoint_id):
        '''
        Read touchpoint according to sensor identifier (name)

        Arguments:
        - touchpoint_id : touchpoint identifier
        '''
        assert touchpoint_id in self._touchpoints
        self.logger.debug('Reading touchpoint: {}'.format(touchpoint_id))
        return self._touchpoints[touchpoint_id].read()
