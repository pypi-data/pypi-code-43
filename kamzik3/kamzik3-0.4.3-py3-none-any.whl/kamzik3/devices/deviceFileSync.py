import os
import time

from kamzik3 import DeviceError
from kamzik3.constants import *
from kamzik3.devices.attribute import Attribute
from kamzik3.devices.device import Device


class DeviceFileSync(Device):

    def __init__(self, filepath, device_id=None, config=None):
        self.filepath = filepath
        super(DeviceFileSync, self).__init__(device_id, config)
        self._expose_methods_to_clients()
        self.connect()

    def _init_attributes(self):
        super(DeviceFileSync, self)._init_attributes()

        self.attributes.update({
            ATTR_FILEPATH: Attribute(set_function=self.set_filepath, readonly=True),
            ATTR_CONTENT: Attribute(set_function=self.set_content),
        })

    def handle_configuration(self):

        start_at = time.time()

        def _finish_configuration(*_, **__):
            self._config_commands()
            self._config_attributes()
            self.set_attribute((ATTR_FILEPATH, VALUE), self.filepath)
            self.set_status(STATUS_CONFIGURED)
            self.logger.info(u"Device configuration took {} sec.".format(time.time() - start_at))

        _finish_configuration()

    def set_filepath(self, value):
        if not os.path.exists(value):
            raise DeviceError("File {} does not exists".format(value))
        else:
            with open(value, "r") as fp:
                file_content = "".join(fp.readlines())
                self.set_value(ATTR_CONTENT, file_content)

    def set_content(self, value):
        file_path = self[ATTR_FILEPATH][VALUE]
        with open(file_path, "w") as fp:
            fp.write(value)
            self.set_value(ATTR_CONTENT, value)
