import time
from threading import Thread

import numpy as np
import serial
from bidict import frozenbidict

from kamzik3 import DeviceError, units
from kamzik3.constants import *
from kamzik3.devices.attribute import Attribute
from kamzik3.devices.device import Device
from kamzik3.devices.deviceChannel import DeviceChannel
from kamzik3.devices.deviceGalil import DeviceGalil
from kamzik3.devices.devicePort import DevicePort
from kamzik3.snippets.snippetsDecorators import expose_method
from kamzik3.snippets.snippetsUnits import device_units
from kamzik3.macro.step import StepDeviceAttributeNumerical

MOTOR_TYPE_PWM_SIGN_SERVO = u"PMW sign servo (1.5)"
MOTOR_TYPE_PWM_SIGN_SERVO_REVERSED_POLARITY = u"PMW servo reversed polarity (-1.5)"
MOTOR_TYPE_SERVO = u"Servo (1)"
MOTOR_TYPE_SERVO_REVERSED_POLARITY = u"Servo reversed polarity (-1)"
MOTOR_TYPE_STEP_ACTIVE_HIGH_REVERSED = u"Step active high reversed (-2.5)"
MOTOR_TYPE_STEP_ACTIVE_HIGH_STEP = u"Step active high step (-2)"
MOTOR_TYPE_STEP_ACTIVE_LOW_REVERSED = u"Step active low reversed (2.5)"
MOTOR_TYPE_STEP_ACTIVE_LOW_STEP = u"Step active low step (2)"

MOTOR_TYPES = frozenbidict({
    MOTOR_TYPE_SERVO: 1,
    MOTOR_TYPE_SERVO_REVERSED_POLARITY: -1,
    MOTOR_TYPE_PWM_SIGN_SERVO: 1.5,
    MOTOR_TYPE_PWM_SIGN_SERVO_REVERSED_POLARITY: -1.5,
    MOTOR_TYPE_STEP_ACTIVE_LOW_STEP: 2,
    MOTOR_TYPE_STEP_ACTIVE_HIGH_STEP: -2,
    MOTOR_TYPE_STEP_ACTIVE_LOW_REVERSED: 2.5,
    MOTOR_TYPE_STEP_ACTIVE_HIGH_REVERSED: -2.5,
})
LIMIT_SWITCH_LEVELS = frozenbidict({
    u"High": 1,
    u"Low": -1
})
HOMING_DIRECTION = frozenbidict({
    u"Forward": 1,
    u"Backward": -1
})
HOMING_METHODS = frozenbidict({
    u"Command based": 0,
    u"Limit based": 1
})
LIMIT_SWITCHES_MODE = frozenbidict({
    u"Both limit switches are enabled": 0,
    u"Forward limit switch disabled": 1,
    u"Reverse limit switch disabled": 2,
    u"Both limit switch disabled": 3
})
FLAG_FORWARD_LIMIT_INACTIVE = u"Forward limit inactive flag"
FLAG_HOME_SWITCH = u"Home switch flag"
FLAG_MOTOR_MOVING = u"Motor moving flag"
FLAG_MOTOR_OFF = u"Motor Off flag"
FLAG_POSITION_EXCEEDS_ERROR = u"Position error flag"
FLAG_POSITION_LATCH = u"Position latch occured flag"
FLAG_REFERENCING = u"Referencing flag"
FLAG_REVERSE_LIMIT_INACTIVE = u"Reversed limit inactive flag"


class DeviceGalilMotor(DeviceGalil):
    acronym_letters = u"ABCDEFGHIJKLMNOPQRSTUVXYZ"
    push_commands_max = 1
    response_timeout = 3000

    def handle_configuration(self):
        start_at = time.time()

        def _finish_configuration(*_, **__):
            self._config_commands()
            self._config_attributes()
            self.start_polling()
            self.set_status(STATUS_CONFIGURED)
            self.logger.info(u"Device configuration took {} sec.".format(time.time() - start_at))

        self.command(u"EO 0;")
        # Get number of channels
        self.command(u"QZ;")
        self.get_motor_config(callback=_finish_configuration)

    def _init_attributes(self):
        Device._init_attributes(self)
        self.attributes.update({
            ATTR_CHANNELS: Attribute(None, readonly=True, default_type=np.uint8, min_value=0, max_value=256),
            ATTR_LIMIT_SWITCH_ACTIVE_LEVEL: Attribute(None, default_type=LIMIT_SWITCH_LEVELS.keys(),
                                                      set_function=self.set_limit_switch_active_level),
            ATTR_HOMING_DIRECTION: Attribute(None, default_type=HOMING_DIRECTION.keys(),
                                             set_function=self.set_homing_direction),
            ATTR_LATCH_INPUT_LEVEL: Attribute(None, default_type=LIMIT_SWITCH_LEVELS.keys(),
                                              set_function=self.set_latch_input_level),
        })

    def start_polling(self):
        Device.start_polling(self)
        self.poll_command(u"TD;", 300)
        self.poll_command(u"TS;", 300)

    def set_limit_switch_active_level(self, value, callback=None):
        self.command(u"CN {};".format(LIMIT_SWITCH_LEVELS.get(value)), callback=callback)

    def set_homing_direction(self, value, callback=None):
        self.command(u"CN ,{};".format(HOMING_DIRECTION.get(value)), callback=callback)

    def set_latch_input_level(self, value, callback=None):
        self.command(u"CN ,,{};".format(LIMIT_SWITCH_LEVELS.get(value)), callback=callback)

    def handle_readout(self, readout_buffer):
        command, output, callback, token = super(DeviceGalil, self).handle_readout(readout_buffer)
        # Strip white characters from output
        output = output.strip()
        if output and output[0] == "?":
            self.handle_command_error(command, output)
            self.get_error_code()
            return False
        elif command == u"MG _CN0, _CN1, _CN2, _CN3, _CN4;":
            ls_level, home_direction, latch_input_level, selective_abort, no_termniation_flag = [int(float(v)) for v in
                                                                                                 output.split(" ")]
            self.set_value(ATTR_LIMIT_SWITCH_ACTIVE_LEVEL, LIMIT_SWITCH_LEVELS.inv.get(ls_level))
            self.set_value(ATTR_HOMING_DIRECTION, HOMING_DIRECTION.inv.get(home_direction))
            self.set_value(ATTR_LATCH_INPUT_LEVEL, LIMIT_SWITCH_LEVELS.inv.get(latch_input_level))
        elif command == u"QZ;":
            parsed_output = [int(float(v)) for v in output.split(", ")]
            self.set_value(ATTR_CHANNELS, parsed_output[0])
        # elif command == u"MG _QZ0;":
        #     self.set_value(ATTR_CHANNELS, int(float(output)))
        elif command == u"TC 1;":
            readout_buffer = output
            self.handle_command_error(command, readout_buffer)
        elif command == u"TS;":
            for channel, status in enumerate((int(float(v)) for v in output.split(", "))):
                for bit, flag in enumerate((FLAG_POSITION_LATCH, FLAG_HOME_SWITCH, FLAG_REVERSE_LIMIT_INACTIVE,
                                            FLAG_FORWARD_LIMIT_INACTIVE, None,
                                            FLAG_MOTOR_OFF, FLAG_POSITION_EXCEEDS_ERROR, FLAG_MOTOR_MOVING)):
                    if flag is None: continue
                    state = bool(status & (1 << bit))
                    self.notify((channel, flag), state)
                    if flag == FLAG_MOTOR_MOVING:
                        self.notify((channel, ATTR_STATUS), STATUS_BUSY if state else STATUS_IDLE)
        elif command == u"TD;":
            for channel, position in enumerate((int(float(v)) for v in output.split(", "))):
                self.notify((channel, ATTR_POSITION), position)
        elif u"MG _AG" in command:
            channel = self.acronym_letters.find(command[-2])
            self.notify((channel, ATTR_AMPLIFIER_GAIN), int(float(output)))
        elif u"MG _MT" in command:
            channel = self.acronym_letters.find(command[-2])
            motor_type = MOTOR_TYPES.inv.get(float(output))
            self.notify((channel, ATTR_MOTOR_TYPE), motor_type)
        elif u"MG _YA" in command:
            channel = self.acronym_letters.find(command[-2])
            self.notify((channel, ATTR_STEP_DRIVE_RESOLUTION), int(float(output)))
        elif u"MG _SP" in command:
            channel = self.acronym_letters.find(command[-2])
            self.notify((channel, ATTR_VELOCITY), int(float(output)))
        elif u"MG _LC" in command:
            channel = self.acronym_letters.find(command[-2])
            self.notify((channel, ATTR_LOW_CURRENT_STEPPER_MODE), int(float(output)))
        elif u"MG _LD" in command:
            channel = self.acronym_letters.find(command[-2])
            limit_mode = LIMIT_SWITCHES_MODE.inv.get(float(output))
            self.notify((channel, ATTR_LIMIT_SWITCHES_MODE), limit_mode)
        elif u"MG _AC" in command:
            channel = self.acronym_letters.find(command[-2])
            self.notify((channel, ATTR_ACCELERATION), int(float(output)))
        elif u"MG _DC" in command:
            channel = self.acronym_letters.find(command[-2])
            self.notify((channel, ATTR_DECELERATION), int(float(output)))
        if callback is not None:
            self.handle_readout_callback(callback, command, readout_buffer)
        if token:
            self.device_server.push_message(self.device_id, [command, readout_buffer], token)

            for observer in self._observers[:]:
                if isinstance(observer, DeviceGalilMotorChannel):
                    self.device_server.push_message(observer.device_id, [command, readout_buffer], token)

    def get_motor_config(self, callback=None):
        self.command(u"MG _CN0, _CN1, _CN2, _CN3, _CN4;", callback)


class DeviceGalilMotorPort(DevicePort, DeviceGalilMotor):
    terminator = DeviceGalil.terminator
    response_timeout = 3000

    def __init__(self, port, baud_rate=19200, parity=serial.PARITY_NONE, stop_bits=serial.STOPBITS_ONE,
                 byte_size=serial.EIGHTBITS, device_id=None, config=None):
        super(DeviceGalilMotorPort, self).__init__(port, baud_rate, parity, stop_bits, byte_size, device_id, config)

    def handshake(self):
        self.logger.info(u"Handshake initiated")
        self.push(b"MG 1;")
        time.sleep(0.02)  # Give some time for devices to reply
        if self.serial_port.in_waiting != 0:
            if self.read_all().strip() in (u"1.0000\r\n:", u"MG 1; 1.0000\r\n:"):
                return True
        return False


class DeviceGalilMotorChannel(DeviceChannel):

    def __init__(self, device, channel, device_id=None, config=None):
        self.acronym = DeviceGalilMotor.acronym_letters[channel]
        self.backlash_cleared_flag = True
        self.final_position_setpoint = None
        DeviceChannel.__init__(self, device, channel, device_id, config)

    def handle_configuration(self):
        if self.configured:
            return

        start_at = time.time()

        def _finish_configuration(*_, **__):
            self._config_commands()
            self._config_attributes()
            self.start_polling()
            self.set_status(STATUS_CONFIGURED)
            self.logger.info(u"Device configuration took {} sec.".format(time.time() - start_at))

        self.connected = True
        self.get_motor_type()
        self.get_step_drive_resolution()
        self.get_velocity()
        self.get_low_current_stepper_mode()
        self.get_acceleration()
        self.get_deceleration()
        self.get_limit_switch_mode()
        self.get_amplifier_gain(callback=_finish_configuration)

    def _init_attributes(self):
        super(DeviceGalilMotorChannel, self)._init_attributes()
        self.attributes.update({
            ATTR_ACRONYM: Attribute(self.acronym, readonly=True),
            ATTR_AMPLIFIER_GAIN: Attribute(None, default_type=np.uint8, min_value=0, max_value=3,
                                           set_function=self.set_amplifier_gain),
            ATTR_MOTOR_TYPE: Attribute(None, default_type=MOTOR_TYPES.keys(), set_function=self.set_motor_type),
            ATTR_VELOCITY: Attribute(None, default_type=np.float, min_value=-15e6, max_value=15e6, unit=u"steps/sec",
                                     set_function=self.set_velocity),
            ATTR_STEP_DRIVE_RESOLUTION: Attribute(None, default_type=np.uint64, max_value=15e6, unit=u"ustep",
                                                  set_function=self.set_step_drive_resolution),
            ATTR_BACKLASH_DISTANCE: Attribute(0, default_type=np.float64, readonly=False, decimals=3),
            FLAG_FORWARD_LIMIT_INACTIVE: Attribute(None, default_type=np.bool, readonly=True),
            FLAG_HOME_SWITCH: Attribute(None, default_type=np.bool, readonly=True),
            FLAG_MOTOR_MOVING: Attribute(None, default_type=np.bool, readonly=True),
            FLAG_MOTOR_OFF: Attribute(None, default_type=np.bool, readonly=True),
            FLAG_POSITION_EXCEEDS_ERROR: Attribute(None, default_type=np.bool, readonly=True),
            FLAG_POSITION_LATCH: Attribute(None, default_type=np.bool, readonly=True),
            FLAG_REFERENCING: Attribute(False, default_type=np.bool, readonly=True),
            FLAG_REVERSE_LIMIT_INACTIVE: Attribute(None, default_type=np.bool, readonly=True),
            ATTR_LOW_CURRENT_STEPPER_MODE: Attribute(None, default_type=np.uint32, max_value=32767,
                                                     set_function=self.set_low_current_stepper_mode),
            ATTR_ACCELERATION: Attribute(None, default_type=np.uint64, min_value=1024, max_value=1073740800,
                                         set_function=self.set_acceleration),
            ATTR_DECELERATION: Attribute(None, default_type=np.uint64, min_value=1024, max_value=1073740800,
                                         set_function=self.set_deceleration),
            ATTR_POSITION: Attribute(None, default_type=np.float64, unit=u"counts", set_function=self._move_absolute,
                                     set_value_when_set_function=False),
            ATTR_HOMING_METHOD: Attribute(u"Limit based", default_type=HOMING_METHODS.keys()),
            ATTR_LIMIT_SWITCHES_MODE: Attribute(None, default_type=LIMIT_SWITCHES_MODE.keys(),
                                                set_function=self.set_limit_switch_mode),
            ATTR_POSITION_LOWER_LIMIT: Attribute(None, default_type=np.float64, unit=u"counts",
                                                 set_function=self.set_lower_position_limit),
            ATTR_POSITION_UPPER_LIMIT: Attribute(None, default_type=np.float64, unit=u"counts",
                                                 set_function=self.set_upper_position_limit),
            ATTR_FAST_REFERENCE_VELOCITY: Attribute(5, default_type=np.float, min_value=-15e6, max_value=15e6,
                                                    unit=u"steps/sec"),
            ATTR_SLOW_REFERENCE_VELOCITY: Attribute(1, default_type=np.float, min_value=-15e6, max_value=15e6,
                                                    unit=u"steps/sec"),
            ATTR_SAFE_DIRECTION: Attribute(u"Forward", default_type=HOMING_DIRECTION.keys()),
            ATTR_REFERENCED: Attribute(False, default_type=np.bool, readonly=True),
            ATTR_REFERENCE_STEPS_BACK: Attribute(40, default_type=np.uint32, min_value=1, unit=u"steps"),
        })

    def subject_update(self, key, value, subject):
        super(DeviceGalilMotorChannel, self).subject_update(key, value, subject)

        if self.connected and isinstance(key, tuple) and key[0] == self.channel:
            attribute = key[1]

            if attribute == ATTR_VELOCITY:
                value /= self.get_value(ATTR_STEP_DRIVE_RESOLUTION)
            elif attribute == ATTR_STATUS:
                if self.get_value(FLAG_REFERENCING):
                    value = STATUS_BUSY
                if value == STATUS_IDLE and not self.get_value(
                        FLAG_MOTOR_OFF) and self.get_value(ATTR_LOW_CURRENT_STEPPER_MODE) == 0:
                    self.servo_off()

            self.set_attribute((ATTR_LATENCY, VALUE), self.device.get_value(ATTR_LATENCY))
            self.set_value(attribute, value)

    def _move_absolute(self, position):
        self.servo_on()
        position_diff = self[ATTR_POSITION][SETPOINT] - self[ATTR_POSITION][VALUE]
        backlash_distance = self.get_value(ATTR_BACKLASH_DISTANCE)
        if self.backlash_cleared_flag and backlash_distance != 0 and np.sign(backlash_distance) == np.sign(
                position_diff):
            backlash_macro = Thread(target=self._move_backlash, args=([self[ATTR_POSITION][SETPOINT]]))
            backlash_macro.start()
            return

        self.command(u"PA{}={:.10f};".format(self.acronym, position))
        self.begin_motion()

    def _move_backlash(self, new_setpoint):
        self.backlash_cleared_flag = False
        backlash_distance = self.get_value(ATTR_BACKLASH_DISTANCE)
        min_t, max_t = self[ATTR_POSITION].negative_tolerance(), self[ATTR_POSITION].positive_tolerance()
        device_unit = self.get_attribute(ATTR_POSITION)[UNIT]
        setpoint_one = units.Quantity(new_setpoint + backlash_distance, device_unit)
        setpoint_two = units.Quantity(new_setpoint, device_unit)
        step_one = StepDeviceAttributeNumerical("One", self.device_id, ATTR_POSITION, setpoint_one, min_t, max_t)
        step_two = StepDeviceAttributeNumerical("Two", self.device_id, ATTR_POSITION, setpoint_two, min_t, max_t)
        step_one.start()
        step_two.start()
        self.backlash_cleared_flag = True

    @expose_method({"steps": "Number of steps"})
    def move_steps(self, steps):
        resolution = self.get_value(ATTR_STEP_DRIVE_RESOLUTION)
        steps = int(steps) * resolution

        self.servo_on()
        self.command(u"PR{}={};".format(self.acronym, steps))
        self.begin_motion()

    @expose_method({"position": ATTR_POSITION})
    def move_relative(self, position):
        position = device_units(self, ATTR_POSITION, position)
        self.logger.info(u"Move motor channel by relative position {:~}".format(position))
        return self.set_attribute([ATTR_POSITION, VALUE], self[ATTR_POSITION][VALUE] + position.m)

    @expose_method({"position": ATTR_POSITION})
    def move_absolute(self, position):
        position = device_units(self, ATTR_POSITION, position)
        self.logger.info(u"Move motor channel to absolute position {:~}".format(position))
        return self.set_attribute([ATTR_POSITION, VALUE], position.m)

    def set_limit_switch_mode(self, value, callback=None):
        return self.command(u"LD{}={};".format(self.acronym, LIMIT_SWITCHES_MODE.get(value)), callback, with_token=True)

    def set_acceleration(self, value, callback=None):
        return self.command(u"AC{}={};".format(self.acronym, int(value)), callback, with_token=True)

    def set_deceleration(self, value, callback=None):
        return self.command(u"DC{}={};".format(self.acronym, int(value)), callback, with_token=True)

    def set_motor_type(self, motor_type, callback=None):
        return self.command(u"MT{}={};".format(self.acronym, MOTOR_TYPES.get(motor_type)), callback, with_token=True)

    def set_amplifier_gain(self, value, callback=None):
        return self.command(u"AG{}={};".format(self.acronym, int(value)), callback, with_token=True)

    def set_step_drive_resolution(self, value, callback=None):
        return self.command(u"YA{}={};".format(self.acronym, int(value)), callback, with_token=True)

    def set_velocity(self, value, callback=None):
        velocity = value * self.get_value(ATTR_STEP_DRIVE_RESOLUTION)
        return self.command(u"SP{}={};".format(self.acronym, int(velocity)), callback, with_token=True)

    def set_low_current_stepper_mode(self, value, callback=None):
        return self.command(u"LC{}={};".format(self.acronym, int(value)), callback, with_token=True)

    def set_lower_position_limit(self, value, callback=None):
        self.set_value(ATTR_POSITION_LOWER_LIMIT, value)
        lower_position_limit = self[ATTR_POSITION].remove_offset_factor(value)
        return self.set_attribute([ATTR_POSITION, MIN], lower_position_limit, callback)

    def set_upper_position_limit(self, value, callback=None):
        self.set_value(ATTR_POSITION_UPPER_LIMIT, value)
        upper_position_limit = self[ATTR_POSITION].remove_offset_factor(value)
        return self.set_attribute([ATTR_POSITION, MAX], upper_position_limit, callback)

    def get_motor_type(self, callback=None):
        self.command(u"MG _MT{};".format(self.acronym), callback)

    def get_amplifier_gain(self, callback=None):
        self.command(u"MG _AG{};".format(self.acronym), callback)

    def get_step_drive_resolution(self, callback=None):
        self.command(u"MG _YA{};".format(self.acronym), callback)

    def get_velocity(self, callback=None):
        self.command(u"MG _SP{};".format(self.acronym), callback)

    def get_position(self, callback=None):
        self.command(u"MG _TD{};".format(self.acronym), callback)

    def get_acceleration(self, callback=None):
        self.command(u"MG _AC{};".format(self.acronym), callback)

    def get_deceleration(self, callback=None):
        self.command(u"MG _DC{};".format(self.acronym), callback)

    def get_low_current_stepper_mode(self, callback=None):
        self.command(u"MG _LC{};".format(self.acronym), callback)

    def get_limit_switch_mode(self, callback=None):
        self.command(u"MG _LD{};".format(self.acronym), callback)

    def get_status(self, callback=None):
        self.command(u"MG _TS{};".format(self.acronym), callback)

    def get_low_current_stepper_mode(self, callback=None):
        self.command(u"MG _LC{};".format(self.acronym), callback)

    def get_acceleration(self, callback=None):
        self.command(u"MG _AC{};".format(self.acronym), callback)

    def get_deceleration(self, callback=None):
        self.command(u"MG _DC{};".format(self.acronym), callback)

    def get_position(self):
        self.command(u"TD{};".format(self.acronym))

    def begin_motion(self):
        self.command(u"BG{};".format(self.acronym))

    def servo_on(self):
        self.command(u"SH{};".format(self.acronym))

    def servo_off(self):
        self.command(u"MO{};".format(self.acronym))

    def _limit_based_reference(self):
        self.set_attribute([FLAG_REFERENCING, VALUE], True)
        self.set_attribute([ATTR_REFERENCED, VALUE], False)
        direction = HOMING_DIRECTION[self.get_value(ATTR_SAFE_DIRECTION)]
        fast_reference_velocity = self.get_value(ATTR_FAST_REFERENCE_VELOCITY)
        slow_reference_velocity = self.get_value(ATTR_SLOW_REFERENCE_VELOCITY)
        current_velocity = self.get_value(ATTR_VELOCITY)
        steps_back = self.get_value(ATTR_REFERENCE_STEPS_BACK)
        if direction == 1:
            check_limit = FLAG_FORWARD_LIMIT_INACTIVE
        else:
            check_limit = FLAG_REVERSE_LIMIT_INACTIVE

        def _reference_motion():
            # Jog fast until hard stop
            self.jog(fast_reference_velocity * direction)
            self._wait_until_stopped()
            # Check if we are at the limit
            if self.get_value(check_limit) == 0:
                # Move away from hard stop by 40 steps
                self.move_steps(steps_back * -direction)
                self._wait_until_stopped()
                # Jog slow until hard stop again
                self.jog(slow_reference_velocity * direction)
                self._wait_until_stopped()
                # Move away from hard stop by 40 steps
                self.move_steps(steps_back * -direction)
                self._wait_until_stopped()
                self.reset_position(0)
                self.set_velocity(current_velocity)
                self.set_attribute([FLAG_REFERENCING, VALUE], False)
                self.set_attribute([ATTR_REFERENCED, VALUE], True)
            else:
                self.set_attribute([FLAG_REFERENCING, VALUE], False)
                raise DeviceError(u"Referencing failed")

        Thread(target=_reference_motion).start()
        self.logger.debug(u"Start referencing in {} direction".format(self.get_value(ATTR_SAFE_DIRECTION)))

    def _wait_until_stopped(self):
        self.command(u"TS;")
        time.sleep(0.2)
        while self.get_value(FLAG_MOTOR_MOVING):
            time.sleep(0.1)
        return True

    @expose_method()
    def find_reference(self):
        homnig_method = self.get_value(ATTR_HOMING_METHOD)
        if homnig_method == u"Command based":
            self.servo_on()
            self.command(u"HM{};".format(self.acronym))
            self.begin_motion()
        elif homnig_method == u"Limit based":
            self._limit_based_reference()

    @expose_method({"position": ATTR_POSITION})
    def reset_position(self, position=0):
        position = device_units(self, ATTR_POSITION, position)
        self.logger.info(u"Reset motor position to {:~}".format(position))
        position = self[ATTR_POSITION].remove_offset_factor(position.m)
        self.command(u"DP{}={};".format(self.acronym, position))

    @expose_method({"velocity": ATTR_VELOCITY})
    def jog(self, velocity):
        self.logger.info(u"Start motor jogging")
        velocity = device_units(self, ATTR_VELOCITY, velocity)
        velocity = self[ATTR_POSITION].remove_offset_factor(velocity)
        velocity = float(velocity.m) * self.get_value(ATTR_STEP_DRIVE_RESOLUTION)
        self.servo_on()
        self.command(u"JG{}={};".format(self.acronym, velocity))
        self.begin_motion()

    @expose_method()
    def stop(self):
        self.logger.info(u"Stop motor channel movement")
        self.backlash_cleared_flag = True
        self.command(u"ST{};".format(self.acronym))
        self.set_value(FLAG_REFERENCING, False)
