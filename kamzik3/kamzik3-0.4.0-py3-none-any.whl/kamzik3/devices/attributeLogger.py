import logging
import time
from logging.handlers import TimedRotatingFileHandler
from threading import Thread, Event

import numpy as np

from kamzik3 import DeviceError, DeviceUnknownError, units
from kamzik3.constants import *
from kamzik3.devices.attribute import Attribute
from kamzik3.devices.device import Device
from kamzik3.snippets.snippetLogging import set_rotating_file_handler, set_file_handler

ATTR_LOGFILE = "Logfile"
ATTR_HEADER = "Header"
ATTR_LAST_LOG_LINE = "Last log line"
ATTR_INTERVAL = "Interval"
ATTR_LOGGING = "Logging"


class AttributeLogger(Device):
    # Logging interval in ms
    interval = 1e3
    separator = ";"
    logged_attributes = None
    attribute_logger = None
    attribute_logger_handler = None
    preset_header = u""

    def __init__(self, log_file_name, device_id=None, config=None):
        if self.logged_attributes is None:
            self.logged_attributes = []

        self.stopped = Event()
        self.log_file_name = log_file_name
        self.log_formatter = logging.Formatter(self.separator.join(['%(asctime)s', '%(created)s', '%(message)s']),
                                               datefmt='%Y-%m-%d %H:%M:%S')
        super(AttributeLogger, self).__init__(device_id, config)
        self.connect()

    def connect(self):
        self.handle_connect_event()
        self.set_status(STATUS_IDLE)

    def _init_attributes(self):
        super(AttributeLogger, self)._init_attributes()
        self.attributes.update({
            ATTR_HEADER: Attribute(readonly=True),
            ATTR_INTERVAL: Attribute(self.interval, min_value=100, max_value=3600 * 1e3, unit=u"ms",
                                     default_type=np.uint32),
            ATTR_LAST_LOG_LINE: Attribute(readonly=True),
            ATTR_LOGFILE: Attribute(self.log_file_name, readonly=True),
            ATTR_LOGGING: Attribute(min_value=0, max_value=1, default_type=np.bool, set_function=self.start,
                                    set_value_when_set_function=True)
        })

    def _get_logged_attributes(self):
        logged_values = []
        value_unit = u""
        for device_id, attribute in self.logged_attributes[:]:
            try:
                device = self.session.get_device(device_id)
                logged_value, value_unit = None, u""
                if device.in_statuses(READY_DEVICE_STATUSES):
                    attribute = device.get_attribute(attribute)
                    if attribute is not None and attribute.value() is not None:
                        attribute_value = attribute.value()
                        if isinstance(attribute_value, units.Quantity):
                            logged_value = "{:~}".format(attribute.value())
                        else:
                            logged_value = attribute.value()
            except DeviceUnknownError:
                logged_value = None

            if logged_value is None:
                logged_value, value_unit = u"None", u""

            logged_values.append("{}{}".format(logged_value, value_unit))

        return logged_values

    def set_log_file_name(self, log_file_name):
        self.set_attribute([ATTR_LOGFILE, VALUE], log_file_name)
        attribute_logger = logging.getLogger(u"AttributeLogger.{}".format(self.device_id))
        if self.attribute_logger_handler is not None:
            attribute_logger.removeHandler(self.attribute_logger_handler)

        if self.config.get("rotating", True):
            self.attribute_logger_handler = set_rotating_file_handler(attribute_logger, self.log_file_name,
                                                                      self.log_formatter)

            def do_rollover():
                TimedRotatingFileHandler.doRollover(self.attribute_logger_handler)
                self.write_header()

            self.attribute_logger_handler.doRollover = do_rollover
        else:
            self.attribute_logger_handler = set_file_handler(attribute_logger, self.log_file_name,
                                                             self.log_formatter)
        attribute_logger.setLevel(logging.INFO)
        return attribute_logger

    def handle_configuration(self):
        start_at = time.time()

        def _finish_configuration(*_, **__):
            self._config_commands()
            self._config_attributes()
            self.attribute_logger = self.set_log_file_name(self.log_file_name)
            self.set_status(STATUS_CONFIGURED)
            self.logger.info(u"Device configuration took {} sec.".format(time.time() - start_at))

        _finish_configuration()

    def handle_interval_timeout(self):
        logged_values = self._get_logged_attributes()
        last_log_line = self.separator.join(logged_values)
        self.set_attribute([ATTR_LAST_LOG_LINE, VALUE], last_log_line)
        self.attribute_logger.info(last_log_line)

    def add_logged_attribute(self, device_id, attribute):
        attribute = Attribute.list_attribute(attribute)
        item = (device_id, attribute)

        if item not in self.logged_attributes:
            self.logged_attributes.append(item)

    def remove_logged_attribute(self, device_id, attribute):
        if isinstance(attribute, str):
            attribute = [attribute]
        elif isinstance(attribute, tuple):
            attribute = list(attribute)

        self.logged_attributes.remove((device_id, attribute))

    def generate_header(self):
        header_line = ["Datetime", "Timestamp"]
        for device_id, attribute in self.logged_attributes[:]:
            header_line.append(u"{} {}".format(device_id, attribute))
        return "# " + self.separator.join(header_line).replace("'", "").replace(", ", ",")

    def write_header(self):
        header = self.preset_header + self.generate_header()
        self.set_attribute([ATTR_HEADER, VALUE], header)
        with open(self.log_file_name, "a+") as fp:
            fp.write(header)
            fp.write("\n")

    def start(self, flag=True):
        if flag:
            if self.is_status(STATUS_BUSY):
                raise DeviceError(u"Logging is already running")

            self.stopped.clear()
            self.write_header()

            Thread(target=self._logging_thread).start()
        else:
            self.stop()

    def stop(self):
        try:
            self.stopped.set()
            self.set_status(STATUS_IDLE)
        except TypeError:
            pass

    def _logging_thread(self):
        self.set_status(STATUS_BUSY)
        # Set waiting time to zero initially so we always get the first log input
        logging_interval = 0
        while not self.stopped.wait(logging_interval):
            t = time.time()
            self.handle_interval_timeout()
            # Time compensation for time needed to collect log input
            time_delta = time.time() - t
            # Calculate next logging interval
            logging_interval = self.get_value(ATTR_INTERVAL) * 1e-3 - time_delta

    def close(self):
        self.stop()
        super(AttributeLogger, self).close()

    def disconnect(self):
        # Remove all handlers
        self.stop()
        try:
            for handler in self.attribute_logger.handlers[:]:
                handler.close()
        except AttributeError:
            # No attribute_logger in which case just continue
            pass
        self.logged_attributes = None
        self.attribute_logger = None
        self.attribute_logger_handler = None
        self.logged_attributes = []
        self.log_formatter = None
        return super().disconnect()


class AttributeLoggerTriggered(AttributeLogger):

    def start(self, flag=True):
        if flag:
            if self.is_status(STATUS_BUSY):
                raise DeviceError(u"Logging is already running")

            self.stopped.clear()
            self.write_header()
            self.set_status(STATUS_BUSY)
        else:
            self.stop()

    def trigger(self):
        self.handle_interval_timeout()
