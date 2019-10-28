import time
from threading import Thread
from time import sleep

import numpy as np

from kamzik3 import DeviceError
from kamzik3.constants import *
from kamzik3.devices.attribute import Attribute
from kamzik3.devices.device import Device
from kamzik3.devices.deviceChannel import DeviceChannel
from kamzik3.snippets.snippetsDecorators import expose_method


class DummyMotor(Device):

    def __init__(self, channels=3, device_id=None, config=None):
        assert channels > 0
        self.channels = channels
        Device.__init__(self, device_id, config)
        self._expose_methods_to_clients()
        self.connect()

    def _init_attributes(self):
        Device._init_attributes(self)
        self.attributes.update({
            ATTR_CHANNELS: Attribute(self.channels, readonly=True, default_type=np.uint16, max_value=255),
        })

    def connect(self, *args):
        """
        Call only this function to connect devices to port / socket / library / ...
        :param args: connect attributes
        """
        self.connecting = True
        self.handle_configuration_event()
        self.connected = True
        self.connecting = False
        self.set_status(STATUS_IDLE)

    def handle_configuration(self):
        start_at = time.time()
        self.set_status(STATUS_CONFIGURED)
        self.logger.info(u"Device configuration took {} sec.".format(time.time() - start_at))


class DummyMotorChannel(DeviceChannel):

    def __init__(self, device, channel, device_id=None, config=None):
        super().__init__(device, channel, device_id, config)
        self.handle_configuration()

    def handle_configuration(self):
        if self.configured:
            return

        start_at = time.time()

        def _finish_configuration(*_, **__):
            self._config_commands()
            self._config_attributes()
            self.configured = True
            self.start_polling()
            self.set_status(STATUS_CONFIGURED)
            self.logger.info(u"Device configuration took {} sec.".format(time.time() - start_at))

        self.connected = True
        _finish_configuration()

    def _init_attributes(self):
        DeviceChannel._init_attributes(self)

        self.attributes.update({
            ATTR_REFERENCED: Attribute(True, readonly=True, default_type=np.bool),
            ATTR_POSITION: Attribute(0, default_type=np.int64, set_function=self._move_absolute, unit="nm",
                                     set_value_when_set_function=False, min_value=-1e9, max_value=1e9),
            ATTR_POSITION_LOWER_LIMIT: Attribute(-1e9, default_type=np.int64, min_value=-1e9, max_value=1e9,
                                                 unit="nm", set_function=self._set_lower_limit),
            ATTR_POSITION_UPPER_LIMIT: Attribute(1e9, default_type=np.int64, min_value=-1e9, max_value=1e9,
                                                 unit="nm", set_function=self._set_upper_limit),
            ATTR_MAXIMUM_VELOCITY: Attribute(1e5, default_type=np.uint64, min_value=10, max_value=1e6, unit="nm/sec",
                                             set_function=self._set_maximum_velocity),
            ATTR_VELOCITY: Attribute(0, default_type=np.int64, min_value=-1e4, max_value=1e4, unit="nm/sec"),
        })

    def subject_update(self, key, value, subject):
        DeviceChannel.subject_update(self, key, value, subject)

        if self.connected and isinstance(key, tuple) and key[0] == self.channel:
            attribute = key[1]

            self.set_attribute((ATTR_LATENCY, VALUE), self.device.get_value(ATTR_LATENCY))
            self.set_value(attribute, value)

    def _move_absolute(self, value, callback=None):
        if self.is_status(STATUS_BUSY):
            raise DeviceError("Motor is moving")

        def move_thread(setpoint):
            if value == self.get_value(ATTR_POSITION):
                return

            direction = 1
            if setpoint - self.get_value(ATTR_POSITION) < 0:
                direction = -1

            self.set_attribute([ATTR_VELOCITY, VALUE], direction * self.get_value(ATTR_MAXIMUM_VELOCITY))
            self.set_status(STATUS_BUSY)
            counter = 0
            while self[ATTR_VELOCITY][VALUE] != 0 and self.is_status(STATUS_BUSY):
                # Velocity in nm / 100ms
                s = time.time()
                counter += 1
                velocity = int(self.get_value(ATTR_VELOCITY) / 10.)
                new_position = self.get_value(ATTR_POSITION) + velocity
                if direction == 1:
                    if new_position < setpoint:
                        self.set_value(ATTR_POSITION, new_position)
                    else:
                        self.set_value(ATTR_POSITION, setpoint)
                        self.stop()
                else:
                    if new_position > setpoint:
                        self.set_value(ATTR_POSITION, new_position)
                    else:
                        self.set_value(ATTR_POSITION, setpoint)
                        self.stop()
                sleep(0.1)
            self.set_status(STATUS_IDLE)

        Thread(target=move_thread, args=[value]).start()
        if callback is not None:
            callback()

    def _set_upper_limit(self, value, callback=None):
        position_upper_limit = self[ATTR_POSITION].remove_offset_factor(value)
        self.set_attribute([ATTR_POSITION, MAX], position_upper_limit)
        if callback is not None:
            callback()

    def _set_lower_limit(self, value, callback=None):
        position_lower_limit = self[ATTR_POSITION].remove_offset_factor(value)
        self.set_attribute([ATTR_POSITION, MIN], position_lower_limit)
        if callback is not None:
            callback()

    def _set_maximum_velocity(self, value, callback=None):
        velocity_upper_limit = self[ATTR_VELOCITY].remove_offset_factor(value)
        velocity_lower_limit = -velocity_upper_limit
        self.set_attribute([ATTR_VELOCITY, MIN], velocity_lower_limit)
        self.set_attribute([ATTR_VELOCITY, MAX], velocity_upper_limit)

        if self.get_value(ATTR_VELOCITY) > velocity_upper_limit:
            self.set_attribute([ATTR_VELOCITY, VALUE], velocity_upper_limit)
        elif self.get_value(ATTR_VELOCITY) < velocity_lower_limit:
            self.set_attribute([ATTR_VELOCITY, VALUE], velocity_lower_limit)
        if callback is not None:
            callback()

    @expose_method()
    def find_reference(self, callback=None):
        if self.is_status(STATUS_BUSY):
            raise DeviceError("Motor is moving")

        self.logger.info(u"Find reference")
        self.set_value(ATTR_POSITION, 0)
        if callback is not None:
            callback()

    @expose_method()
    def stop(self, callback=None):
        self.set_attribute([ATTR_VELOCITY, VALUE], 0)
        if callback is not None:
            callback()

    def disconnect(self):
        self.stop()
        super().disconnect()
