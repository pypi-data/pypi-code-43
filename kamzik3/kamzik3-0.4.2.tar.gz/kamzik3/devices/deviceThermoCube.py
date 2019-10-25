import time

import numpy as np
import serial

from kamzik3 import units, WriteException
from kamzik3.constants import *
from kamzik3.devices.attribute import Attribute
from kamzik3.devices.devicePort import DevicePort
from kamzik3.devices.deviceSocket import DeviceSocket


class DeviceThermoCube(DeviceSocket):
    """
    The ThermoCube 200/300/400 can store 8 bytes of transmission and can only handle up to 3
    commands per second.
    """
    terminator = b"\r\n"
    push_commands_max = 1

    def handle_configuration(self):
        start_at = time.time()

        def _finish_configuration(*_, **__):
            self._config_commands()
            self._config_attributes()
            self.start_polling()
            self.set_status(STATUS_CONFIGURED)
            self.logger.info(u"Device configuration took {} sec.".format(time.time() - start_at))

        self.command(b'\xC8')
        self.command(b'\xC9')
        self.command(b'\xC1', callback=_finish_configuration)

    def _init_attributes(self):
        DeviceSocket._init_attributes(self)

        self.attributes.update({
            ATTR_FAULT_BYTE: Attribute(None, readonly=True, min_value=0, max_value=8, default_type=np.uint8),
            ATTR_TEMPERATURE: Attribute(None, readonly=True, min_value=-100, max_value=100, unit="degC",
                                        default_type=np.float, decimals=3),
            ATTR_SETPOINT: Attribute(None, min_value=-100, max_value=100, unit="degC",
                                     default_type=np.float, decimals=3, set_function=self.set_setpoint),
        })

    def handle_readout(self, readout_buffer):
        command, output, callback, token = DeviceSocket.handle_readout(self, readout_buffer)
        if command == b'\xC9':
            temperature = self.hex_to_temperature(self.parse_temperature_readout(output))
            self.set_value(ATTR_TEMPERATURE, temperature.m)
        elif command == b'\xC1':
            setpoint = self.hex_to_temperature(self.parse_temperature_readout(output))
            self.set_value(ATTR_SETPOINT, setpoint.m)
        elif command == b'\xC8':
            errorByte = int(output)
            self.set_value(ATTR_FAULT_BYTE, errorByte)
            if errorByte == 0:
                self.set_status(STATUS_IDLE)
            else:
                self.set_status(STATUS_ERROR)

        if callback is not None:
            self.handle_readout_callback(callback, command, readout_buffer)
        if token:
            self.device_server.push_message(self.device_id, [command, readout_buffer], token)

    def start_polling(self):
        DeviceSocket.start_polling(self)
        # Poll current temperature
        self.poll_command(b'\xC9', 500)
        # Poll current setpoint
        self.poll_command(b'\xC1', 5000)
        # Poll current setpoint
        self.poll_command(b'\xC8', 500)

    @staticmethod
    def parse_temperature_readout(rawDeviceReadout):
        low_byte, high_byte = rawDeviceReadout.split(",")
        return "0x%x%x" % (int(high_byte), int(low_byte))

    @staticmethod
    def temperature_to_hex(temperature):
        temperature_in_kelvin = units.Quantity(temperature, "celsius").to("fahrenheit")
        return "{:04X}".format(int(temperature_in_kelvin.m * 10))

    @staticmethod
    def hex_to_temperature(hexTemperature):
        temperature_in_fahrenheit = int(hexTemperature, 16) / 10
        return units.Quantity(temperature_in_fahrenheit, "fahrenheit").to("celsius")

    def get_temperature(self):
        self.command(b'\xC9')

    def get_setpoint(self):
        self.command(b'\xC1')

    def get_error(self):
        self.command(b'\xC8')

    def set_setpoint(self, temperature, callback=None):
        """
        Set temperature setpoint.
        We need to send three commands.
        E1, Low data byte, High data byte.
        :param temperature:
        :param callback:
        :return:
        """
        temperature_in_hex = self.temperature_to_hex(temperature)
        self.command(b'\xE1', returning=False)
        self.command(bytes.fromhex(temperature_in_hex[2:]), returning=False)
        self.command(bytes.fromhex(temperature_in_hex[:2]), returning=False, with_token=True)

    def send_command(self, commands):
        try:
            if self.connected:
                command = commands.pop(0)
                if command[3]:  # If command is returning
                    self.commands_buffer.append((command, time.time()))
                else:  # Command is not returning, simulate immediate execution
                    self.response_timestamp = time.time()
                self.push(command[0])
            else:
                self.handle_response_error(u"Device is not connected")
        except IndexError:
            self.handle_connection_error(u"Device {} buffer error".format(self.device_id))
        except (WriteException, serial.SerialException):
            self.handle_response_error(u"Device {} writing error".format(self.device_id))
        finally:
            return commands


class DeviceThermoCubePort(DevicePort, DeviceThermoCube):
    terminator = None
    push_commands_max = 1

    def __init__(self, port, baud_rate=9600, parity=serial.PARITY_NONE, stop_bits=serial.STOPBITS_ONE,
                 byte_size=serial.EIGHTBITS, device_id=None, config=None):
        DevicePort.__init__(self, port, baud_rate, parity, stop_bits, byte_size, device_id, config)

    def handshake(self):
        self.logger.info(u"Handshake initiated")
        self.push(b'\xC8')
        time.sleep(0.3)  # Give some time for devices to reply
        if self.serial_port.in_waiting != 0:
            readout = ord(self.read_all())
            if readout >= 0:
                return True
        return False

    def collect_incoming_data(self, data):
        # Get all bytes as separate string
        for c in data:
            self.buffer.append(str(c))

        cmd_query = self.commands_buffer[0][0][0]
        # Commands that queries temperature consist of two bytes
        if cmd_query in (b'\xC9', b'\xC1') and len(self.buffer) != 2:
            return
        # Create final string by joining buffer content with comma
        self.buffer = [",".join(self.buffer)]
        # Invoke found_terminator even though there is now terminator
        # We just want to continue in normal controller workflow and process command
        self.found_terminator()
