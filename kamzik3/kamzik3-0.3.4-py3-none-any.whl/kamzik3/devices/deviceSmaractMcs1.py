import re
import time

import numpy as np
import serial
from bidict import frozenbidict
from pint.errors import UndefinedUnitError

from kamzik3 import DeviceUnitError
from kamzik3.constants import *
from kamzik3.devices.attribute import Attribute
from kamzik3.devices.deviceChannel import DeviceChannel
from kamzik3.devices.devicePort import DevicePort
from kamzik3.devices.deviceSocket import DeviceSocket
from kamzik3.snippets.snippetsDecorators import expose_method
from kamzik3.snippets.snippetsUnits import device_units

""" Example of yaml configuration
Smaract0: &Smaract0 !Device:kamzik3.devices.deviceSmaractMcs1.DeviceSmaractMcs1
    device_id: Smaract0
    host: 192.168.83.91
Smaract0_axis_0: &Smaract0_axis_0 !Device:kamzik3.devices.deviceSmaractMcs1.DeviceSmaractMcs1Channel
    device: *Smaract0
    channel: 0
    device_id: MotorAxis0
    config:
      attributes:
        !!python/tuple [Sensor type, Value]: 1
        !!python/tuple [Position +limit, Value]: 15mm
        !!python/tuple [Position -limit, Value]: -15mm
        !!python/tuple [Position, Tolerance]: [10nm, 10nm]
"""


class DeviceSmaractMcs1(DeviceSocket):
    push_buffer_size = 50
    response_timeout = 3000
    terminator = b"\n"
    handtool_modes = frozenbidict({"Disabled": 0, "Enabled": 1, "Display only": 2})
    sensor_modes = frozenbidict({"Disabled": 0, "Enabled": 1, "Power safe": 2})
    channel_command_pattern = re.compile(":([A-Z]+)([-0-9]+),(.*)")
    linear_sensor_type = [None, 1, 5, 6, 9, 18, 21, 24, 32, 38, 40, 41, 42, 43, 44]
    sensor_types = [1, 2, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 23, 24, 32, 37, 38, 39, 40,
                    41, 42, 43, 44, 48, 49, 50, 51, 53, 54]
    safe_direction_modes = frozenbidict({"Forward": 0, "Backward": 1})

    def __init__(self, host, port=5000, device_id=None, config=None):
        super(DeviceSmaractMcs1, self).__init__(host, port, device_id, config)

    def _init_attributes(self):
        super(DeviceSmaractMcs1, self)._init_attributes()

        self.attributes.update({
            ATTR_STATE: Attribute(None, readonly=True, default_type=np.uint16),
            ATTR_SERIAL_NUMBER: Attribute(readonly=True),
            ATTR_CHANNELS: Attribute(None, readonly=True, default_type=np.uint16),
            ATTR_HAND_TOOL_MODE: Attribute("Display only", default_type=self.handtool_modes.keys(),
                                           set_function=self.set_hand_tool_mode),
            ATTR_SENSOR_MODE: Attribute(None, default_type=self.sensor_modes.keys(), set_function=self.set_sensor_mode,
                                        set_value_when_set_function=True),
            ATTR_SENSOR_PRESENT: Attribute(True, readonly=True, default_type=np.bool),
        })

    def valid_command_format(self, command):
        if command is not None and command[-1] == "\n":
            return True
        else:
            return False

    def handle_configuration(self):
        start_at = time.time()

        def _finish_configuration(*_, **__):
            self._config_commands()
            self._config_attributes()
            self.set_status(STATUS_CONFIGURED)
            self.logger.info(u"Device configuration took {} sec.".format(time.time() - start_at))

        # Set communication to synchronous
        self.command(u":SCM0\n")
        # Set hand-tool mode to just display positions
        self.set_hand_tool_mode("Display only")
        # Get Interface version
        self.command(u":GSI\n")
        # Get number of channels
        self.command(u":GNC\n")
        # Get Interface version
        self.command(u":GSE\n", callback=_finish_configuration)

    def handle_readout(self, readout_buffer):
        command, output, callback, token = super(DeviceSmaractMcs1, self).handle_readout(readout_buffer)

        if output[:2] == ":E":
            channel, error_number = [int(v) for v in output[2:].split(",")]
            if error_number > 0:
                # if error_number == 129:
                #     self.set_value(ATTR_SENSOR_PRESENT, False)
                #     self.set_value(ATTR_SENSOR_MODE, "Disabled")
                # for channel in range(self[ATTR_CHANNELS][VALUE]):
                #     self.notify((channel, ATTR_SENSOR_MODE), "Disabled")
                #     self.notify((channel, ATTR_SENSOR_PRESENT), False)
                # elif error_number == 140:
                #     self.set_value(ATTR_SENSOR_MODE, "Disabled")
                # for channel in range(self[ATTR_CHANNELS][VALUE]):
                #     self.notify((channel, ATTR_SENSOR_MODE), "Disabled")
                self.handle_command_error(command, output)
        elif command == ":GSI\n":
            self.set_value(ATTR_SERIAL_NUMBER, output.strip(":IN"))
        elif command == ":GNC\n":
            channels = int(output.strip(":N"))
            self.set_value(ATTR_CHANNELS, channels)
        elif command == ":GSE\n":
            mode = self.sensor_modes.inv[int(output.strip(":SE"))]
            self.set_value(ATTR_SENSOR_MODE, mode)
            for channel in range(self[ATTR_CHANNELS][VALUE]):
                self.notify((channel, ATTR_SENSOR_MODE), mode)
        elif output[:3] == ":BR":
            pass
        else:
            find = self.channel_command_pattern.search(output)
            if find is not None and find != -1:
                attribute = None
                cmd, channel, value = find.group(1), int(find.group(2)), find.group(3)
                if cmd == "S":
                    attribute, value = ATTR_STATE, int(value)
                elif cmd == "P":
                    attribute, value = ATTR_POSITION, int(value)
                elif cmd == "A":
                    position, revolutions = value.split(",")
                    self.notify((channel, ATTR_REVOLUTIONS), int(revolutions))
                    attribute, value = ATTR_POSITION, int(position)
                elif cmd == "ST":
                    attribute, value = ATTR_SENSOR_TYPE, int(value)
                elif cmd == "PPK":
                    attribute, value = ATTR_REFERENCED, bool(int(value))
                elif cmd == "SD":
                    safe_direction = self.safe_direction_modes.inv[int(value)]
                    attribute, value = ATTR_SAFE_DIRECTION, safe_direction
                elif cmd == "CLA":
                    attribute, value = ATTR_ACCELERATION, int(value)
                elif cmd == "CLS":
                    attribute, value = ATTR_VELOCITY, int(value)
                elif cmd == "AL":
                    min_position, min_revolution, max_position, max_revolution = [int(i) for i in value.split(",")]
                    attribute, value = ATTR_POSITION_LOWER_LIMIT, (min_position, min_revolution)
                    self.notify((channel, ATTR_POSITION_UPPER_LIMIT), (max_position, max_revolution))
                elif cmd == "PL":
                    min_position, max_position = value.split(",")
                    attribute, value = ATTR_POSITION_LOWER_LIMIT, int(min_position)
                    self.notify((channel, ATTR_POSITION_UPPER_LIMIT), int(max_position))
                if attribute:
                    self.notify((channel, attribute), value)

        if callback is not None:
            self.handle_readout_callback(callback, command, readout_buffer)
        if token:
            self.device_server.push_message(self.device_id, [command, readout_buffer], token)
            for observer in self._observers[:]:
                if isinstance(observer, DeviceSmaractMcs1Channel):
                    self.device_server.push_message(observer.device_id, [command, readout_buffer], token)

        # if callback is not None:
        #     self.handle_readout_callback(callback, command, readout_buffer)
        # if token:
        #     self.device_server.push_message(self.device_id, readout_buffer, token)
        #
        #     for observer in self._observers[:]:
        #         if isinstance(observer, DeviceSmaractMcs1Channel):
        #             self.device_server.push_message(observer.device_id, readout_buffer, token)

    def set_hand_tool_mode(self, value):
        self.logger.info(u"Set hand tool mode to {}".format(value))
        int_mode = self.handtool_modes[value]
        self.command(u":SHE{}\n".format(int_mode))

    def set_sensor_mode(self, value):
        self.logger.info(u"Set sensor mode to {}".format(value))
        for channel in range(self[ATTR_CHANNELS][VALUE]):
            self.notify((channel, ATTR_SENSOR_MODE), value)

        value = self.sensor_modes[value]
        self.command(u":SSE{}\n".format(value))


class DeviceSmaractMcs1Port(DevicePort, DeviceSmaractMcs1):
    push_buffer_size = DeviceSmaractMcs1.push_buffer_size
    response_timeout = DeviceSmaractMcs1.response_timeout
    terminator = DeviceSmaractMcs1.terminator

    def __init__(self, port, baud_rate=9600, parity=serial.PARITY_NONE, stop_bits=serial.STOPBITS_ONE,
                 byte_size=serial.EIGHTBITS, device_id=None, config=None):
        super(DeviceSmaractMcs1Port, self).__init__(port, baud_rate, parity, stop_bits, byte_size, device_id, config)

    def _init_attributes(self):
        super(DeviceSmaractMcs1Port, self)._init_attributes()
        self.attributes.update({
            ATTR_BAUDRATE: Attribute(self.baud_rate, readonly=False, default_type=self.BAUDRATES,
                                     set_function=self.set_baudrate)
        })

    def handshake(self):
        self.logger.info(u"Handshake initiated")
        self.push(b":SCM0\n")
        time.sleep(0.05)  # Give some time for devices to reply
        if self.serial_port.in_waiting != 0:
            if self.read_all().strip() == ":E-1,0":
                return True
        return False

    def set_baudrate(self, value):
        self.logger.info(u"Set baud-rate to {}".format(value))
        self.command(u":CB{}\n".format(int(value)))


class DeviceSmaractMcs1Channel(DeviceChannel):
    sensor_types = DeviceSmaractMcs1.sensor_types
    linear_sensor_type = DeviceSmaractMcs1.linear_sensor_type
    sensor_modes = DeviceSmaractMcs1.sensor_modes
    safe_direction_modes = DeviceSmaractMcs1.safe_direction_modes

    def handle_configuration(self):
        if self.configured:
            return

        start_at = time.time()

        def _finish_configuration(*_, **__):
            self._config_commands()
            self._config_attributes()
            self.get_position_limit_range()
            self.start_polling()
            self.set_status(STATUS_CONFIGURED)
            self.logger.info(u"Device configuration took {} sec.".format(time.time() - start_at))

        self.connected = True
        self.get_sensor_type()
        self.get_acceleration()
        self.get_safe_direction()
        self.command(u":GCLS{}\n".format(self.channel), callback=_finish_configuration)

    def _init_attributes(self):
        super(DeviceSmaractMcs1Channel, self)._init_attributes()

        self.attributes.update({
            ATTR_STATE: Attribute(None, readonly=True, default_type=np.uint16),
            ATTR_MOVING: Attribute(None, readonly=True, default_type=np.bool),
            ATTR_POSITION: Attribute(None, default_type=np.int64, set_function=self._move_absolute,
                                     set_value_when_set_function=False),
            ATTR_REVOLUTIONS: Attribute(None, readonly=True, default_type=np.int64),
            ATTR_CALIBRATING: Attribute(None, readonly=True, default_type=np.bool),
            ATTR_REFERENCING: Attribute(None, readonly=True, default_type=np.bool),
            ATTR_CALIBRATED: Attribute(None, readonly=True, default_type=np.bool),
            ATTR_REFERENCED: Attribute(None, readonly=True, default_type=np.bool),
            ATTR_MOVEMENT_LOCKED: Attribute(None, readonly=True, default_type=np.bool),
            ATTR_SENSOR_MODE: Attribute(None, readonly=True, default_type=self.sensor_modes.keys()),
            ATTR_SENSOR_TYPE: Attribute(None, default_type=self.sensor_types, set_function=self.set_sensor_type),
            ATTR_SENSOR_PRESENT: Attribute(True, readonly=True, default_type=np.bool),
            ATTR_ENCODER_BASE_UNIT: Attribute(None, readonly=True),
            ATTR_ENCODER_RESOLUTION: Attribute(None, readonly=True, default_type=np.int8),
            ATTR_POSITION_LOWER_LIMIT: Attribute(None, default_type=np.int64,
                                                 set_function=self.set_lower_position_limit),
            ATTR_POSITION_UPPER_LIMIT: Attribute(None, default_type=np.int64,
                                                 set_function=self.set_upper_position_limit),
            ATTR_STEP_FREQUENCY: Attribute(1000, default_type=np.uint32, min_value=1, max_value=18.5e3, unit="Hz",
                                           set_function=self.set_step_frequency),
            ATTR_STEP_AMPLITUDE: Attribute(1000, default_type=np.uint32, min_value=1, max_value=65535,
                                           set_function=self.set_step_amplitude),
            ATTR_ACCELERATION: Attribute(None, default_type=np.int64, min_value=0, max_value=100e9,
                                         set_function=self.set_acceleration),
            ATTR_VELOCITY: Attribute(None, default_type=np.int64, min_value=0, max_value=1e8,
                                     set_function=self.set_velocity),
            ATTR_SAFE_DIRECTION: Attribute(None, default_type=self.safe_direction_modes.keys(),
                                           set_function=self.set_safe_direction),
            ATTR_HOLDING_TIME: Attribute(0, default_type=np.uint16, min_value=0, max_value=60e3, unit=u"ms"),
        })

    def subject_update(self, key, value, subject):
        super(DeviceSmaractMcs1Channel, self).subject_update(key, value, subject)

        if self.connected and isinstance(key, tuple) and key[0] == self.channel:
            attribute = key[1]
            if attribute == ATTR_STATE and self.get_value(ATTR_STATE) != value:
                if value in (0, 3):
                    self.set_status(STATUS_IDLE)
                    self.set_value(ATTR_CALIBRATING, False)
                    self.set_value(ATTR_REFERENCING, False)
                    self.set_value(ATTR_MOVING, False)
                else:
                    self.set_status(STATUS_BUSY)
                    if value in (1, 2, 4, 6, 7):
                        self.set_value(ATTR_MOVING, True)

                        if value == 6:
                            self.set_value(ATTR_CALIBRATING, True)
                        elif value == 7:
                            self.set_value(ATTR_REFERENCING, True)
                        elif value == 9:
                            self.set_value(ATTR_MOVEMENT_LOCKED, True)
            elif attribute == ATTR_SENSOR_TYPE:
                self._set_position_unit(value)
                self._set_position_polling(value)
                self.get_referenced()
                self.get_position_limit_range(value)
            elif attribute == ATTR_SENSOR_PRESENT:
                if not value:
                    self.remove_poll_command(":GP{}\n".format(self.channel), 200)
                    self.remove_poll_command(":GA{}\n".format(self.channel), 200)
                else:
                    self._set_position_polling(self[ATTR_SENSOR_TYPE][VALUE])
            elif attribute == ATTR_SENSOR_MODE:
                if value == "Disabled":
                    self.remove_poll_command(":GP{}\n".format(self.channel), 200)
                    self.remove_poll_command(":GA{}\n".format(self.channel), 200)
                else:
                    self._set_position_polling(self[ATTR_SENSOR_TYPE][VALUE])
            elif attribute == ATTR_POSITION and self[ATTR_REVOLUTIONS][VALUE] != 0:
                revolution = 360 * 10 ** abs(self[ATTR_ENCODER_RESOLUTION][VALUE])
                value += self[ATTR_REVOLUTIONS][VALUE] * revolution
            elif attribute == ATTR_POSITION_LOWER_LIMIT and self[ATTR_SENSOR_TYPE][
                VALUE] not in self.linear_sensor_type:
                revolution = 360 * 10 ** abs(self[ATTR_ENCODER_RESOLUTION][VALUE])
                min_position, min_revolutions = value
                value = min_position + min_revolutions * revolution
                # self.set_attribute([ATTR_POSITION, MIN], value)
            elif attribute == ATTR_POSITION_UPPER_LIMIT and self[ATTR_SENSOR_TYPE][
                VALUE] not in self.linear_sensor_type:
                revolution = 360 * 10 ** abs(self[ATTR_ENCODER_RESOLUTION][VALUE])
                max_position, max_revolutions = value
                value = max_position + max_revolutions * revolution
                # self.set_attribute([ATTR_POSITION, MAX], value)
            self.set_attribute((ATTR_LATENCY, VALUE), self.device.get_value(ATTR_LATENCY))
            self.set_value(attribute, value)

    def _set_position_unit(self, sensor_type):
        if sensor_type is None:
            return

        prefix = {-12: "p", -9: "n", -6: "u", -3: "m"}
        if sensor_type in self.linear_sensor_type:
            resolution = -9
            unit = "m"
        else:
            resolution = -6
            unit = "deg"
        base_position_unit = prefix.get(resolution, "") + unit
        self.set_attribute((ATTR_ENCODER_RESOLUTION, VALUE), resolution)
        self.set_attribute((ATTR_ENCODER_BASE_UNIT, VALUE), unit)
        self.set_attribute((ATTR_POSITION, UNIT), base_position_unit)
        self.set_attribute((ATTR_POSITION_UPPER_LIMIT, UNIT), base_position_unit)
        self.set_attribute((ATTR_POSITION_LOWER_LIMIT, UNIT), base_position_unit)
        self.set_attribute((ATTR_ACCELERATION, UNIT), "{}/s".format(base_position_unit))
        self.set_attribute((ATTR_VELOCITY, UNIT), "{}/s".format(base_position_unit))

    def _set_position_polling(self, sensor_type):
        if sensor_type is None:
            return
        elif sensor_type in self.linear_sensor_type:
            self.poll_command(":GP{}\n".format(self.channel), 200)
            self.set_value(ATTR_REVOLUTIONS, 0)
        else:
            self.poll_command(":GA{}\n".format(self.channel), 200)

    def start_polling(self):
        super(DeviceSmaractMcs1Channel, self).start_polling()
        self.poll_command(":GS{}\n".format(self.channel), 200)

    def stop_polling(self):
        self.remove_poll_command(":GS{}\n".format(self.channel), 200)
        self.remove_poll_command(":GP{}\n".format(self.channel), 200)
        self.remove_poll_command(":GA{}\n".format(self.channel), 200)

    def _move_absolute(self, value, callback=None):
        self.logger.info(u"Move to position {}".format(value))
        holding_time = self.get_value(ATTR_HOLDING_TIME)
        if self[ATTR_SENSOR_TYPE][VALUE] in self.linear_sensor_type:
            return self.command(u":MPA{},{},{}\n".format(self.channel, int(value), holding_time), callback,
                                with_token=True)
        else:
            revolution = 360 * 10 ** abs(self[ATTR_ENCODER_RESOLUTION][VALUE])
            revolutions = int(value // revolution)
            angular_position = int(value - revolutions * revolution)
            return self.command(u":MAA{},{},{},{}\n".format(self.channel, angular_position, revolutions, holding_time),
                                callback,
                                with_token=True)

    def _move_relative(self, value, callback=None):
        self.logger.info(u"Move by relative position {}".format(value))
        holding_time = self.get_value(ATTR_HOLDING_TIME)
        if self[ATTR_SENSOR_TYPE][VALUE] in self.linear_sensor_type:
            return self.command(u":MPR{},{},{}\n".format(self.channel, int(value), holding_time), callback,
                                with_token=True)
        else:
            revolution = 360 * 10 ** abs(self[ATTR_ENCODER_RESOLUTION][VALUE])
            revolutions = int(value // revolution)
            angular_position = int(value - revolutions * revolution)
            return self.command(u":MAR{},{},{},{}\n".format(self.channel, angular_position, revolutions, holding_time),
                                callback,
                                with_token=True)

    @expose_method()
    def stop(self, callback=None):
        self.logger.info(u"Stop movement")
        return self.command(u":S{}\n".format(self.channel), callback, with_token=True)

    @expose_method()
    def calibrate(self, callback=None):
        self.logger.info(u"Calibrate")
        return self.command(u":CS{}\n".format(self.channel), callback, with_token=True)

    @expose_method()
    def find_reference(self, callback=None):
        self.logger.info(u"Reference")
        reference_direction = self.safe_direction_modes[self.get_value(ATTR_SAFE_DIRECTION)]
        return self.command(u":FRM{},{},0,1\n".format(self.channel, reference_direction), callback, with_token=True)

    @expose_method({"position": ATTR_POSITION})
    def move_absolute(self, position):
        try:
            position = device_units(self, ATTR_POSITION, position)
            self.logger.info(u"Move to absolute position {}".format(position))
            return self.set_attribute((ATTR_POSITION, VALUE), position)
        except (UndefinedUnitError, ValueError) as e:
            self.logger.exception(e)
            raise DeviceUnitError(e)

    @expose_method({"position": ATTR_POSITION})
    def move_relative(self, position):
        try:
            position = device_units(self, ATTR_POSITION, position)
            self.logger.info(u"Move by relative position {}".format(position))
            return self.set_attribute((ATTR_POSITION, VALUE), self[ATTR_POSITION].value() + position)
        except (UndefinedUnitError, ValueError) as e:
            self.logger.exception(e)
            raise DeviceUnitError(e)

    @expose_method({"steps": "Number of steps", "amplitude": ATTR_STEP_AMPLITUDE, "frequency": ATTR_STEP_FREQUENCY})
    def move_step(self, steps, amplitude=None, frequency=None, callback=None):
        if amplitude in (None, ""):
            amplitude = self[ATTR_STEP_AMPLITUDE][VALUE]
        else:
            amplitude = device_units(self, ATTR_STEP_AMPLITUDE, amplitude).m
        if frequency in (None, ""):
            frequency = self[ATTR_STEP_FREQUENCY][VALUE]
        else:
            frequency = device_units(self, ATTR_STEP_FREQUENCY, frequency).m
        amplitude = int(self[ATTR_STEP_AMPLITUDE].remove_offset_factor(amplitude))
        frequency = int(self[ATTR_STEP_FREQUENCY].remove_offset_factor(frequency))
        self.logger.info(u"Move by {} steps with amplitude {} and frequency of {} Hz".format(int(steps), int(amplitude),
                                                                                             int(frequency)))
        return self.command(u":MST{},{},{},{}\n".format(self.channel, int(steps), amplitude, frequency), callback,
                            with_token=True)

    def get_sensor_type(self):
        self.command(u":GST{}\n".format(self.channel))

    def get_position_limit_range(self, sensor_type=None):
        if sensor_type in self.linear_sensor_type:
            self.command(u":GPL{}\n".format(self.channel))
        else:
            self.command(u":GAL{}\n".format(self.channel))

    def get_velocity(self):
        self.command(u":GCLS{}\n".format(self.channel))

    def get_acceleration(self):
        self.command(u":GCLA{}\n".format(self.channel))

    def get_safe_direction(self):
        self.command(u":GSD{}\n".format(self.channel))

    def get_referenced(self):
        self.command(u":GPPK{}\n".format(self.channel))

    def set_sensor_type(self, value, callback=None):
        self.logger.info(u"Set sensor type to {}".format(value))
        if value != self.get_value(ATTR_SENSOR_TYPE):
            self.remove_poll_command(":GP{}\n".format(self.channel), 200)
            self.remove_poll_command(":GA{}\n".format(self.channel), 200)

            token = self.command(u":SST{},{}\n".format(self.channel, int(value)), callback, with_token=True)
            self.get_sensor_type()
            return token

    def set_lower_position_limit(self, value, callback=None):
        self.logger.info(u"Set lower position limit to {}".format(value))
        upper_limit = self[ATTR_POSITION_UPPER_LIMIT][VALUE]
        # self.set_value(ATTR_POSITION_LOWER_LIMIT, int(value))
        if upper_limit is None:
            upper_limit = value
            # self.set_value(ATTR_POSITION_UPPER_LIMIT, upper_limit)
        if int(self[ATTR_SENSOR_TYPE][VALUE]) in self.linear_sensor_type:
            out = self.command(u":SPL{},{},{}\n".format(self.channel, int(value), int(upper_limit)), with_token=True)
        else:
            revolution = 360 * 10 ** abs(self[ATTR_ENCODER_RESOLUTION][VALUE])
            min_revolutions = int(value // revolution)
            min_angular_position = int(value - min_revolutions * revolution)
            max_revolutions = int(upper_limit // revolution)
            max_angular_position = int(upper_limit - max_revolutions * revolution)
            out = self.command(
                u":SAL{},{},{},{},{}\n".format(self.channel, int(min_angular_position), int(min_revolutions),
                                               int(max_angular_position), int(max_revolutions)), callback,
                with_token=True)

        self.set_attribute([ATTR_POSITION, MIN], self[ATTR_POSITION].remove_offset_factor(value))
        self.get_position_limit_range()
        return out

    def set_upper_position_limit(self, value, callback=None):
        self.logger.info(u"Set upper position limit to {}".format(value))
        lower_limit = self[ATTR_POSITION_LOWER_LIMIT][VALUE]
        # self.set_value(ATTR_POSITION_UPPER_LIMIT, int(value))
        if lower_limit is None:
            lower_limit = value
            # self.set_value(ATTR_POSITION_LOWER_LIMIT, lower_limit)
        if int(self[ATTR_SENSOR_TYPE][VALUE]) in self.linear_sensor_type:
            out = self.command(u":SPL{},{},{}\n".format(self.channel, int(value), int(lower_limit)), callback,
                               with_token=True)
        else:
            revolution = 360 * 10 ** abs(self[ATTR_ENCODER_RESOLUTION][VALUE])
            max_revolutions = int(value // revolution)
            max_angular_position = int(value - max_revolutions * revolution)
            min_revolutions = int(lower_limit // revolution)
            min_angular_position = int(lower_limit - min_revolutions * revolution)
            out = self.command(
                u":SAL{},{},{},{},{}\n".format(self.channel, int(min_angular_position), int(min_revolutions),
                                               int(max_angular_position), int(max_revolutions)), callback,
                with_token=True)

        self.set_attribute([ATTR_POSITION, MAX], self[ATTR_POSITION].remove_offset_factor(value))
        self.get_position_limit_range()
        return out

    def set_step_frequency(self, value, callback=None):
        self.logger.info(u"Set step frequency to {} Hz".format(value))
        return self.command(u":SCLF{},{}\n".format(self.channel, int(value)), callback, with_token=True)

    def set_step_amplitude(self, value):
        self.logger.info(u"Set step amplitude to {}".format(value))
        self[ATTR_STEP_AMPLITUDE][VALUE] = value

    def set_velocity(self, value, callback=None):
        self.logger.info(u"Set velocity to {}".format(value))
        return self.command(u":SCLS{},{}\n".format(self.channel, int(value)), callback, with_token=True)

    def set_acceleration(self, value, callback=None):
        self.logger.info(u"Set acceleration to {}".format(value))
        return self.command(u":SCLA{},{}\n".format(self.channel, int(value)), callback, with_token=True)

    def set_safe_direction(self, value, callback=None):
        self.logger.info(u"Set safe direction to {}".format(value))
        value = self.safe_direction_modes[value]
        return self.command(u":SSD{},{}\n".format(self.channel, value), callback, with_token=True)
