"""
 Copyright (c) 2018-2019 Alan Yorinks All rights reserved.

 This program is free software; you can redistribute it and/or
 modify it under the terms of the GNU AFFERO GENERAL PUBLIC LICENSE
 Version 3 as published by the Free Software Foundation; either
 or (at your option) any later version.
 This library is distributed in the hope that it will be useful,
 but WITHOUT ANY WARRANTY; without even the implied warranty of
 MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
 General Public License for more details.

 You should have received a copy of the GNU AFFERO GENERAL PUBLIC LICENSE
 along with this library; if not, write to the Free Software
 Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA
"""

# noinspection PyCompatibility
import asyncio
import sys
import time
from serial.tools import list_ports

# noinspection PyPackageRequirements
from pin_data import PinData
from private_constants import PrivateConstants
from pymata_express_serial import PymataExpressSerial


# noinspection PyCallingNonCallable,PyCallingNonCallable,PyPep8,PyBroadException,PyBroadException,PyCompatibility
class PymataExpress:
    """
    This class exposes and implements the PymataExpress API,
    It includes the public API methods as well as
    a set of private methods. If your application is using asyncio,
    this is the API that you should use.

    After instantiating this class, its "start" method MUST be called to
    perform Arduino pin auto-detection.
    """
    def __init__(self, com_port=None, baud_rate=115200,
                 arduino_instance_id=1, arduino_wait=4,
                 sleep_tune=0.0001, autostart=True,
                 analog_report_differential=1):
        """
        If you are using the Firmata Express Arduino sketch,
        and have a single Arduino connected to your computer,
        then accept all the default values.

        If you are using some other Firmata sketch, then
        you must specify both the com_port and baudrate.

        :param com_port: e.g. COM3 or /dev/ttyACM0

        :param baud_rate: Match this to the Firmata sketch

        :param arduino_instance_id: If you are using the Firmata
                                    Express sketch, match this
                                    value to that in the sketch.

        :param arduino_wait: Amount of time to wait for an Arduino to
                             fully reset itself.

        :param sleep_tune: A tuning parameter used by PymataExpressSerial

        :param autostart: If you wish to call one of the start methods within
                          your application, then set this to False.

        :param analog_report_differential: value difference between last
                                           value reported and current for
                                           callback method to be invoked

        """
        # check to make sure that Python interpreter is version 3.5 or greater
        python_version = sys.version_info
        if python_version[0] >= 3:
            if python_version[1] >= 7:
                pass
            else:
                print(
                    "ERROR: Python 3.7 or greater is required for use of this program.")

        # save input parameters
        self.com_port = com_port
        self.baud_rate = baud_rate
        self.arduino_instance_id = arduino_instance_id
        self.arduino_wait = arduino_wait
        self.sleep_tune = sleep_tune
        self.autostart = autostart
        self.analog_report_differential = analog_report_differential

        # a list of PinData objects - one for each pin segregated by pin type
        # see pin_data.py
        self.analog_pins = []
        self.digital_pins = []

        # serial port
        self.serial_port = None

        # An i2c_map entry consists of a device i2c address as the key, and
        #  the value of the key consists of a dictionary containing 3 entries.
        #  The first entry. 'value' contains the last value reported, and
        # the second, 'callback' contains a reference to a callback function.
        # the third, callback_type contains the callback type selector
        #  (None = Direct, 1 = await)
        # For example:
        # {12345: {'value': 23, 'callback': None, 'callback_type: None}}
        self.i2c_map = {}

        # the active_sonar_map maps the sonar trigger pin number (the key)
        # to the current data value returned
        # if a callback was specified, it is stored in the map as well.
        # an entry in the map consists of:
        #   pin: [callback,, callback_type, [current_data_returned]]
        self.active_sonar_map = {}

        # keep alive variables
        self.keep_alive_interval = 0
        self.period = 0
        self.margin = 0

        # first analog pin number
        self.first_analog_pin = None

        # asyncio loop
        self.loop = asyncio.get_event_loop()

        # generic asyncio task holder
        self.the_task = None

        # flag to indicate we are in shutdown mode
        self.shutdown_flag = False

        # this dictionary for mapping incoming Firmata message types to
        # handlers for the messages
        self.command_dictionary = {PrivateConstants.REPORT_VERSION:
                                       self._report_version,
                                   PrivateConstants.REPORT_FIRMWARE:
                                       self._report_firmware,
                                   PrivateConstants.CAPABILITY_RESPONSE:
                                       self._capability_response,
                                   PrivateConstants.ANALOG_MAPPING_RESPONSE:
                                       self._analog_mapping_response,
                                   PrivateConstants.PIN_STATE_RESPONSE:
                                       self._pin_state_response,
                                   PrivateConstants.STRING_DATA:
                                       self._string_data,
                                   PrivateConstants.ANALOG_MESSAGE:
                                       self._analog_message,
                                   PrivateConstants.DIGITAL_MESSAGE:
                                       self._digital_message,
                                   PrivateConstants.I2C_REPLY:
                                       self._i2c_reply,
                                   PrivateConstants.SONAR_DATA:
                                       self._sonar_data,}

        # report query results are stored in this dictionary
        self.query_reply_data = {PrivateConstants.REPORT_VERSION: '',
                                 PrivateConstants.STRING_DATA: '',
                                 PrivateConstants.REPORT_FIRMWARE: '',
                                 PrivateConstants.CAPABILITY_RESPONSE: None,
                                 PrivateConstants.ANALOG_MAPPING_RESPONSE: None,
                                 PrivateConstants.PIN_STATE_RESPONSE: None}

        print('{}{}{}'.format('\n', 'pymata_aio Version ' +
                              PrivateConstants.PYMATA_EXPRESS_VERSION,
                              '\tCopyright (c) 2018-2019 Alan Yorinks All '
                              'rights reserved.\n'))
        if not self.com_port:
            # user did not specify a com_port
            try:
                self.loop.run_until_complete(self._find_arduino())
            except KeyboardInterrupt:
                self.loop.run_until_complete(self.shutdown())
        else:
            # com_port specified - set com_port speed
            try:
                self.loop.run_until_complete(self._manual_open())
            except KeyboardInterrupt:
                self.loop.run_until_complete(self.shutdown())

        if self.com_port:
            print('{}{}\n'.format('\nArduino found and connected to ', self.com_port))

        # no com_port found - raise a runtime exception
        else:
            self.loop.run_until_complete(self.shutdown())
            raise RuntimeError('No Arduino Found or User Aborted Program')

        # start the application
        if autostart:
            self.start()

    def start(self):
        """
        This method may be called directly, but first set the autostart
        parameter to false.

        This method instantiates the serial interface and then performs auto pin
        discovery.
        Use this method if you wish to start PymataExpress manually from
        a non-asyncio function.

        """
        try:
            self.the_task = self.loop.create_task(self._arduino_report_dispatcher())
        except:
            self.shutdown()

        # get arduino firmware version and print it
        try:
            print('Retrieving Arduino Firmware ID...')
            firmware_version = self.loop.run_until_complete(self.get_firmware_version())

            print("Arduino Firmware ID: " + firmware_version)
        except TypeError:
            print('\nIs your serial cable plugged in and do you have the correct Firmata sketch loaded?')
            print('Is the COM port correct?')
            print('To see a list of serial ports, type: "list_serial_ports" in your console.')
            raise RuntimeError

        # try to get an analog pin map. if it comes back as none - shutdown
        report = self.loop.run_until_complete(self.get_analog_map())
        if not report:

            print('*** Analog map retrieval timed out. ***')
            print('\nDo you have Arduino connectivity and do you have a '
                  'Firmata sketch uploaded to the board?')
            self.loop.run_until_complete(self.shutdown())
            raise RuntimeError

        # custom assemble the pin lists
        for pin in report:
            digital_data = PinData()
            self.digital_pins.append(digital_data)
            if pin != Constants.IGNORE:
                analog_data = PinData()
                self.analog_pins.append(analog_data)

        print('{} {} {} {} {}'.format('Auto-discovery complete. Found',
                                      len(self.digital_pins),
                                      'Digital Pins and',
                                      len(self.analog_pins),
                                      'Analog Pins\n\n'))
        self.first_analog_pin = len(self.digital_pins) - len(self.analog_pins)

    async def start_aio(self):
        """
        This method may be called directly, but first set the autostart
        parameter to false.

        This method instantiates the serial interface and then performs auto pin
        discovery.
        Use this method if you wish to start PymataExpress manually from
        an asyncio function.
         """

        # start the command dispatcher loop
        self.loop = asyncio.get_event_loop()
        self.the_task = self.loop.create_task(self._arduino_report_dispatcher())

        # get arduino firmware version and print it
        firmware_version = await self.get_firmware_version()
        if not firmware_version:
            print('*** Firmware Version retrieval timed out. ***')
            print('\nDo you have Arduino connectivity and do you have a ')
            print('Firmata sketch uploaded to the board and are connected')
            print('to the correct serial port.\n')
            print('To see a list of serial ports, type: "list_serial_ports" in your console.')
            await self.shutdown()
            raise RuntimeError
        else:
            print("\nArduino Firmware ID: " + firmware_version)

        # try to get an analog pin map. if it comes back as none - shutdown
        report = await self.get_analog_map()
        if not report:
            print('*** Analog map retrieval timed out. ***')
            print('\nDo you have Arduino connectivity and do you have a '
                  'Firmata sketch uploaded to the board?')
            await self.shutdown()
            raise RuntimeError

        # custom assemble the pin lists
        for pin in report:
            digital_data = PinData()
            self.digital_pins.append(digital_data)
            if pin != Constants.IGNORE:
                analog_data = PinData()
                self.analog_pins.append(analog_data)

        print('{} {} {} {} {}'.format('Auto-discovery complete. Found',
                                      len(self.digital_pins),
                                      'Digital Pins and',
                                      len(self.analog_pins),
                                      'Analog Pins\n\n'))
        self.first_analog_pin = len(self.digital_pins) - len(self.analog_pins)

    async def _find_arduino(self):
        """
        This method will search all potential serial ports for an Arduino
        containing a sketch that has a matching arduino_instance_id as
        specified in the input parameters of this class.

        This is used explicitly with the FirmataExpress sketch.
        """

        serial_ports = []
        # print('Searching each com port for an  Arduino using ID = ', self.arduino_instance_id)
        # print('Note: 4 seconds will be allowed for the Arduino to reset itself.')
        # print('To modify the wait time, use the "arduino_wait" parameter.')
        print('Opening all potential serial ports...')
        the_ports_list = list_ports.comports()
        for port in the_ports_list:
            if port.pid is None:
                continue
            # print('\nChecking {}'.format(port.device))
            self.serial_port = PymataExpressSerial(port.device, self.baud_rate)
            # create a list of serial ports that we opened
            serial_ports.append(self.serial_port)
            print('\t' + port.device)
            await self.serial_port.reset_input_buffer()
            # print('Waiting {} seconds for Arduino To Reset.'.format(self.arduino_wait))

        # wait for arduino to reset
        print('\nWaiting {} seconds(arduino_wait) for Arduino devices to '
              'reset...'.format(self.arduino_wait))
        await asyncio.sleep(self.arduino_wait)

        print('\nSearching for an Arduino configured with an arduino_instance = ', self.arduino_instance_id)

        for serial_port in serial_ports:
            self.serial_port = serial_port
            # send the are you there request to the arduino
            await self._send_sysex(PrivateConstants.ARE_YOU_THERE)

            # await asyncio.sleep(1)
            # wait until the END_SYSEX comes back
            i_am_here = await self.serial_port.read_until(expected=b'\xf7')
            if not i_am_here:
                continue

            if len(i_am_here) != 4:
                continue

            # convert i_am_here to a list
            i_am_here = list(i_am_here)

            # check sysex command is I_AM_HERE
            if i_am_here[1] != PrivateConstants.I_AM_HERE:
                continue
            else:
                # got an I am here message - is it the correct ID?
                if i_am_here[2] == self.arduino_instance_id:
                    self.com_port = serial_port.com_port
                    return

    async def _manual_open(self):
        """
        Com port was specified by the user - try to open up that port

        :return:

        """
        # if port is not found, a serial exception will be thrown
        print('Opening {} ...'.format(self.com_port))
        self.serial_port = PymataExpressSerial(self.com_port, self.baud_rate)

        print('Waiting {} seconds for the Arduino To Reset.'.format(self.arduino_wait))
        await asyncio.sleep(self.arduino_wait)
        if self.baud_rate == 115200:
            await self._send_sysex(PrivateConstants.ARE_YOU_THERE)

            # await asyncio.sleep(1)
            # wait until the END_SYSEX comes back
            i_am_here = await self.serial_port.read_until(expected=b'\xf7')

            # convert i_am_here to a list
            i_am_here = list(i_am_here)

            if len(i_am_here) != 4:
                raise RuntimeError('Invalid Arduino ID reply length')

            # check sysex command is I_AM_HERE
            if i_am_here[1] != PrivateConstants.I_AM_HERE:
                raise RuntimeError('Retrieving ID From Arduino Failed.')
            else:
                # got an I am here message - is it the correct ID?
                if i_am_here[2] == self.arduino_instance_id:
                    return
                else:
                    raise RuntimeError('Invalid Arduino identifier retrieved')

    async def analog_read(self, pin):
        """
        Retrieve the last data update for the specified analog pin.

        :param pin: Analog pin number (ex. A2 is specified as 2)

        :returns: A tuple of last value change and the time that it occurred
        """

        return self.analog_pins[pin].current_value, self.analog_pins[pin].event_time

    async def analog_write(self, pin, value):
        """
        Set the selected pin to the specified value.

        :param pin: PWM pin number

        :param value: Pin value (0 - 0x4000)

        :returns: No return value
        """
        if PrivateConstants.ANALOG_MESSAGE + pin < 0xf0:
            command = [PrivateConstants.ANALOG_MESSAGE + pin, value & 0x7f,
                       (value >> 7) & 0x7f]
            await self._send_command(command)
        else:
            await self.extended_analog(pin, value)

    async def digital_read(self, pin):
        """
        Retrieve the last data update for the specified digital pin.

        :param pin: Digital pin number

        :returns: A tuple of last value change and the time that it occurred
        """
        return self.digital_pins[pin].current_value, self.digital_pins[pin].event_time

    async def digital_pin_write(self, pin, value):
        """
        Set the specified pin to the specified value directly without port manipulation.

        :param pin: pin number

        :param value: pin value

        :returns: No return value
        """

        command = (PrivateConstants.SET_DIGITAL_PIN_VALUE, pin, value)

        await self._send_command(command)

    async def digital_write(self, pin, value):
        """
        Set the specified pin to the specified value.

        :param pin: pin number

        :param value: pin value

        :returns: No return value
        """
        # The command value is not a fixed value, but needs to be calculated
        # using the pin's port number
        port = pin // 8

        calculated_command = PrivateConstants.DIGITAL_MESSAGE + port
        mask = 1 << (pin % 8)
        # Calculate the value for the pin's position in the port mask
        if value == 1:
            PrivateConstants.DIGITAL_OUTPUT_PORT_PINS[port] |= mask
        else:
            PrivateConstants.DIGITAL_OUTPUT_PORT_PINS[port] &= ~mask

        # Assemble the command
        command = (calculated_command,
                   PrivateConstants.DIGITAL_OUTPUT_PORT_PINS[port] & 0x7f,
                   (PrivateConstants.DIGITAL_OUTPUT_PORT_PINS[port] >> 7) & 0x7f)

        await self._send_command(command)

    async def disable_analog_reporting(self, pin):
        """
        Disables analog reporting for a single analog pin.

        :param pin: Analog pin number. For example for A0, the number is 0.

        :returns: No return value
        """
        command = [PrivateConstants.REPORT_ANALOG + pin,
                   PrivateConstants.REPORTING_DISABLE]
        await self._send_command(command)

    async def disable_digital_reporting(self, pin):
        """
        Disables digital reporting. By turning reporting off for this pin,
        Reporting is disabled for all 8 bits in the "port"

        :param pin: Pin and all pins for this port

        :returns: No return value
        """
        port = pin // 8
        command = [PrivateConstants.REPORT_DIGITAL + port,
                   PrivateConstants.REPORTING_DISABLE]
        await self._send_command(command)

    async def enable_analog_reporting(self, pin):
        """
        Enables analog reporting. By turning reporting on for a single pin,

        :param pin: Analog pin number. For example for A0, the number is 0.

        :returns: No return value
        """
        command = [PrivateConstants.REPORT_ANALOG + pin,
                   PrivateConstants.REPORTING_ENABLE]
        await self._send_command(command)

    async def enable_digital_reporting(self, pin):
        """
        Enables digital reporting. By turning reporting on for all 8 bits
        in the "port" - this is part of Firmata's protocol specification.

        :param pin: Pin and all pins for this port

        :returns: No return value
            """
        port = pin // 8
        command = [PrivateConstants.REPORT_DIGITAL + port,
                   PrivateConstants.REPORTING_ENABLE]
        await self._send_command(command)

    async def extended_analog(self, pin, data):
        """
        This method will send an extended-data analog write command to the
        selected pin.

        :param pin: 0 - 127

        :param data: 0 - 0xfffff

        :returns: No return value
        """
        analog_data = [pin, data & 0x7f, (data >> 7) & 0x7f, (data >> 14) & 0x7f]
        await self._send_sysex(PrivateConstants.EXTENDED_ANALOG, analog_data)

    async def get_analog_map(self):
        """
        This method requests a Firmata analog map query and returns the results.

        :returns: An analog map response or None if a timeout occurs
        """
        # get the current time to make sure a report is retrieved
        current_time = time.time()

        # if we do not have existing report results, send a Firmata
        # message to request one
        if self.query_reply_data.get(
                PrivateConstants.ANALOG_MAPPING_RESPONSE) is None:
            await self._send_sysex(PrivateConstants.ANALOG_MAPPING_QUERY)
            # wait for the report results to return for 4 seconds
            # if the timer expires, shutdown
            while self.query_reply_data.get(
                    PrivateConstants.ANALOG_MAPPING_RESPONSE) is None:
                elapsed_time = time.time()
                if elapsed_time - current_time > 4:
                    return None
                await asyncio.sleep(self.sleep_tune)
        return self.query_reply_data.get(
            PrivateConstants.ANALOG_MAPPING_RESPONSE)

    async def get_capability_report(self):
        """
        This method requests and returns a Firmata capability query report

        :returns: A capability report in the form of a list
        """
        if self.query_reply_data.get(
                PrivateConstants.CAPABILITY_RESPONSE) is None:
            await self._send_sysex(PrivateConstants.CAPABILITY_QUERY)
            while self.query_reply_data.get(
                    PrivateConstants.CAPABILITY_RESPONSE) is None:
                await asyncio.sleep(self.sleep_tune)
        return self.query_reply_data.get(PrivateConstants.CAPABILITY_RESPONSE)

    async def get_firmware_version(self):
        """
        This method retrieves the Firmata firmware version

        :returns: Firmata firmware version
        """
        current_time = time.time()
        if self.query_reply_data.get(PrivateConstants.REPORT_FIRMWARE) == '':
            await self._send_sysex(PrivateConstants.REPORT_FIRMWARE)
            while self.query_reply_data.get(
                    PrivateConstants.REPORT_FIRMWARE) == '':
                elapsed_time = time.time()
                if elapsed_time - current_time > 4:
                    return None
                await asyncio.sleep(self.sleep_tune)
        return self.query_reply_data.get(PrivateConstants.REPORT_FIRMWARE)

    async def get_protocol_version(self):
        """
        This method returns the major and minor values for the protocol
        version, i.e. 2.4

        :returns: Firmata protocol version
        """
        if self.query_reply_data.get(PrivateConstants.REPORT_VERSION) == '':
            await self._send_command([PrivateConstants.REPORT_VERSION])
            while self.query_reply_data.get(
                    PrivateConstants.REPORT_VERSION) == '':
                await asyncio.sleep(self.sleep_tune)
        return self.query_reply_data.get(PrivateConstants.REPORT_VERSION)

    async def get_pin_state(self, pin):
        """
        This method retrieves a pin state report for the specified pin

        :param pin: Pin of interest

        :returns: pin state report
        """
        # place pin in a list to keep _send_sysex happy
        await self._send_sysex(PrivateConstants.PIN_STATE_QUERY, [pin])
        while self.query_reply_data.get(
                PrivateConstants.PIN_STATE_RESPONSE) is None:
            await asyncio.sleep(self.sleep_tune)
        pin_state_report = self.query_reply_data.get(
            PrivateConstants.PIN_STATE_RESPONSE)
        self.query_reply_data[PrivateConstants.PIN_STATE_RESPONSE] = None
        return pin_state_report

    # noinspection PyMethodMayBeStatic
    async def get_pymata_version(self):
        """
        This method retrieves the PyMata version number

        :returns: PyMata version number.
        """
        return PrivateConstants.PYMATA_EXPRESS_VERSION

    # noinspection PyIncorrectDocstring
    async def i2c_config(self, read_delay_time=0):
        """
        NOTE: THIS METHOD MUST BE CALLED BEFORE ANY I2C REQUEST IS MADE
        This method initializes Firmata for I2c operations.

        :param read_delay_time (in microseconds): an optional parameter,
                                                  default is 0

        :returns: No Return Value
        """
        data = [read_delay_time & 0x7f, (read_delay_time >> 7) & 0x7f]
        await self._send_sysex(PrivateConstants.I2C_CONFIG, data)

    async def i2c_read_data(self, address):
        """
        This method retrieves cached i2c data to support a polling mode.

        :param address: I2C device address

        :returns: Last cached value read
        """
        if address in self.i2c_map:
            map_entry = self.i2c_map.get(address)
            data = map_entry.get('value')
            return data
        else:
            return None

    async def i2c_read_request(self, address, register, number_of_bytes,
                               read_type, cb=None, cb_type=None):
        """
        This method requests the read of an i2c device. Results are retrieved
        by a call to i2c_get_read_data(). or by callback.

        If a callback method is provided, when data is received from the
        device it will be sent to the callback method.
        Some devices require that transmission be restarted
        (e.g. MMA8452Q accelerometer).
        Use Constants.I2C_READ | Constants.I2C_END_TX_MASK for those cases.

        :param address: i2c device address

        :param register: register number (can be set to zero)

        :param number_of_bytes: number of bytes expected to be returned

        :param read_type: I2C_READ  or I2C_READ_CONTINUOUSLY. I2C_END_TX_MASK
                          may be OR'ed when required

        :param cb: Optional callback function to report i2c data as a
                   result of read command

        :param cb_type: Constants.CB_TYPE_DIRECT = direct call or
                        Constants.CB_TYPE_ASYNCIO = asyncio coroutine

        :returns: No return value.
        """
        if address not in self.i2c_map:
            # self.i2c_map[address] = [None, cb]
            self.i2c_map[address] = {'value': None, 'callback': cb,
                                     'callback_type': cb_type}
        data = [address, read_type, register & 0x7f, (register >> 7) & 0x7f,
                number_of_bytes & 0x7f, (number_of_bytes >> 7) & 0x7f]
        await self._send_sysex(PrivateConstants.I2C_REQUEST, data)

    async def i2c_write_request(self, address, args):
        """
        Write data to an i2c device.

        :param address: i2c device address

        :param args: A variable number of bytes to be sent to the device
                     passed in as a list

        :returns: No return value.
        """
        data = [address, Constants.I2C_WRITE]
        for item in args:
            item_lsb = item & 0x7f
            data.append(item_lsb)
            item_msb = (item >> 7) & 0x7f
            data.append(item_msb)
        await self._send_sysex(PrivateConstants.I2C_REQUEST, data)

    async def keep_alive(self, period=1, margin=.3):
        """
        Periodically send a keep alive message to the Arduino.
        Frequency of keep alive transmission is calculated as follows:
        keep_alive_sent = period - (period * margin)


        :param period: Time period between keepalives. Range is 0-10 seconds.
                       0 disables the keepalive mechanism.

        :param margin: Safety margin to assure keepalives are sent before
                    period expires. Range is 0.1 to 0.9
        :returns: No return value
        """
        if period < 0:
            period = 0
        if period > 10:
            period = 10
        self.period = period
        if margin < .1:
            margin = .1
        if margin > .9:
            margin = .9
        self.margin = margin
        self.keep_alive_interval = [period & 0x7f, (period >> 7) & 0x7f]
        await self._send_sysex(PrivateConstants.SAMPLING_INTERVAL,
                               self.keep_alive_interval)
        while True:
            if self.period:
                await asyncio.sleep(period - (period - (period * margin)))
                await self._send_sysex(PrivateConstants.KEEP_ALIVE,
                                       self.keep_alive_interval)
            else:
                break

    async def play_tone(self, pin, tone_command, frequency, duration):
        """
        This method will call the Tone library for the selected pin.
        It requires FirmataPlus to be loaded onto the arduino

        If the tone command is set to TONE_TONE, then the specified
        tone will be played.

        Else, if the tone command is TONE_NO_TONE, then any currently
        playing tone will be disabled.

        :param pin: Pin number

        :param tone_command: Either TONE_TONE, or TONE_NO_TONE

        :param frequency: Frequency of tone

        :param duration: Duration of tone in milliseconds

        :returns: No return value
        """
        # convert the integer values to bytes
        if tone_command == Constants.TONE_TONE:
            # duration is specified
            if duration:
                data = [tone_command, pin, frequency & 0x7f, (frequency >> 7) & 0x7f,
                        duration & 0x7f, (duration >> 7) & 0x7f]

            else:
                data = [tone_command, pin,
                        frequency & 0x7f, (frequency >> 7) & 0x7f, 0, 0]
        # turn off tone
        else:
            data = [tone_command, pin]
        await self._send_sysex(PrivateConstants.TONE_DATA, data)

    async def send_reset(self):
        """
        Send a Sysex reset command to the arduino

        :returns: No return value.
        """
        try:
            await self._send_command([PrivateConstants.SYSTEM_RESET])
        except RuntimeError:
            sys.exit(0)

    async def servo_config(self, pin, min_pulse=544, max_pulse=2400):
        """
        Configure a pin as a servo pin. Set pulse min, max in ms.
        Use this method (not set_pin_mode) to configure a pin for servo
        operation.

        :param pin: Servo Pin.

        :param min_pulse: Min pulse width in ms.

        :param max_pulse: Max pulse width in ms.

        :returns: No return value
        """
        command = [pin, min_pulse & 0x7f, (min_pulse >> 7) & 0x7f, max_pulse & 0x7f,
                   (max_pulse >> 7) & 0x7f]

        await self._send_sysex(PrivateConstants.SERVO_CONFIG, command)

    async def set_pin_mode(self, pin_number, pin_state, callback=None,
                           callback_type=Constants.CB_TYPE_ASYNCIO):
        """
        This method sets the pin mode for the specified pin.
        For Servo, use servo_config() instead.

        :param pin_number: Arduino Pin Number

        :param pin_state: INPUT/OUTPUT/ANALOG/PWM/PULLUP - for SERVO use
                          servo_config()

        :param callback: Optional: A reference to a call back function to be
                         called when pin data value changes

        :param callback_type: Constants.CB_TYPE_DIRECT = direct call or
                        Constants.CB_TYPE_ASYNCIO = asyncio coroutine

        :returns: No return value
        """

        # There is a potential start up race condition when running pymata3.
        # This is a workaround for that race condition
        #
        if not len(self.digital_pins):
            await asyncio.sleep(2)
        if callback:
            if pin_state == Constants.INPUT:
                self.digital_pins[pin_number].cb = callback
                self.digital_pins[pin_number].cb_type = callback_type
            elif pin_state == Constants.ANALOG:
                self.analog_pins[pin_number].cb = callback
                self.analog_pins[pin_number].cb_type = callback_type
            else:
                print('{} {}'.format('set_pin_mode: callback ignored for '
                                         'pin state:', pin_state))

        pin_mode = pin_state

        if pin_mode == Constants.ANALOG:
            pin_number = pin_number + self.first_analog_pin

        command = [PrivateConstants.SET_PIN_MODE, pin_number, pin_mode]
        await self._send_command(command)
        if pin_state == Constants.ANALOG:
            await self.enable_analog_reporting(pin_number)
        elif pin_state == Constants.INPUT:
            await self.enable_digital_reporting(pin_number)
        else:
            pass

        await self.sleep(.05)

    async def set_sampling_interval(self, interval):
        """
        This method sends the desired sampling interval to Firmata.
        Note: Standard Firmata  will ignore any interval less than
              10 milliseconds

        :param interval: Integer value for desired sampling interval
                         in milliseconds

        :returns: No return value.
        """
        data = [interval & 0x7f, (interval >> 7) & 0x7f]
        await self._send_sysex(PrivateConstants.SAMPLING_INTERVAL, data)

    async def shutdown(self):
        """
        This method attempts an orderly shutdown
        If any exceptions are thrown, just ignore them.

        :returns: No return value
        """

        self.shutdown_flag = True

        for pin in range(len(self.analog_pins)):
           await self.disable_analog_reporting(pin)

        for pin in range(len(self.digital_pins)):
            await self.disable_digital_reporting(pin)


        try:
            # self.loop.close()
            await self.serial_port.reset_input_buffer()
            await self.serial_port.close()
            self.loop.stop()
        except RuntimeError:
            pass

    async def sleep(self, sleep_time):
        """
        This method is a proxy method for asyncio.sleep

        :param sleep_time: Sleep interval in seconds

        :returns: No return value.
        """
        try:
            await asyncio.sleep(sleep_time)
        except RuntimeError('sleep exception'):
            await self.shutdown()

    async def sonar_config(self, trigger_pin, echo_pin, cb=None,
                           ping_interval=50, max_distance=200, cb_type=None):
        """
        Configure the pins,ping interval and maximum distance for an HC-SR04
        type device.
        Single pin configuration may be used. To do so, set both the trigger
        and echo pins to the same value.
        Up to a maximum of 6 SONAR devices is supported
        If the maximum is exceeded a message is sent to the console and the
        request is ignored.
        NOTE: data is measured in centimeters

        :param trigger_pin: The pin number of for the trigger (transmitter).

        :param echo_pin: The pin number for the received echo.

        :param cb: optional callback function to report sonar data changes

        :param ping_interval: Minimum interval between pings. Lowest number
                              to use is 33 ms. Max is 127ms.

        :param max_distance: Maximum distance in cm. Max is 200.

        :param cb_type: Constants.CB_TYPE_DIRECT = direct call or
                        Constants.CB_TYPE_ASYNCIO = asyncio coroutine
        :returns: No return value.
        """
        # if there is an entry for the trigger pin in existence, just exit
        if trigger_pin in self.active_sonar_map:
            return

        if max_distance > 200:
            max_distance = 200
        max_distance_lsb = max_distance & 0x7f
        max_distance_msb = (max_distance >> 7) & 0x7f
        data = [trigger_pin, echo_pin, ping_interval, max_distance_lsb,
                max_distance_msb]
        await self.set_pin_mode(trigger_pin, Constants.SONAR, Constants.INPUT)
        await self.set_pin_mode(echo_pin, Constants.SONAR, Constants.INPUT)
        # update the ping data map for this pin
        if len(self.active_sonar_map) > 6:
            print('sonar_config: maximum number of devices assigned'
                  ' - ignoring request')
        else:
            self.active_sonar_map[trigger_pin] = [cb, cb_type, 0]

        await self._send_sysex(PrivateConstants.SONAR_CONFIG, data)

    async def sonar_data_retrieve(self, trigger_pin):
        """
        Retrieve Ping (HC-SR04 type) data. The data is presented as a
        dictionary.
        The 'key' is the trigger pin specified in sonar_config()
        and the 'data' is the current measured distance (in centimeters)
        for that pin. If there is no data, the value is set to None.

        :param trigger_pin: key into sonar data map

        :returns: active_sonar_map
        """
        # sonar_pin_entry = self.active_sonar_map[pin]
        sonar_pin_entry = self.active_sonar_map.get(trigger_pin)
        value = sonar_pin_entry[1]
        return value

    async def stepper_config(self, steps_per_revolution, stepper_pins):
        """
        Configure stepper motor prior to operation.
        This is a FirmataPlus feature.

        :param steps_per_revolution: number of steps per motor revolution

        :param stepper_pins: a list of control pin numbers - either 4 or 2

        :returns: No return value.
        """
        data = [PrivateConstants.STEPPER_CONFIGURE, steps_per_revolution & 0x7f,
                (steps_per_revolution >> 7) & 0x7f]
        for pin in range(len(stepper_pins)):
            data.append(stepper_pins[pin])
        await self._send_sysex(PrivateConstants.STEPPER_DATA, data)

    async def stepper_step(self, motor_speed, number_of_steps):
        """
        Move a stepper motor for the number of steps at the specified speed
        This is a FirmataPlus feature.

        :param motor_speed: 21 bits of data to set motor speed

        :param number_of_steps: 14 bits for number of steps & direction
                                positive is forward, negative is reverse

        :returns: No return value.
        """
        if number_of_steps > 0:
            direction = 1
        else:
            direction = 0
        abs_number_of_steps = abs(number_of_steps)
        data = [PrivateConstants.STEPPER_STEP, motor_speed & 0x7f,
                (motor_speed >> 7) & 0x7f, (motor_speed >> 14) & 0x7f,
                abs_number_of_steps & 0x7f, (abs_number_of_steps >> 7) & 0x7f, direction]
        await self._send_sysex(PrivateConstants.STEPPER_DATA, data)

    async def _arduino_report_dispatcher(self):
        """
        This is a private method.
        It continually accepts and interprets data coming from Firmata,and then
        dispatches the correct handler to process the data.

        :returns: This method never returns
        """
        # sysex commands are assembled into this list for processing
        sysex = []

        while True:
            try:
                if self.shutdown_flag:
                    break
                next_command_byte = await self.serial_port.read()
                # if this is a SYSEX command, then assemble the entire
                # command process it
                if next_command_byte == PrivateConstants.START_SYSEX:
                    while next_command_byte != PrivateConstants.END_SYSEX:
                        # await asyncio.sleep(self.sleep_tune)
                        next_command_byte = await self.serial_port.read()
                        sysex.append(next_command_byte)
                    await self.command_dictionary[sysex[0]](sysex)
                    sysex = []
                    # await asyncio.sleep(self.sleep_tune)
                # if this is an analog message, process it.
                elif 0xE0 <= next_command_byte <= 0xEF:
                    # analog message
                    # assemble the entire analog message in command
                    command = []
                    # get the pin number for the message
                    pin = next_command_byte & 0x0f
                    command.append(pin)
                    # get the next 2 bytes for the command
                    command = await self._wait_for_data(command, 2)
                    # process the analog message
                    await self._analog_message(command)
                # handle the digital message
                elif 0x90 <= next_command_byte <= 0x9F:
                    command = []
                    port = next_command_byte & 0x0f
                    command.append(port)
                    command = await self._wait_for_data(command, 2)
                    await self._digital_message(command)
                # handle all other messages by looking them up in the
                # command dictionary
                elif next_command_byte in self.command_dictionary:
                    await self.command_dictionary[next_command_byte]()
                    await asyncio.sleep(self.sleep_tune)
                else:
                    # we need to yield back to the loop
                    # await asyncio.sleep(self.sleep_tune)
                    continue
            except:
                raise


    '''
    Firmata message handlers
    '''

    async def _analog_mapping_response(self, data):
        """
        This is a private message handler method.
        It is a message handler for the analog mapping response message

        :param data: response data

        :returns: none - but saves the response
        """
        self.query_reply_data[PrivateConstants.ANALOG_MAPPING_RESPONSE] = \
            data[1:-1]

    async def _analog_message(self, data):
        """
        This is a private message handler method.
        It is a message handler for analog messages.

        :param data: message data

        :returns: None - but saves the data in the pins structure
        """
        pin = data[0]
        value = (data[PrivateConstants.MSB] << 7) + data[PrivateConstants.LSB]

        # only report when there is a change in value
        differential = abs(value - self.analog_pins[pin].current_value)
        if differential >= self.analog_report_differential:
            self.analog_pins[pin].current_value = value
            time_stamp = self.loop.time()
            self.digital_pins[pin].event_time = time_stamp

            # append pin number, pin value, and pin type to return value and return as a list
            message = [pin, value, Constants.ANALOG, time_stamp]

            if self.analog_pins[pin].cb:
                if self.analog_pins[pin].cb_type:
                    await self.analog_pins[pin].cb(message)
                else:
                    loop = self.loop
                    loop.call_soon(self.analog_pins[pin].cb, message)

    async def _capability_response(self, data):
        """
        This is a private message handler method.
        It is a message handler for capability report responses.

        :param data: capability report

        :returns: None - but report is saved
        """
        self.query_reply_data[PrivateConstants.CAPABILITY_RESPONSE] = data[1:-1]

    async def _digital_message(self, data):
        """
        This is a private message handler method.
        It is a message handler for Digital Messages.

        :param data: digital message

        :returns: None - but update is saved in pins structure
        """
        port = data[0]
        port_data = (data[PrivateConstants.MSB] << 7) + \
                    data[PrivateConstants.LSB]
        pin = port * 8
        for pin in range(pin, min(pin + 8, len(self.digital_pins))):
            # get pin value
            value = port_data & 0x01

            # set the current value in the pin structure
            self.digital_pins[pin].current_value = value
            time_stamp = self.loop.time()
            self.digital_pins[pin].event_time = time_stamp

            # append pin number, pin value, and pin type to return value and return as a list
            message = [pin, value, Constants.INPUT, time_stamp]

            if self.digital_pins[pin].cb:
                if self.digital_pins[pin].cb_type:
                    await self.digital_pins[pin].cb(message)
                else:
                    # self.digital_pins[pin].cb(data)
                    loop = self.loop
                    loop.call_soon(self.digital_pins[pin].cb, message)

            port_data >>= 1

    async def _encoder_data(self, data):
        """
        This is a private message handler method.
        It handles encoder data messages.

        :param data: encoder data

        :returns: None - but update is saved in the digital pins structure
        """
        # strip off sysex start and end
        data = data[1:-1]
        pin = data[0]
        val = int((data[PrivateConstants.MSB] << 7) +
                  data[PrivateConstants.LSB])
        # set value so that it shows positive and negative values
        if val > 8192:
            val -= 16384
        # if this value is different that is what is already in the
        # table store it and check for callback
        if val != self.digital_pins[pin].current_value:
            self.digital_pins[pin].current_value = val
            if self.digital_pins[pin].cb:
                # self.digital_pins[pin].cb([pin, val])
                if self.digital_pins[pin].cb_type:
                    await self.digital_pins[pin].cb(val)
                else:
                    # self.digital_pins[pin].cb(data)
                    loop = self.loop
                    loop.call_soon(self.digital_pins[pin].cb, val)

    # noinspection PyDictCreation

    async def _i2c_reply(self, data):
        """
        This is a private message handler method.
        It handles replies to i2c_read requests. It stores the data
        for each i2c device address in a dictionary called i2c_map.
        The data may be retrieved via a polling call to i2c_get_read_data().
        It a callback was specified in pymata.i2c_read, the raw data is sent
        through the callback

        :param data: raw data returned from i2c device

        """
        # remove the start and end sysex commands from the data
        data = data[1:-1]
        reply_data = []
        # reassemble the data from the firmata 2 byte format
        address = (data[0] & 0x7f) + (data[1] << 7)

        # if we have an entry in the i2c_map, proceed
        if address in self.i2c_map:
            # get 2 bytes, combine them and append to reply data list
            for i in range(0, len(data), 2):
                combined_data = (data[i] & 0x7f) + (data[i + 1] << 7)
                reply_data.append(combined_data)

            # place the data in the i2c map without storing the address byte or
            #  register byte (returned data only)
            map_entry = self.i2c_map.get(address)
            map_entry['value'] = reply_data[2:]
            self.i2c_map[address] = map_entry
            cb = map_entry.get('callback')
            cb_type = map_entry.get('callback_type')
            if cb:
                # send everything, including address and register bytes back
                # to caller
                if cb_type:
                    await cb(reply_data)
                else:
                    loop = self.loop
                    loop.call_soon(cb, reply_data)
                await asyncio.sleep(self.sleep_tune)

    async def _pin_state_response(self, data):
        """
        This is a private message handler method.
        It handles pin state query response messages.

        :param data: Pin state message

        :returns: None - but response is saved
        """
        self.query_reply_data[PrivateConstants.PIN_STATE_RESPONSE] = data[1:-1]

    async def _report_firmware(self, sysex_data):
        """
        This is a private message handler method.
        This method handles the sysex 'report firmware' command sent by
        Firmata (0x79).
        It assembles the firmware version by concatenating the major and
         minor version number components and
        the firmware identifier into a string.
        e.g. "2.3 StandardFirmata.ino"

        :param sysex_data: Sysex data sent from Firmata

        :returns: None
        """
        # first byte after command is major number
        major = sysex_data[1]
        version_string = str(major)

        # next byte is minor number
        minor = sysex_data[2]

        # append a dot to major number
        version_string += '.'

        # append minor number
        version_string += str(minor)
        # add a space after the major and minor numbers
        version_string += ' '

        # slice the identifier - from the first byte after the minor
        #  number up until, but not including the END_SYSEX byte

        name = sysex_data[3:-1]
        firmware_name_iterator = iter(name)

        # convert each element from two 7-bit bytes into characters, then add each
        # character to the version string
        for e in firmware_name_iterator:
            version_string += chr(e + (next(firmware_name_iterator) << 7))

        # store the value
        self.query_reply_data[PrivateConstants.REPORT_FIRMWARE] = version_string

    async def _report_version(self):
        """
        This is a private message handler method.
        This method reads the following 2 bytes after the report version
        command (0xF9 - non sysex).
        The first byte is the major number and the second byte is the
        minor number.

        :returns: None
        """
        # get next two bytes
        major = await self.serial_port.read()
        version_string = str(major)
        minor = await self.serial_port.read()
        version_string += '.'
        version_string += str(minor)
        self.query_reply_data[PrivateConstants.REPORT_VERSION] = version_string

    async def _sonar_data(self, data):
        """
        This method handles the incoming sonar data message and stores
        the data in the response table.

        :param data: Message data from Firmata

        :returns: No return value.
        """

        # strip off sysex start and end
        data = data[1:-1]
        pin_number = data[0]
        val = int((data[PrivateConstants.MSB] << 7) +
                  data[PrivateConstants.LSB])
        reply_data = []

        sonar_pin_entry = self.active_sonar_map[pin_number]

        if sonar_pin_entry[0] is not None:
            # check if value changed since last reading
            if sonar_pin_entry[2] != val:
                sonar_pin_entry[2] = val
                self.active_sonar_map[pin_number] = sonar_pin_entry
                # Do a callback if one is specified in the table
                if sonar_pin_entry[0]:
                    # if this is an asyncio callback type
                    reply_data.append(pin_number)
                    reply_data.append(val)
                    if sonar_pin_entry[1]:
                        await sonar_pin_entry[0](reply_data)
                    else:
                        # sonar_pin_entry[0]([pin_number, val])
                        loop = self.loop
                        loop.call_soon(sonar_pin_entry[0], reply_data)
        # update the data in the table with latest value
        else:
            sonar_pin_entry[1] = val
            self.active_sonar_map[pin_number] = sonar_pin_entry

        await asyncio.sleep(self.sleep_tune)

    # noinspection PyMethodMayBeStatic
    async def _string_data(self, data):
        """
        This is a private message handler method.
        It is the message handler for String data messages that will be
        printed to the console.
        :param data:  message

        :returns: None - message is sent to console
        """
        reply = ''
        data = data[1:-1]
        for x in data:
            reply_data = x
            if reply_data:
                reply += chr(reply_data)
        print(reply)

    '''
    utilities
    '''

    # noinspection PyMethodMayBeStatic
    def _format_capability_report(self, data):
        """
        This is a private utility method.
        This method formats a capability report if the user wishes to
        send it to the console.
        If log_output = True, no output is generated

        :param data: Capability report

        :returns: None
        """




        pin_modes = {0: 'Digital_Input', 1: 'Digital_Output',
                     2: 'Analog', 3: 'PWM', 4: 'Servo',
                     5: 'Shift', 6: 'I2C', 7: 'One Wire',
                     8: 'Stepper', 9: 'Encoder'}
        x = 0
        pin = 0

        print('\nCapability Report')
        print('-----------------\n')
        while x < len(data):
            # get index of next end marker
            print('{} {}{}'.format('Pin', str(pin), ':'))
            while data[x] != 127:
                mode_str = ""
                pin_mode = pin_modes.get(data[x])
                mode_str += str(pin_mode)
                x += 1
                bits = data[x]
                print('{:>5}{}{} {}'.format('  ', mode_str, ':', bits))
                x += 1
            x += 1
            pin += 1

    async def _send_command(self, command):
        """
        This is a private utility method.
        The method sends a non-sysex command to Firmata.

        :param command:  command data

        :returns: length of data sent
        """
        send_message = ""

        for i in command:
            send_message += chr(i)
        result = None
        for data in send_message:
            try:
                result = await self.serial_port.write(data)
            except:
                raise RuntimeError('cannot send command')

        return result

    async def _send_sysex(self, sysex_command, sysex_data=None):
        """
        This is a private utility method.
        This method sends a sysex command to Firmata.

        :param sysex_command: sysex command

        :param sysex_data: data for command

        :returns : No return value.
        """
        if not sysex_data:
            sysex_data = []

        # convert the message command and data to characters
        sysex_message = chr(PrivateConstants.START_SYSEX)
        sysex_message += chr(sysex_command)
        if len(sysex_data):
            for d in sysex_data:
                sysex_message += chr(d)
        sysex_message += chr(PrivateConstants.END_SYSEX)

        for data in sysex_message:
            await self.serial_port.write(data)

    async def _wait_for_data(self, current_command, number_of_bytes):
        """
        This is a private utility method.
        This method accumulates the requested number of bytes and
        then returns the full command

        :param current_command:  command id

        :param number_of_bytes:  how many bytes to wait for

        :returns: command
        """
        while number_of_bytes:
            next_command_byte = await self.serial_port.read()
            current_command.append(next_command_byte)
            number_of_bytes -= 1
        return current_command
