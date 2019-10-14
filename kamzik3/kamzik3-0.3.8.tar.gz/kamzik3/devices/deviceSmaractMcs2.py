import re
import time

import numpy as np
from bidict import frozenbidict
from pint.errors import UndefinedUnitError

import kamzik3
from kamzik3 import DeviceError, CommandFormatException, DeviceUnitError
from kamzik3.constants import *
from kamzik3.devices.attribute import Attribute
from kamzik3.devices.deviceChannel import DeviceChannel
from kamzik3.devices.deviceSocket import DeviceSocket
from kamzik3.devices.general.deviceScanner import DeviceScanner
from kamzik3.snippets.snippetsDecorators import expose_method
from kamzik3.snippets.snippetsUnits import device_units

""" Example of yaml configuration
Smaract0: &Smaract0 !Device:kamzik3.devices.deviceSmaractMcs1.DeviceSmaractMcs2
    device_id: Smaract0
    host: 192.168.83.91
Smaract0_axis_0: &Smaract0_axis_0 !Device:kamzik3.devices.deviceSmaractMcs1.DeviceSmaractMcs1Channe2
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

"""
Positioner codes:
SL...S1SS 300 Linear positioner, single piezo element
SL...D1SS 301 Linear positioner, double piezo element
SL...S1SC1 303 Linear positioner, single piezo element
SL...D1SC1 304 Linear positioner, double piezo element
SL...D1SC2 307 Linear positioner, double piezo element
SR...S1S5S 309 Small rotary positioner S single mark
SR...S1S6S 312 Rotary positioner S single mark
SR...D1S6S 313 Rotary positioner, double piezo element
SR...D1S7S 316 Rotary positioner, double piezo element
SR...T1S8S 320 Large rotary positioner S single mark
SG...D1S1S 325 Goniometer, 60.5mm radius, double
SG...D1S2S 328 Goniometer, 77.5mm radius, double
SL...S1LE 342 Linear positioner, single piezo element
SL...D1LE 343 Linear positioner, double piezo element
SL...S1LS 345 Linear positioner, single piezo element
SL...D1LS 346 Linear positioner, double piezo element
SL...S1LC1 348 Linear positioner, single piezo element
SL...D1LC1 349 Linear positioner, double piezo element
SR...S1L2S 354 Rotary positioner L single mark
SR...D1L2S 355 Rotary positioner, double piezo element
SL...S1ME 357 Linear positioner, single piezo element
SL...D1ME 358 Linear positioner, double piezo element
SL...S1P1E 360 Linear positioner, double piezo element
SL...D1P1E 361 Linear positioner, double piezo element
SG...S1M1E 363 Goniometer, 60.5mm radius, single
SG...S1M2E 366 Goniometer, 77.5mm radius, single
SG...D1L1S 381 Goniometer, 60.5mm radius, double
SG...D1L2S 383 Goniometer, 77.5mm radius, double
SG...D1L1E 387 Goniometer, 60.5mm radius, double
SG...D1L2E 389 Goniometer, 77.5mm radius, double
SH...A1SS 395 High load table, single piezo element S single mark
"""


class DeviceSmaractMcs2(DeviceSocket):
    response_timeout = 3000
    terminator = b"\r\n"
    error_pattern = re.compile('([-0-9]+),\"([\w ]+)"')
    sensor_modes = frozenbidict({"Disabled": 0, "Enabled": 1, "Power safe": 2})
    move_modes = frozenbidict({"Absolute": 0, "Relative": 1, "Scan absolute": 2, "Scan relative": 3, "Step": 4})
    safe_direction_modes = frozenbidict({"Forward": 0, "Backward": 1})

    def __init__(self, host, port=55551, device_id=None, config=None):
        super(DeviceSmaractMcs2, self).__init__(host, port, device_id, config)

    def _init_attributes(self):
        super(DeviceSmaractMcs2, self)._init_attributes()

        self.attributes.update({
            ATTR_STATE: Attribute(None, readonly=True, default_type=np.uint16),
            ATTR_SERIAL_NUMBER: Attribute(readonly=True),
            ATTR_CHANNELS: Attribute(None, readonly=True, default_type=np.uint16),
            ATTR_MODULES: Attribute(None, readonly=True, default_type=np.uint16),
            ATTR_HAND_TOOL: Attribute(None, readonly=True, default_type=np.bool),
            ATTR_MOVEMENT_LOCKED: Attribute(None, readonly=True, default_type=np.bool),
            ATTR_INTERNAL_COMM_FAILURE: Attribute(None, readonly=True, default_type=np.bool),
            ATTR_STREAMING: Attribute(None, readonly=True, default_type=np.bool),
        })

    def command(self, command, callback=None, with_token=False, returning=True):
        if not self.valid_command_format(command):
            raise CommandFormatException(u"Command '{}' form is invalid".format(command))

        returning = True
        command += ":SYST:ERR:NEXT?\r\n"
        return super(DeviceSmaractMcs2, self).command(command, callback, with_token, returning)

    def poll_command(self, command, interval):
        if not self.valid_command_format(command):
            raise CommandFormatException(u"Command '{}' form is invalid".format(command))

        command += ":SYST:ERR:NEXT?\r\n"
        super(DeviceSmaractMcs2, self).poll_command(command, interval)

    def handle_configuration(self):

        start_at = time.time()

        def _finish_configuration(*_, **__):
            self._config_commands()
            self._config_attributes()
            self.set_status(STATUS_CONFIGURED)
            self.logger.info(u"Device configuration took {} sec.".format(time.time() - start_at))

        # Check for possible errors
        self.get_errors_count()
        # Get number of channels
        self.command(u":DEV:NOCH?\r\n")
        # Get serial number
        self.command(u":DEV:SNUM?\r\n")
        # Get number of modules
        self.command(u":DEV:NOBM?\r\n", callback=_finish_configuration)

        self.start_polling()

    def handle_configuration_event(self):
        try:
            start_at = time.time()
            self.set_status(STATUS_CONFIGURING)
            self.handle_configuration()
            self.logger.info(u"Device configuration took {} sec.".format(time.time() - start_at))
        except DeviceError:
            self.logger.exception(u"Error during configuration")

    def valid_command_format(self, command):
        if command is not None and command[-2:] == "\r\n":
            return True
        else:
            return False

    def handle_readout(self, readout_buffer):
        is_error_message = self.error_pattern.match(readout_buffer[0])
        command, output, callback, token = super(DeviceSmaractMcs2, self).handle_readout(readout_buffer)
        if is_error_message is not None:
            if command == ":SYST:ERR:NEXT?\r\n" and int(is_error_message.group(1)) != 0:
                self.logger.error(readout_buffer[0])
            elif int(is_error_message.group(1)) != 0:
                self.logger.error(readout_buffer[0])

            if callback is not None:
                self.handle_readout_callback(callback, command, readout_buffer)
            if token:
                self.device_server.push_message(self.device_id, [command, readout_buffer], token)
                for observer in self._observers[:]:
                    if isinstance(observer, DeviceSmaractMcs2Channel):
                        self.device_server.push_message(observer.device_id, [command, readout_buffer], token)
            return
        else:
            command = command.replace(":SYST:ERR:NEXT?\r\n", "")
            self.commands_buffer.appendleft(((":SYST:ERR:NEXT?\r\n", None, None, True), time.time()))

        command = command.strip()

        if command == ":DEV:NOCH?":
            self.set_attribute((ATTR_CHANNELS, VALUE), int(output))
        elif command == ":DEV:SNUM?":
            self.set_attribute((ATTR_SERIAL_NUMBER, VALUE), output.replace('"', ""))
        elif command == ":DEV:NOBM?":
            self.set_attribute((ATTR_MODULES, VALUE), int(output))
            for i in range(int(output)):
                module_name = "Module{}".format(i)
                self.attributes[module_name] = {
                    ATTR_STATE: Attribute(None, readonly=True, default_type=np.uint16),
                    ATTR_TEMPERATURE: Attribute(readonly=True, default_type=np.float32, decimals=2, unit="degC", ),
                    ATTR_SENSOR_PRESENT: Attribute(None, readonly=True, default_type=np.bool),
                    ATTR_BOOSTER_PRESENT: Attribute(None, readonly=True, default_type=np.bool),
                    ATTR_ADJUSTMENT_ACTIVE: Attribute(None, readonly=True, default_type=np.bool),
                    ATTR_IOM_PRESENT: Attribute(None, readonly=True, default_type=np.bool),
                    ATTR_INTERNAL_COMM_FAILURE: Attribute(None, readonly=True, default_type=np.bool),
                    ATTR_HIGH_VOLTAGE_FAILURE: Attribute(None, readonly=True, default_type=np.bool),
                    ATTR_HIGH_VOLTAGE_OVERLOAD: Attribute(None, readonly=True, default_type=np.bool),
                    ATTR_OVER_TEMPERATURE: Attribute(None, readonly=True, default_type=np.bool),
                }
                self.poll_command(":MOD{}:STAT?\r\n".format(i), 2000)
                self.poll_command(":MOD{}:TEMP?\r\n".format(i), 2000)
        elif command == ":DEV:STAT?":
            output = int(output)
            self.set_attribute((ATTR_STATE, VALUE), output)
            self.set_attribute((ATTR_HAND_TOOL, VALUE), bool(output % 0x0001))
            self.set_attribute((ATTR_MOVEMENT_LOCKED, VALUE), bool(output % 0x0002))
            self.set_attribute((ATTR_INTERNAL_COMM_FAILURE, VALUE), bool(output % 0x0100))
            self.set_attribute((ATTR_STREAMING, VALUE), bool(output % 0x1000))
        elif command == ":SYST:ERR:COUN?":
            if int(output) > 0:
                self.get_next_error()
        elif command == ":SYST:ERR:NEXT?":
            self.logger.error(output)
            self.get_errors_count()
        elif command[:4] == ":MOD":
            _, module, attribute = command.split(":")
            module_name = "Module{}".format(module[3:])
            if attribute == "TEMP?":
                self.set_attribute((module_name, ATTR_TEMPERATURE, VALUE), float(output))
            elif attribute == "STAT?":
                output = int(output)
                self.set_attribute((module_name, ATTR_STATE, VALUE), output)
                self.set_attribute((module_name, ATTR_SENSOR_PRESENT, VALUE), bool(output & 0x0001))
                self.set_attribute((module_name, ATTR_BOOSTER_PRESENT, VALUE), bool(output & 0x0002))
                self.set_attribute((module_name, ATTR_ADJUSTMENT_ACTIVE, VALUE), bool(output & 0x0004))
                self.set_attribute((module_name, ATTR_IOM_PRESENT, VALUE), bool(output & 0x0008))
                self.set_attribute((module_name, ATTR_INTERNAL_COMM_FAILURE, VALUE), bool(output & 0x0100))
                self.set_attribute((module_name, ATTR_HIGH_VOLTAGE_FAILURE, VALUE), bool(output & 0x1000))
                self.set_attribute((module_name, ATTR_HIGH_VOLTAGE_OVERLOAD, VALUE), bool(output & 0x2000))
                self.set_attribute((module_name, ATTR_OVER_TEMPERATURE, VALUE), bool(output & 0x4000))
        elif command[:5] == ":CHAN":
            chunks = command.split(":")
            channel, attribute = chunks[1], chunks[-1]
            channel = int(channel[4:])
            if attribute == "STAT?":
                attribute, output = ATTR_STATE, int(output)
            elif attribute == "CURR?":
                attribute, output = ATTR_POSITION, int(output)
            elif attribute == "TARG?":
                attribute, output = ATTR_TARGET_POSITION, int(output)
            elif attribute == "TEMP?":
                attribute, output = ATTR_TEMPERATURE, float(output)
            elif attribute == "UNIT?":
                attribute, output = ATTR_ENCODER_BASE_UNIT, int(output)
            elif attribute == "RES?":
                attribute, output = ATTR_ENCODER_RESOLUTION, int(output)
            elif attribute == "NAME?":
                attribute, output = ATTR_POSITIONER_TYPE, output.replace('"', "")
            elif attribute == "CODE?":
                attribute, output = ATTR_POSITIONER_CODE, int(output)
            elif attribute == "MIN?":
                attribute, output = ATTR_POSITION_LOWER_LIMIT, int(output)
            elif attribute == "MAX?":
                attribute, output = ATTR_POSITION_UPPER_LIMIT, int(output)
            elif attribute == "FREQ?":
                attribute, output = ATTR_STEP_FREQUENCY, int(output)
            elif attribute == "AMPL?":
                attribute, output = ATTR_STEP_AMPLITUDE, int(output)
            elif attribute == "VEL?":
                attribute, output = ATTR_VELOCITY, int(output)
            elif attribute == "HOLD?":
                attribute, output = ATTR_HOLDING_TIME, int(output)
            elif attribute == "ACC?":
                attribute, output = ATTR_ACCELERATION, int(output)
            elif attribute == "MODE?":
                attribute, output = ATTR_SENSOR_MODE, self.sensor_modes.inv[int(output)]
            elif attribute == "MMOD?":
                attribute, output = ATTR_MOVE_MODE, self.move_modes.inv[int(output)]
            elif attribute == "SDIR?":
                attribute, output = ATTR_SAFE_DIRECTION, self.safe_direction_modes.inv[int(output)]
            else:
                return
            self.notify((channel, attribute), output)

        if callback is not None:
            self.handle_readout_callback(callback, command, readout_buffer)
        if token:
            self.device_server.push_message(self.device_id, [command, readout_buffer], token)
            for observer in self._observers[:]:
                if isinstance(observer, DeviceSmaractMcs2Channel):
                    self.device_server.push_message(observer.device_id, [command, readout_buffer], token)

    def start_polling(self):
        super(DeviceSmaractMcs2, self).start_polling()
        self.poll_command(":DEV:STAT?\r\n", 1000)

    def get_errors_count(self):
        self.command(u":SYST:ERR:COUN?\r\n")

    def get_next_error(self):
        self.command(u":SYST:ERR:NEXT?\r\n")


class DeviceSmaractMcs2Channel(DeviceChannel):
    sensor_modes = DeviceSmaractMcs2.sensor_modes
    move_modes = DeviceSmaractMcs2.move_modes
    safe_direction_modes = DeviceSmaractMcs2.safe_direction_modes

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
        self.get_sensor_mode()
        self.get_encoder_unit()
        self.get_position_limit_range()
        self.get_positioner_configuration()
        self.get_step_frequency()
        self.get_step_amplitude()
        self.get_acceleration()
        self.get_velocity()
        self.get_move_mode()
        self.get_holding_time()
        self.command(u":CHAN{}:SDIR?\r\n".format(self.channel), callback=_finish_configuration)

    def _init_attributes(self):
        super(DeviceSmaractMcs2Channel, self)._init_attributes()

        self.attributes.update({
            ATTR_STATE: Attribute(None, readonly=True, default_type=np.uint16),
            ATTR_TEMPERATURE: Attribute(readonly=True, default_type=np.float16, decimals=2, unit="degC"),
            ATTR_MOVING: Attribute(None, readonly=True, default_type=np.bool),
            ATTR_POSITION: Attribute(None, readonly=False, default_type=np.int64, set_function=self._move_absolute,
                                     set_value_when_set_function=False),
            ATTR_TARGET_POSITION: Attribute(None, default_type=np.int64, set_function=self._move_absolute,
                                            set_value_when_set_function=False),
            ATTR_CLOSED_LOOP_ACTIVE: Attribute(None, readonly=True, default_type=np.bool),
            ATTR_CALIBRATING: Attribute(None, readonly=True, default_type=np.bool),
            ATTR_REFERENCING: Attribute(None, readonly=True, default_type=np.bool),
            ATTR_MOVE_DELAYED: Attribute(None, readonly=True, default_type=np.bool),
            ATTR_SENSOR_PRESENT: Attribute(None, readonly=True, default_type=np.bool),
            ATTR_CALIBRATED: Attribute(None, readonly=True, default_type=np.bool),
            ATTR_REFERENCED: Attribute(None, readonly=True, default_type=np.bool),
            ATTR_END_STOP_REACHED: Attribute(None, readonly=True, default_type=np.bool),
            ATTR_RANGE_LIMIT_REACHED: Attribute(None, readonly=True, default_type=np.bool),
            ATTR_FOLLOWING_LIMIT_REACHED: Attribute(None, readonly=True, default_type=np.bool),
            ATTR_MOVEMENT_FAILED: Attribute(None, readonly=True, default_type=np.bool),
            ATTR_STREAMING: Attribute(None, readonly=True, default_type=np.bool),
            ATTR_OVER_TEMPERATURE: Attribute(None, readonly=True, default_type=np.bool),
            ATTR_INDEX_MARK: Attribute(None, readonly=True, default_type=np.bool),
            ATTR_ENCODER_BASE_UNIT: Attribute(None, readonly=True),
            ATTR_ENCODER_RESOLUTION: Attribute(None, readonly=True, default_type=np.int8),
            ATTR_POSITIONER_CODE: Attribute(None, readonly=False, default_type=np.int8, min_value=300, max_value=395,
                                            set_function=self.set_positioner_code),
            ATTR_POSITIONER_TYPE: Attribute(None, readonly=True),
            ATTR_POSITION_LOWER_LIMIT: Attribute(None, default_type=np.int64,
                                                 set_function=self.set_lower_position_limit),
            ATTR_POSITION_UPPER_LIMIT: Attribute(None, default_type=np.int64,
                                                 set_function=self.set_upper_position_limit),
            ATTR_STEP_FREQUENCY: Attribute(None, default_type=np.uint32, min_value=1, max_value=20e3, unit="Hz",
                                           set_function=self.set_step_frequency),
            ATTR_STEP_AMPLITUDE: Attribute(None, default_type=np.uint32, min_value=1, max_value=65535,
                                           set_function=self.set_step_amplitude),
            ATTR_ACCELERATION: Attribute(None, default_type=np.int64, min_value=0, max_value=100e9,
                                         set_function=self.set_acceleration),
            ATTR_VELOCITY: Attribute(None, default_type=np.int64, min_value=0, max_value=10e12,
                                     set_function=self.set_velocity),
            ATTR_SENSOR_MODE: Attribute(None, default_type=self.sensor_modes.keys(), set_function=self.set_sensor_mode),
            ATTR_MOVE_MODE: Attribute(None, default_type=self.move_modes.keys(), set_function=self.set_move_mode),
            ATTR_SAFE_DIRECTION: Attribute(None, default_type=self.safe_direction_modes.keys(),
                                           set_function=self.set_safe_direction),
            ATTR_HOLDING_TIME: Attribute(None, default_type=np.int32, min_value=-1, unit="ms",
                                         set_function=self.set_holding_time),
        })

    def start_polling(self):
        super(DeviceSmaractMcs2Channel, self).start_polling()
        self.poll_command(":CHAN{}:STAT?\r\n".format(self.channel), 250)
        self.poll_command(":CHAN{}:POS:CURR?\r\n".format(self.channel), 250)
        self.poll_command(":CHAN{}:POS:TARG?\r\n".format(self.channel), 250)
        self.poll_command(":CHAN{}:TEMP?\r\n".format(self.channel), 10000)

    def stop_polling(self):
        self.remove_poll_command(":CHAN{}:STAT?\r\n".format(self.channel), 250)
        self.remove_poll_command(":CHAN{}:POS:CURR?\r\n".format(self.channel), 250)
        self.remove_poll_command(":CHAN{}:POS:TARG?\r\n".format(self.channel), 250)
        self.remove_poll_command(":CHAN{}:TEMP?\r\n".format(self.channel), 10000)

    def subject_update(self, key, value, subject):
        super(DeviceSmaractMcs2Channel, self).subject_update(key, value, subject)

        if self.connected and isinstance(key, tuple) and key[0] == self.channel:
            attribute = key[1]

            if attribute == ATTR_STATE and self.get_value(ATTR_STATE) != value:
                self.set_attribute((ATTR_MOVING, VALUE), bool(value & 0x0001))
                self.set_attribute((ATTR_CLOSED_LOOP_ACTIVE, VALUE), bool(value & 0x0002))
                self.set_attribute((ATTR_CALIBRATING, VALUE), bool(value & 0x0004))
                self.set_attribute((ATTR_REFERENCING, VALUE), bool(value & 0x0008))
                self.set_attribute((ATTR_MOVE_DELAYED, VALUE), bool(value & 0x0100))
                self.set_attribute((ATTR_SENSOR_PRESENT, VALUE), bool(value & 0x0020))
                self.set_attribute((ATTR_CALIBRATED, VALUE), bool(value & 0x0040))
                self.set_attribute((ATTR_REFERENCED, VALUE), bool(value & 0x0080))
                self.set_attribute((ATTR_END_STOP_REACHED, VALUE), bool(value & 0x0100))
                self.set_attribute((ATTR_RANGE_LIMIT_REACHED, VALUE), bool(value & 0x0200))
                self.set_attribute((ATTR_FOLLOWING_LIMIT_REACHED, VALUE), bool(value & 0x0400))
                self.set_attribute((ATTR_MOVEMENT_FAILED, VALUE), bool(value & 0x0800))
                self.set_attribute((ATTR_STREAMING, VALUE), bool(value & 0x1000))
                self.set_attribute((ATTR_OVER_TEMPERATURE, VALUE), bool(value & 0x4000))
                self.set_attribute((ATTR_INDEX_MARK, VALUE), bool(value & 0x8000))

                if bool(value & 0x0001):
                    self.set_status(STATUS_BUSY)
                else:
                    self.set_status(STATUS_IDLE)
            elif attribute == ATTR_ENCODER_BASE_UNIT:
                if value == 2:
                    value = u"m"
                else:
                    value = u"deg"
            elif attribute == ATTR_ENCODER_RESOLUTION:
                unit = self.get_value(ATTR_ENCODER_BASE_UNIT)
                prefix = {-12: u"p", -9: u"n", -6: u"u", -3: u"m"}
                base_position_unit = prefix.get(value, "") + unit
                self.set_attribute((ATTR_POSITION, UNIT), base_position_unit)
                self.set_attribute((ATTR_TARGET_POSITION, UNIT), base_position_unit)
                self.set_attribute((ATTR_POSITION_UPPER_LIMIT, UNIT), base_position_unit)
                self.set_attribute((ATTR_POSITION_LOWER_LIMIT, UNIT), base_position_unit)
                self.set_attribute((ATTR_ACCELERATION, UNIT), u"{}/s".format(base_position_unit))
                self.set_attribute((ATTR_VELOCITY, UNIT), u"{}/s".format(base_position_unit))
            elif attribute == ATTR_POSITION_LOWER_LIMIT:
                self.set_attribute([ATTR_POSITION, MIN], value)
            elif attribute == ATTR_POSITION_UPPER_LIMIT:
                self.set_attribute([ATTR_POSITION, MAX], value)
            self.set_attribute((ATTR_LATENCY, VALUE), self.device.get_value(ATTR_LATENCY))
            self.set_value(attribute, value)

    @expose_method()
    def stop(self, callback=None):
        self.logger.info(u"Stop movement")
        return self.command(u":STOP{}\r\n".format(self.channel), callback, with_token=True)

    @expose_method()
    def calibrate(self, callback=None):
        self.logger.info(u"Calibrate")
        return self.command(u":CAL{}\r\n".format(self.channel), callback, with_token=True)

    @expose_method()
    def find_reference(self, callback=None):
        self.logger.info(u"Reference")
        return self.command(u":REF{}\r\n".format(self.channel), callback, with_token=True)

    @expose_method({"position": ATTR_POSITION})
    def move_absolute(self, position):
        try:
            move_mode = self[ATTR_MOVE_MODE][VALUE]
            position = device_units(self, ATTR_POSITION, position)
            self.logger.info(u"Move to absolute position {}".format(position))
            if move_mode == "Relative":
                position = position.m - self[ATTR_POSITION][VALUE]
            else:
                position = position.m
            return self.set_attribute((ATTR_TARGET_POSITION, VALUE), position)
        except (UndefinedUnitError, ValueError) as e:
            self.logger.exception(e)
            raise DeviceUnitError(e)

    @expose_method({"position": ATTR_POSITION})
    def move_relative(self, position):
        try:
            move_mode = self[ATTR_MOVE_MODE][VALUE]
            position = device_units(self, ATTR_POSITION, position).m
            self.logger.info(u"Move by relative position {}".format(position))
            if move_mode == "Absolute":
                position = self[ATTR_POSITION][VALUE] + position
            else:
                position = position.m
            return self.set_attribute((ATTR_TARGET_POSITION, VALUE), position)
        except (UndefinedUnitError, ValueError) as e:
            self.logger.exception(e)
            raise DeviceUnitError(e)

    def _move_absolute(self, value, callback=None):
        self.logger.info(u"Move to position {}".format(value))
        token = self.command(u":MOVE{} {}\r\n".format(self.channel, value), callback, with_token=True)
        return token

    def get_encoder_unit(self):
        self.command(u":CHAN{}:TUN:BASE:UNIT?\r\n".format(self.channel))
        self.command(u":CHAN{}:TUN:BASE:RES?\r\n".format(self.channel))

    def get_position_limit_range(self):
        self.command(u":CHAN{}:RLIM:MAX?\r\n".format(self.channel))
        self.command(u":CHAN{}:RLIM:MIN?\r\n".format(self.channel))

    def get_positioner_configuration(self):
        self.command(u":CHAN{}:PTYP:NAME?\r\n".format(self.channel))
        self.command(u":CHAN{}:PTYP:CODE?\r\n".format(self.channel))

    def get_step_frequency(self):
        self.command(u":CHAN{}:STEP:FREQ?\r\n".format(self.channel))

    def get_step_amplitude(self):
        self.command(u":CHAN{}:STEP:AMPL?\r\n".format(self.channel))

    def get_velocity(self):
        self.command(u":CHAN{}:VEL?\r\n".format(self.channel))

    def get_acceleration(self):
        self.command(u":CHAN{}:ACC?\r\n".format(self.channel))

    def get_sensor_mode(self):
        self.command(u":CHAN{}:SENS:MODE?\r\n".format(self.channel))

    def get_move_mode(self):
        self.command(u":CHAN{}:MMOD?\r\n".format(self.channel))

    def get_safe_direction(self):
        self.command(u":CHAN{}:SDIR?\r\n".format(self.channel))

    def get_holding_time(self):
        self.command(u":CHAN{}:HOLD?\r\n".format(self.channel))

    def set_holding_time(self, value, callback=None):
        self.logger.info(u"Set holding time to {}".format(value))
        return self.command(u":CHAN{}:HOLD {}\r\n".format(self.channel, int(value)), callback, with_token=True)

    def set_upper_position_limit(self, value, callback=None):
        self.logger.info(u"Set upper limit to {}".format(value))
        token = self.command(u":CHAN{}:RLIM:MAX {}\r\n".format(self.channel, int(value)), callback, with_token=True)
        self.set_attribute([ATTR_POSITION, MAX], value)
        return token

    def set_lower_position_limit(self, value, callback=None):
        self.logger.info(u"Set lower limit to {}".format(value))
        token = self.command(u":CHAN{}:RLIM:MIN {}\r\n".format(self.channel, int(value)), callback, with_token=True)
        self.set_attribute([ATTR_POSITION, MIN], value)
        return token

    def set_positioner_code(self, value, callback=None):
        self.logger.info(u"Set positioner  code to {}".format(value))
        token = self.command(u":CHAN{}:PTYP:CODE {}\r\n".format(self.channel, int(value)), callback, with_token=True)
        self.get_positioner_configuration()
        self.get_encoder_unit()
        return token

    def set_step_frequency(self, value, callback=None):
        self.logger.info(u"Set step frequency to {} Hz".format(value))
        return self.command(u":CHAN{}:STEP:FREQ {}\r\n".format(self.channel, int(value)), callback, with_token=True)

    def set_step_amplitude(self, value, callback=None):
        self.logger.info(u"Set step amplitude to {}".format(value))
        return self.command(u":CHAN{}:STEP:AMPL {}\r\n".format(self.channel, int(value)), callback, with_token=True)

    def set_velocity(self, value, callback=None):
        self.logger.info(u"Set velocity to {}".format(value))
        return self.command(u":CHAN{}:VEL {}\r\n".format(self.channel, int(value)), callback, with_token=True)

    def set_acceleration(self, value, callback=None):
        self.logger.info(u"Set acceleration to {}".format(value))
        return self.command(u":CHAN{}:ACC {}\r\n".format(self.channel, int(value)), callback, with_token=True)

    def set_sensor_mode(self, value, callback=None):
        self.logger.info(u"Set sensor mode to {}".format(value))
        value = self.sensor_modes[value]
        return self.command(u":CHAN{}:SENS:MODE {}\r\n".format(self.channel, value), callback, with_token=True)

    def set_move_mode(self, value, callback=None):
        self.logger.info(u"Set move mode to {}".format(value))
        value = self.move_modes[value]
        return self.command(u":CHAN{}:MMOD {}\r\n".format(self.channel, value), callback, with_token=True)

    def set_safe_direction(self, value, callback=None):
        self.logger.info(u"Set safe direction to {}".format(value))
        value = self.safe_direction_modes[value]
        return self.command(u":CHAN{}:SDIR {}\r\n".format(self.channel, value), callback, with_token=True)


class DeviceMCS2FlyScanner(DeviceScanner):

    def __init__(self, device_id=None, config=None):
        super().__init__(device_id, config)

    def _init_attributes(self):
        DeviceScanner._init_attributes(self)
        last_scan = kamzik3.session.get_scan_count()
        self.attributes.update({
            ATTR_DWELL_TIME: Attribute(100, default_type=np.float32, min_value=1, unit="ms"),
        })

    @expose_method()
    def get_scanner_attributes(self):
        raise NotImplementedError

    @expose_method()
    def get_scanner_macro(self, scanner_input, scanner_attributes):
        raise NotImplementedError
