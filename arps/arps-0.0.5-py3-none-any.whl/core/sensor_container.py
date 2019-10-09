import logging

from arps.core.touchpoint import Sensor
from arps.core.touchpoint_container import TouchPointContainer


class SensorContainer(TouchPointContainer):

    def __init__(self, sensors):
        '''
        Arguments:
        - sensors : list containing instances from Sensor class

        Raise:
        - ValueError if any sensor is not a instance of Sensor class
        '''
        super().__init__(sensors, Sensor)
        self.logger = logging.getLogger(self.__class__.__name__)
        self.logger.debug(
            'Creating interface to read the following sensors: {}'.format(
                self._touchpoints))
