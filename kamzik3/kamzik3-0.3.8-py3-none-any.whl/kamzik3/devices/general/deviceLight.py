import time

import numpy as np

from kamzik3.constants import *
from kamzik3.devices.attribute import Attribute
from kamzik3.devices.device import Device
from kamzik3.snippets.snippetsDecorators import expose_method


class DeviceLight(Device):

    def __init__(self, device_id=None, config=None):
        super(DeviceLight, self).__init__(device_id, config)
        self._expose_methods_to_clients()
        self.connect()

    def handle_configuration(self):
        start_at = time.time()

        def _finish_configuration(*_, **__):
            self._config_commands()
            self._config_attributes()
            self.set_status(STATUS_CONFIGURED)
            self.logger.info(u"Device configuration took {} sec.".format(time.time() - start_at))

        _finish_configuration()

    def _init_attributes(self):
        super()._init_attributes()

        self.attributes.update({
            ATTR_INTENSITY: Attribute(None, readonly=False, default_type=np.float16, min_value=0, max_value=100,
                                      unit="%", decimals=1, set_function=self.set_intensity,
                                      set_value_when_set_function=False)
        })

    def set_intensity(self, value, callback=None):
        raise NotImplementedError()


class DeviceLightAttribute(DeviceLight):

    def __init__(self, device, attribute, device_id=None, config=None):
        self.device = device
        self.attribute = Attribute.list_attribute(attribute)
        super().__init__(device_id, config)

    def connect(self, *args):
        super(DeviceLightAttribute, self).connect(*args)
        self.device.attach_attribute_callback(self.attribute, self.value_changed)
        self.device.attach_attribute_callback(ATTR_STATUS, self.status_changed)

    def value_changed(self, key, value):
        if key == VALUE:
            value_min, value_max = self.device.get_attribute(self.attribute + [MIN]), self.device.get_attribute(
                self.attribute + [MAX])
            intensity = ((value - value_min) * 100) / (value_max - value_min)
            self.set_value(ATTR_INTENSITY, intensity)

    def status_changed(self, key, value):
        if key == VALUE:
            self.set_status(value)

    def set_intensity(self, value, callback=None):
        self.logger.info(u"Set light intensity to {} %".format(value))
        value_min, value_max = self.device.get_attribute(self.attribute + [MIN]), self.device.get_attribute(
            self.attribute + [MAX])
        attribute_value = ((value * (value_max - value_min) / 100) + value_min)
        self.device.set_attribute(self.attribute + [VALUE], attribute_value)

    @expose_method()
    def stop(self):
        self.device.stop()

    def close(self):
        self.device.detach_attribute_callback(self.attribute, self.value_changed)
        self.device.detach_attribute_callback(ATTR_STATUS, self.status_changed)
        return super(DeviceLightAttribute, self).close()
