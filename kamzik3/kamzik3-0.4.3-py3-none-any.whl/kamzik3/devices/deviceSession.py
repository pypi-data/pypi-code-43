import logging
import os
import time
from collections import OrderedDict

import numpy as np

import kamzik3
from kamzik3 import DeviceUnknownError, DeviceError
from kamzik3.constants import *
from kamzik3.devices.attribute import Attribute
from kamzik3.devices.attributeLogger import AttributeLogger, ATTR_LOGGING
from kamzik3.devices.device import Device
from kamzik3.devices.deviceClient import DeviceClient
from kamzik3.devices.general.measurementGroup import MeasurementGroup
from kamzik3.snippets.snippetLogging import set_rotating_file_handler, set_sys_exception_handler, get_console_handler
from kamzik3.snippets.snippetsControlLoops import control_asyncore_loop, control_device_poller, control_port_read_loop, \
    control_device_client_poller


class DeviceSession(Device):
    LOG_DEVICE_OUTPUT_FILE = u"devices.log"
    LOG_CONSOLE_OUTPUT_FILE = u"console.log"
    LOG_ATTRIBUTES_OUTPUT_FILE = u"attributes.log"
    LOG_GUI_OUTPUT_FILE = u"gui.log"
    LOG_MACRO_OUTPUT_FILE = u"macro.log"
    log_level = logging.INFO

    def __init__(self, device_id=None, config=None):
        kamzik3.session = self
        self.devices = OrderedDict()
        self.measurement_groups = {}
        super(DeviceSession, self).__init__(device_id, config)
        self._expose_methods_to_clients()
        self.connect()

    def _init_attributes(self):
        super(DeviceSession, self)._init_attributes()

        self.attributes.update({
            ATTR_LOG_DIRECTORY: Attribute(set_function=self.set_log_directory, readonly=True,
                                          set_value_when_set_function=True),
            ATTR_RESOURCE_DIRECTORY: Attribute(set_function=self.set_resource_directory, readonly=True,
                                               set_value_when_set_function=True),
            ATTR_DEVICES_COUNT: Attribute(0, default_type=np.uint64, readonly=True),
            ATTR_ALLOW_CONSOLE_LOG: Attribute(True, default_type=np.bool),
            ATTR_ALLOW_GUI_LOG: Attribute(True, default_type=np.bool),
            ATTR_ALLOW_DEVICE_LOG: Attribute(True, default_type=np.bool),
            ATTR_ALLOW_ATTRIBUTE_LOG: Attribute(True, default_type=np.bool),
            ATTR_ALLOW_MACRO_LOG: Attribute(True, default_type=np.bool),
            ATTR_LOOPS_RUNNING: Attribute(False, default_type=np.bool, readonly=True),
        })

    def add_measurement_group(self, measurement_group):
        assert isinstance(measurement_group, MeasurementGroup)
        self.measurement_groups[measurement_group.group_id] = measurement_group

    def set_session(self, session):
        self.devices[self.device_id] = self
        self.session = self
        self.set_value(ATTR_DEVICES_COUNT, len(self.devices))

    def handle_configuration(self):

        start_at = time.time()

        def _finish_configuration(*_, **__):
            self._config_commands()
            self._config_attributes()

            if self.get_value(ATTR_ALLOW_CONSOLE_LOG):
                self.set_console_log_directory(u"Console")
            if self.get_value(ATTR_ALLOW_GUI_LOG):
                self.set_gui_log_directory(u"Gui")
            if self.get_value(ATTR_ALLOW_DEVICE_LOG):
                self.set_device_log_directory(u"Device")
            if self.get_value(ATTR_ALLOW_ATTRIBUTE_LOG):
                self.set_attribute_log_directory(u"Attributes")
                self._config_attributes_log()
            if self.get_value(ATTR_ALLOW_MACRO_LOG):
                self.set_macro_log_directory(u"Macro")

            self.set_status(STATUS_CONFIGURED)
            self.logger.info(u"Device configuration took {} sec.".format(time.time() - start_at))

        _finish_configuration()

    def _config_attributes_log(self):
        if self.config:
            logger = self.get_device("AttributeLogger")
            for device_id, attribute in self.config.get("logged_attributes", {}).items():
                if isinstance(attribute, list):
                    for sub_attribute in attribute:
                        logger.add_logged_attribute(device_id, sub_attribute)
                else:
                    logger.add_logged_attribute(device_id, attribute)
            logger.set_attribute((ATTR_LOGGING, VALUE), True)

    def get_device(self, device_id):
        try:
            return self.devices[device_id]
        except KeyError:
            master_server, master_port = self.config.get("master_server", False), self.config.get("master_port", False)
            if master_server and master_port:
                return DeviceClient(master_server, master_port, device_id)
            raise DeviceUnknownError("Device {} was not found.".format(device_id))

    def add_device(self, device):
        assert isinstance(device, Device)

        if device.device_id not in self.devices:
            self.devices[device.device_id] = device
            device.session = self
            self.set_value(ATTR_DEVICES_COUNT, len(self.devices))
            if self.device_server is not None:
                self.device_server.add_device(device)
        else:

            raise DeviceError("Device {} is already registered within session.".format(device.device_id))

    def remove_device(self, device):
        assert isinstance(device, Device)

        if device.device_id in self.devices:
            device.session = None
            del self.devices[device.device_id]
            self.set_value(ATTR_DEVICES_COUNT, len(self.devices))

    def get_devices(self, class_filter=None, attribute_filter=None, method_filter=None):
        """
        Filter devices in current session
        :param class_filter: list of classes
        :param attribute_filter: attribute
        :param method_filter: method name
        :return: list of filtered devices
        """
        filtered_devices = self.devices.copy()
        # Filter over device class
        if class_filter is not None:
            for device_id, device in filtered_devices.copy().items():
                # if not isinstance(device, class_filter):
                if class_filter in device.qualified_name:
                    del filtered_devices[device_id]
        # Filter over device attributes
        if attribute_filter is not None:
            for device_id, device in filtered_devices.copy().items():
                if device.get_attribute(attribute_filter) is None:
                    del filtered_devices[device_id]
        # Filter over device methods
        if method_filter is not None:
            for device_id, device in filtered_devices.copy().items():
                filtered_out_methods = filter(lambda val: val[0] == method_filter, device.exposed_methods)
                try:
                    next(filtered_out_methods)
                except StopIteration:
                    del filtered_devices[device_id]

        return filtered_devices

    def set_log_directory(self, value):
        self.logger.info(u"Setting log directory to: {}".format(value))
        if not os.path.exists(value):
            self.logger.info(u"Directory {} does not exists, trying to create it.".format(value))
            os.makedirs(value)

    def set_resource_directory(self, value):
        self.logger.info(u"Setting resource directory to: {}".format(value))
        if not os.path.exists(value):
            self.logger.info(u"Directory {} does not exists, trying to create it.".format(value))
            os.makedirs(value)

    def set_console_log_directory(self, value):
        log_directory = self.get_value(ATTR_LOG_DIRECTORY)
        if log_directory is None:
            raise DeviceError(u"Cannot set console log directory. Attribute 'Log directory' is not set.")
        log_directory = os.path.join(log_directory, value)
        self.logger.info(u"Setting console log directory to: {}".format(log_directory))
        if not os.path.exists(log_directory):
            self.logger.info(u"Directory {} does not exists, trying to create it.".format(log_directory))
            os.makedirs(log_directory)

        handler = get_console_handler()
        logger = logging.getLogger(u"Console")
        set_rotating_file_handler(logger, os.path.join(log_directory, self.LOG_CONSOLE_OUTPUT_FILE))
        set_sys_exception_handler(logger)
        logger.setLevel(self.log_level)
        logger.addHandler(handler)

    def set_gui_log_directory(self, value):
        log_directory = self.get_value(ATTR_LOG_DIRECTORY)
        if log_directory is None:
            raise DeviceError(u"Cannot set gui log directory. Attribute 'Log directory' is not set.")
        log_directory = os.path.join(log_directory, value)

        self.logger.info(u"Setting gui log directory to: {}".format(log_directory))
        if not os.path.exists(log_directory):
            self.logger.info(u"Directory {} does not exists, trying to create it.".format(log_directory))
            os.makedirs(log_directory)

        handler = get_console_handler()
        logger = logging.getLogger(u"Gui")
        set_rotating_file_handler(logger, os.path.join(log_directory, self.LOG_GUI_OUTPUT_FILE))
        logger.setLevel(logging.DEBUG)
        logger.addHandler(handler)

    def set_attribute_log_directory(self, value):
        log_directory = self.get_value(ATTR_LOG_DIRECTORY)
        if log_directory is None:
            raise DeviceError(u"Cannot set device log directory. Attribute 'Log directory' is not set.")
        log_directory = os.path.join(log_directory, value)

        self.logger.info(u"Setting device log directory to: {}".format(log_directory))
        if not os.path.exists(log_directory):
            self.logger.info(u"Directory {} does not exists, trying to create it.".format(log_directory))
            os.makedirs(log_directory)

        logger = AttributeLogger(os.path.join(log_directory, self.LOG_ATTRIBUTES_OUTPUT_FILE),
                                 device_id="AttributeLogger")
        self.attributes.update({
            "Attribute logger": logger.attributes
        })

    def set_device_log_directory(self, value):
        log_directory = self.get_value(ATTR_LOG_DIRECTORY)
        if log_directory is None:
            raise DeviceError(u"Cannot set device log directory. Attribute 'Log directory' is not set.")
        log_directory = os.path.join(log_directory, value)

        self.logger.info(u"Setting device log directory to: {}".format(log_directory))
        if not os.path.exists(log_directory):
            self.logger.info(u"Directory {} does not exists, trying to create it.".format(log_directory))
            os.makedirs(log_directory)

        handler = get_console_handler()
        logger = logging.getLogger(u"Device")
        set_rotating_file_handler(logger, os.path.join(log_directory, self.LOG_DEVICE_OUTPUT_FILE))
        logger.setLevel(self.log_level)
        logger.addHandler(handler)

    def set_macro_log_directory(self, value):
        log_directory = self.get_value(ATTR_LOG_DIRECTORY)
        if log_directory is None:
            raise DeviceError(u"Cannot set gui log directory. Attribute 'Log directory' is not set.")
        log_directory = os.path.join(log_directory, value)

        self.logger.info(u"Setting gui log directory to: {}".format(log_directory))
        if not os.path.exists(log_directory):
            self.logger.info(u"Directory {} does not exists, trying to create it.".format(log_directory))
            os.makedirs(log_directory)

        handler = get_console_handler()
        logger = logging.getLogger(u"Macro")
        set_rotating_file_handler(logger, os.path.join(log_directory, self.LOG_MACRO_OUTPUT_FILE))
        logger.setLevel(logging.DEBUG)
        logger.addHandler(handler)

    def start_control_loops(self):
        if not self.get_value(ATTR_LOOPS_RUNNING):
            self.start_asyncore_loop()
            self.start_device_poller_loop()
            self.start_port_read_loop()
            self.start_client_poller_loop()
            self.set_value(ATTR_LOOPS_RUNNING, True)

    def stop_control_loops(self):
        if self.get_value(ATTR_LOOPS_RUNNING):
            self.stop_asyncore_loop()
            self.stop_port_read_loop()
            self.stop_device_poller_loop()
            self.stop_client_poller_loop()
            self.set_value(ATTR_LOOPS_RUNNING, False)

        self.logger.info("Closing all control loops")
        # Here we try to join all control loops giving them 1 second timeout
        control_asyncore_loop.join(1)
        control_device_poller.join(1)
        control_port_read_loop.join(1)
        control_device_client_poller.join(1)
        self.logger.info("Control loops closed")

    def stop(self):
        if self.device_server is not None:
            self.device_server.close()
        self.stop_client_poller_loop()
        self.session = None
        del self.devices[self.device_id]

        for device in list(self.devices.values()):
            device.disconnect()

        if self.get_value(ATTR_LOOPS_RUNNING):
            self.stop_control_loops()
            self.set_value(ATTR_LOOPS_RUNNING, False)

    @staticmethod
    def start_client_poller_loop():
        control_device_client_poller.start()

    @staticmethod
    def stop_client_poller_loop():
        control_device_client_poller.stop()

    @staticmethod
    def start_asyncore_loop():
        control_asyncore_loop.start()

    @staticmethod
    def stop_asyncore_loop():
        control_asyncore_loop.stop()

    @staticmethod
    def start_device_poller_loop():
        control_device_poller.start()

    @staticmethod
    def stop_device_poller_loop():
        control_device_poller.stop()

    @staticmethod
    def start_port_read_loop():
        control_port_read_loop.start()

    @staticmethod
    def stop_port_read_loop():
        control_port_read_loop.stop()
