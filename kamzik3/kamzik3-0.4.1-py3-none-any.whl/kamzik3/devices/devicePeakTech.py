import time

import numpy as np
import serial

from kamzik3.constants import *
from kamzik3.devices.attribute import Attribute
from kamzik3.devices.devicePort import DevicePort
from kamzik3.devices.deviceSocket import DeviceSocket


class DevicePeakTech(DeviceSocket):
    terminator = b"OK\r"
    push_commands_max = 1

    def handle_configuration(self):
        start_at = time.time()

        def _finish_configuration(*_, **__):
            self._config_commands()
            self._config_attributes()
            self.start_polling()
            self.set_status(STATUS_CONFIGURED)
            self.logger.info(u"Device configuration took {} sec.".format(time.time() - start_at))

        self.command(u"GOVP\r")
        self.command(u"GOCP\r", callback=_finish_configuration)

    def _init_attributes(self):
        super(DevicePeakTech, self)._init_attributes()

        self.attributes.update({
            ATTR_CONSTANT_CURRENT: Attribute(None, readonly=True, default_type=np.bool),
            ATTR_CONSTANT_VOLTAGE: Attribute(None, readonly=True, default_type=np.bool),
            ATTR_VOLTAGE: Attribute(None, default_type=np.float16, min_value=0, decimals=3, unit="V",
                                    set_function=self.set_voltage_output),
            ATTR_MAX_VOLTAGE: Attribute(None, default_type=np.float16, min_value=0, decimals=1, unit="V",
                                        max_value=99.9, set_function=self.set_max_voltage_output,
                                        set_value_when_set_function=False),
            ATTR_CURRENT: Attribute(None, default_type=np.float16, min_value=0,
                                    decimals=3, unit="A", set_function=self.set_current_output),
            ATTR_MAX_CURRENT: Attribute(None, default_type=np.float16, min_value=0, max_value=99.9, decimals=1,
                                        unit="A",
                                        set_function=self.set_max_current_output, set_value_when_set_function=False),
            ATTR_OUTPUT_SWITCH: Attribute(None, readonly=False, default_type=np.bool, set_function=self.switch_output,
                                          set_value_when_set_function=False),
        })

    def handle_readout(self, readout_buffer):
        command, output, callback, token = super(DevicePeakTech, self).handle_readout(readout_buffer)

        if command == u"GETD\r":
            voltage, current, cv_cc_flag = int(output[:4]) / 100., int(output[4:8]) / 100, int(output[8:])
            self.set_value(ATTR_CONSTANT_VOLTAGE, True if cv_cc_flag == 0 else False)
            self.set_value(ATTR_CONSTANT_CURRENT, True if cv_cc_flag == 1 else False)
            self.set_value(ATTR_VOLTAGE, voltage)
            self.set_value(ATTR_CURRENT, current)
            if voltage < 0.75:
                self.set_value(ATTR_OUTPUT_SWITCH, False)
            else:
                self.set_value(ATTR_OUTPUT_SWITCH, True)
        elif command == u"GOVP\r":
            max_voltage = int(output[:3]) / 10
            self.set_attribute((ATTR_VOLTAGE, MAX), max_voltage)
            self.set_value(ATTR_MAX_VOLTAGE, max_voltage)
        elif command == u"GOCP\r":
            max_current = int(output[:3]) / 10
            self.set_attribute((ATTR_CURRENT, MAX), max_current)
            self.set_value(ATTR_MAX_CURRENT, max_current)

        if callback is not None:
            self.handle_readout_callback(callback, command, readout_buffer)
        if token:
            self.device_server.push_message(self.device_id, [command, readout_buffer], token)

    def start_polling(self):
        super().start_polling()
        self.poll_command(u"GETD\r", 200)

    def set_max_voltage_output(self, value, callback=None):
        self.logger.info(u"Set max voltage output to {} V".format(value))
        self.command(u"SOVP{0:03d}\r".format(int(float(value) * 10.)), callback, with_token=True)
        return self.command("GOVP\r")

    def set_max_current_output(self, value, callback=None):
        self.logger.info(u"Set max current output to {} A".format(value))
        self.command(u"SOCP{0:03d}\r".format(int(float(value) * 10.)), callback, with_token=True)
        return self.command("GOCP\r")

    def set_voltage_output(self, value, callback=None):
        self.logger.info(u"Set voltage output to {} V".format(value))
        return self.command(u"VOLT{0:03d}\r".format(int(float(value) * 10.)), callback, with_token=True)

    def set_current_output(self, value, callback=None):
        self.logger.info(u"Set current output to {} A".format(value))
        return self.command(u"CURR{0:03d}\r".format(int(float(value) * 10.)), callback, with_token=True)

    def switch_output(self, value, callback=None):
        self.logger.info(u"Switch output to {}".format(value))
        return self.command(u"SOUT{}\r".format(int(not value)), callback, with_token=True)

    def stop(self):
        self.set_voltage_output(0)
        self.set_current_output(0)


class DevicePeakTechPort(DevicePort, DevicePeakTech):
    terminator = DevicePeakTech.terminator
    push_commands_max = DevicePeakTech.push_commands_max

    def __init__(self, port, baud_rate=9600, parity=serial.PARITY_NONE, stop_bits=serial.STOPBITS_ONE,
                 byte_size=serial.EIGHTBITS, device_id=None, config=None):
        super().__init__(port, baud_rate, parity, stop_bits, byte_size, device_id, config)

    def handshake(self):
        self.logger.info(u"Handshake initiated")
        self.push(b"GETD\r")
        time.sleep(0.1)  # Give some time for devices to reply
        if self.serial_port.in_waiting != 0:
            readout = self.read_all().split("\r")
            if readout[1] == "OK":
                return True
        return False
