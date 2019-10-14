import time

import numpy as np

from kamzik3.constants import *
from kamzik3.devices.attribute import Attribute
from kamzik3.devices.device import Device
from kamzik3.snippets.snippetsDecorators import expose_method
from kamzik3.snippets.snippetsUnits import device_units


class DeviceShutter(Device):

    def __init__(self, device_id=None, config=None):
        super(DeviceShutter, self).__init__(device_id, config)
        self._expose_methods_to_clients()
        self.connect()

    def _init_attributes(self):
        super(DeviceShutter, self)._init_attributes()

        self.attributes.update({
            ATTR_OPENED: Attribute(False, readonly=True, default_type=np.bool),
            ATTR_AUTO_MODE: Attribute(False, default_type=np.bool, set_value_when_set_function=True),
        })

    def handle_configuration(self):
        start_at = time.time()

        def _finish_configuration(*_, **__):
            self._config_commands()
            self._config_attributes()
            self.set_status(STATUS_CONFIGURED)
            self.logger.info(u"Device configuration took {} sec.".format(time.time() - start_at))

        _finish_configuration()

    def open_shutter(self):
        raise NotImplementedError()

    def close_shutter(self):
        raise NotImplementedError()

    def is_opened(self):
        raise NotImplementedError()


class DeviceShutterAttribute(DeviceShutter):

    def __init__(self, device, attribute, opened_value, closed_value, device_id=None, config=None):
        self.device = device
        self.attribute = Attribute.list_attribute(attribute)
        self.opened_value = opened_value
        self.closed_value = closed_value
        super(DeviceShutterAttribute, self).__init__(device_id, config)

    def _init_attributes(self):
        super(DeviceShutterAttribute, self)._init_attributes()
        opened_value = device_units(self.device, self.attribute, self.opened_value)
        closed_value = device_units(self.device, self.attribute, self.closed_value)
        self.attributes.update({
            ATTR_OPENED_VALUE: Attribute(opened_value.m, default_type=np.float64, unit="{:~}".format(opened_value.u)),
            ATTR_CLOSED_VALUE: Attribute(closed_value.m, default_type=np.float64, unit="{:~}".format(closed_value.u)),
            ATTR_OPENED_AT: Attribute(0, readonly=True, default_type=np.float16, min_value=0, max_value=100, decimals=2,
                                      unit=u"%"),
        })

    def connect(self, *args):
        super(DeviceShutterAttribute, self).connect(*args)
        self.device.attach_attribute_callback(self.attribute, self.shutter_value_changed)
        self.device.attach_attribute_callback(ATTR_STATUS, self.shutter_status_changed)

    def shutter_value_changed(self, key, value):
        if key == VALUE:
            self.set_value(ATTR_OPENED, self.is_opened(value))

    def shutter_status_changed(self, key, value):
        if key == VALUE:
            self.set_status(value)

    @expose_method()
    def open_shutter(self, clear_auto_mode=True):
        self.set_value(ATTR_AUTO_MODE, not clear_auto_mode)
        self.device.set_attribute(self.attribute + [VALUE], self.get_value(ATTR_OPENED_VALUE))

    @expose_method()
    def close_shutter(self, clear_auto_mode=True):
        self.set_value(ATTR_AUTO_MODE, not clear_auto_mode)
        self.device.set_attribute(self.attribute + [VALUE], self.get_value(ATTR_CLOSED_VALUE))

    @expose_method()
    def stop(self):
        self.device.stop()

    def is_opened(self, current_value=None):
        if current_value is None:
            current_value = self.get_value(self.attribute)
        tolerance = self.device.get_attribute(self.attribute + [TOLERANCE])
        opened_value = self.get_value(ATTR_OPENED_VALUE)
        try:
            self.set_value(ATTR_OPENED_AT, (float(current_value) / float(opened_value)) * 100)
        except ZeroDivisionError:
            self.set_value(ATTR_OPENED_AT, 100)
        return (opened_value - tolerance[0]) <= current_value <= (opened_value + tolerance[1])

    def close(self):
        self.device.detach_attribute_callback(self.attribute, self.shutter_value_changed)
        self.device.detach_attribute_callback(ATTR_STATUS, self.shutter_status_changed)
        return super(DeviceShutterAttribute, self).close()
