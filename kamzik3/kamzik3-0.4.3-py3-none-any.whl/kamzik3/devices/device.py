import logging
import time
from collections import deque
from copy import copy
from math import inf
from threading import Thread

import numpy as np
import serial
from pint import UndefinedUnitError, DimensionalityError

import kamzik3
from kamzik3 import WriteException, CommandFormatException, DeviceError, units
from kamzik3.constants import *
from kamzik3.devices.attribute import Attribute, SetFunction
from kamzik3.devices.subject import Subject
from kamzik3.snippets.snippetDataAccess import get_from_dict, set_in_dict, fullname
from kamzik3.snippets.snippetsControlLoops import control_device_poller
from kamzik3.snippets.snippetsGenerators import device_id_generator, token_generator
from kamzik3.snippets.snippetsUnits import device_units
from kamzik3.snippets.snippetsYaml import YamlSerializable


class Device(Subject, YamlSerializable):
    """
    Connection is done in sequence:
        : connect()
        : handle_connect_event()
            : handle_connect()
            : handle_configuration_event()
                : handle_configuration()

    Connection error handling:
        : if connect() => error state
           : disconnect() if critical error
           : cloe(), reconnect() if not critical error
        : if connect() => connection timeout
            : handle_connection_error(), close(), reconnect()
        : if Device.connected and response timeout()
            : handle_response_error(), close_connection(), reconnect()

    Disconnection is done in sequence:
        : disconnect()
            : close() if not Device.connected
            : close_connection() if connected
                : close()
    """
    id_generator = device_id_generator()
    device_id = None
    connection_timeout = 4000
    response_timeout = 4000
    allow_reconnect = True
    config = None
    # Size of command buffer used in push
    push_buffer_size = 2 ** 16
    device_server = None
    session = None
    # Maximum number of commands joined in one request
    push_commands_max = inf
    max_command_retry = 0
    command_retry_count = 0

    def __init__(self, device_id=None, config=None):
        Subject.__init__(self)
        self.device_poller = control_device_poller
        self.device_id = device_id
        self.config = config
        self.qualified_name = fullname(self)
        if self.config is None:
            self.config = {}
        if device_id is None:
            self.device_id = next(Device.id_generator)
        if not hasattr(self, "logger"):
            self.logger = logging.getLogger("Device.{}".format(self.device_id))
        if self.config.get("push_commands_max", None) is not None:
            self.push_commands_max = self.config.get("push_commands_max")
        if self.config.get("push_buffer_size", None) is not None:
            self.push_buffer_size = self.config.get("push_buffer_size")
        if not self.push_commands_max:
            self.push_commands_max = inf
        self.macro_steps = {MACRO_SET_ATTRIBUTE_STEP: ["*"], MACRO_EXECUTE_METHOD_STEP: ["*"]}
        self.exposed_methods = []
        # Check if attributes are already defined
        if not hasattr(self, "attributes"):
            self.attributes = {}
            self.attributes_sharing_map = {}
            self._init_attributes()
        self.token_generator = token_generator()
        self.connecting_time = 0
        self.response_timestamp = 0
        self.request_timestamp = 0
        self.connected = False
        self.connecting = False
        self.closing = False
        self.closed = False
        self.connection_error = False
        self.response_error = False
        self.latency_buffer = []
        self.init_time = time.time()
        self.init_timeout = self.init_time
        self.commands_buffer = deque()
        if kamzik3.session is not None and self.device_id not in kamzik3.session.devices:
            self.set_session(kamzik3.session)

    def __getitem__(self, item):
        return self.attributes[item]

    def __setitem__(self, key, value):
        self.attributes[key] = value

    def _init_attributes(self):
        """
        Initiate Device's attributes.
        To call this method is mandatory.
        Overload this method for any other derived Device.
        """

        def set_status(key, value):
            if key == VALUE:
                self.notify(ATTR_STATUS, value)

        status_attribute = Attribute(STATUS_DISCONNECTED, readonly=True, description="Current device status")
        status_attribute.attach_callback(set_status)

        self.attributes = {
            ATTR_ID: Attribute(self.device_id, readonly=True, description="Unique device ID"),
            ATTR_STATUS: status_attribute,
            ATTR_DESCRIPTION: Attribute(readonly=True, description="Device description"),
            ATTR_ENABLED: Attribute(True, default_type=np.bool, description="Allow any external changes to device"),
            ATTR_LATENCY: Attribute(0, default_type=np.uint16,
                                    description="Latency between sending command and receiving an answer",
                                    min_value=0, max_value=9999, unit="ms", readonly=True),
            ATTR_BUFFERED_COMMANDS: Attribute(0, default_type=np.uint32,
                                              description="Amount of commands waiting to be executed",
                                              min_value=0, readonly=True),
            ATTR_HANGING_COMMANDS: Attribute(0, default_type=np.uint32,
                                             description="Amount of commands waiting to be answered from device",
                                             min_value=0, readonly=True),
            ATTR_LAST_ERROR: Attribute(None, readonly=True, description="Last device error exception"),
        }

    def share_attribute(self, source_device, source_attribute_group, target_attribute_group, shared_attributes=ALL):
        """
        Share attribute ensures that attributes from one device are mirrored to current device.
        On the client side we use attributes_sharing_map to see which devices, groups and attributes are involved.
        Using this approach we can save traffic. We don't have to use data twice, just once and simply use subscription
        to attributes topic.
        :param source_device: Device
        :param source_attribute_group: Attribute group we want to share or None
        :param target_attribute_group: Attribute group where we want to put shared attributes
        :param shared_attributes: list of attributes we want to share or ALL for all attributes in group
        :return: None
        """
        if target_attribute_group is None:
            target = self.attributes
        else:
            if target_attribute_group not in self.attributes:
                self.attributes[target_attribute_group] = {}
            target = self.attributes[target_attribute_group]

        if source_attribute_group is not None:
            assert source_attribute_group in source_device.attributes
            source = source_device[source_attribute_group]
        else:
            source = source_device.attributes

        if shared_attributes == ALL:
            target.update(source)
        else:
            for attribute in shared_attributes:
                target[attribute] = source[attribute]

        if source_device.device_id not in self.attributes_sharing_map:
            self.attributes_sharing_map[source_device.device_id] = {}

        self.attributes_sharing_map[source_device.device_id][source_attribute_group] = (
            target_attribute_group, shared_attributes)

    def share_exposed_method(self, source_device, source_method, shared_method_attributes=None):
        """
        Share exposed method with source_device.
        This is handy method when You share attributes of other device and You want to also expose it's methods.
        Each new method will go under new name source_device.id_source_method.name.
        If You define shared_method_attributes they will overwrite default ones.
        :param source_device: Device
        :param source_method: Name of exposed function
        :param shared_method_attributes: Dictionary of method attributes
        :return:
        """
        for method_name, method_parameters in source_device.exposed_methods:
            if method_name == source_method:
                shared_method_name = "{}_{}".format(source_device.device_id, method_name)
                if shared_method_attributes is None:
                    shared_method_attributes = method_parameters
                method = copy(getattr(source_device, method_name))
                # Check if method is meant to be exposed and remove exposed_parameters to prevent double exposing
                if hasattr(method, "exposed_parameters"):
                    del method.__dict__["exposed_parameters"]
                setattr(self, shared_method_name, method)
                self.exposed_methods.append((shared_method_name, shared_method_attributes))

    def set_session(self, session):
        """
        Set session for device.
        :param session: Session
        :return: None
        """
        self.session = session
        session.add_device(self)

    def reconnect_allowed(self):
        """
        Allow device to reconnect or not.
        :return: Bool
        """
        if self.connecting or self.connected:
            self.close()
            return True
        else:
            return self.allow_reconnect

    def attach_attribute_callback(self, attribute, callback, max_update_rate=None):
        """
        Attach callback for every change of attribute.
        If max_update_rate is specified that callback will be called only after
        specified timeout.
        :param attribute: [ATTRIBUTE]
        :param callback: callable
        :param max_update_rate: millisecond(s)
        :return: None
        """
        assert callable(callback)
        try:
            attribute = self._get(attribute)
            attribute.attach_callback(callback, max_update_rate)
        except (KeyError, AttributeError):
            self.logger.exception(u"Attribute {} is not defined".format(attribute))

    def detach_attribute_callback(self, attribute, callback):
        """
        Detach attached callback from attribute.
        :param attribute: [ATTRIBUTE]
        :param callback: callable
        :return: None
        """
        assert callable(callback)
        try:
            attribute = self._get(attribute)
            attribute.detach_callback(callback)
        except (KeyError, AttributeError):
            if self.logger is not None:
                self.logger.exception(u"Attribute {} is not defined".format(attribute))

    def set_attribute(self, attribute, value, callback=None):
        """
        This sets Device attribute.
        Re-implement it for client or any special use.
        :param attribute: tuple, list, str
        :param value: mixed
        :param callback: callable
        :return: None
        """
        set_token = 0
        if attribute[-1] == VALUE:
            device_attribute = self.get_attribute(attribute[:-1])
            with SetFunction(device_attribute, callback):
                self._set(attribute, value)
                set_token = device_attribute.read_and_reset_token()
                if not set_token and callback is not None:
                    callback(attribute, value)
        else:
            self._set(attribute, value)

        return set_token

    def get_attribute(self, attribute):
        """
        This gets Device attribute.
        Re-implement it for client or any special use.
        :param attribute: tuple, list, str
        :return: mixed
        """
        return self._get(attribute)

    def _set(self, attribute, value):
        """
        This sets Device attribute.
        Use this function when You want to set attribute by tuple or list key.
        Example: Device.set((ATTR_STATUS, VALUE), STATUS_IDLE)
        Attribute value is pushed into server if Device is connected on any.
        To reduce amount of pushed attributes we check if value is different from previous one.
        :param attribute: tuple, list, str
        :param value: mixed
        :return: None
        """
        if isinstance(attribute, (tuple, list)):
            current_value = get_from_dict(self.attributes, attribute)
            set_in_dict(self.attributes, attribute, value)
            if attribute[-1] == VALUE:
                # Get new value possibly affected by offset and factor
                value = get_from_dict(self.attributes, attribute)
        else:
            current_value = self.attributes[attribute]
            self.attributes[attribute] = value
            if attribute == VALUE:
                # Get new value possibly affected by offset and factor
                value = self.attributes[attribute]

        if value != current_value and self.device_server is not None:
            token = "{}.{}".format(TOKEN_ATTRIBUTE, ".".join(attribute))
            self.device_server.push_message(self.device_id, (attribute, value), token)

    def _get(self, attribute):
        """
        This gets Device attribute.
        Use this function when You want to get attribute by tuple or list key.
        Example: Device.get((ATTR_STATUS, VALUE))
        Otherwise use faster method Device[ATTR_STATUS][VALUE]
        :param attribute: tuple, list, str
        :return: mixed
        """
        try:
            if isinstance(attribute, (tuple, list)):
                return get_from_dict(self.attributes, attribute)
            else:
                return self.attributes.get(attribute)
        except (KeyError, TypeError):
            return None

    def connect(self, *args):
        """
        Call only this function to connect devices to port / socket / library / ...
        :param args: connect attributes
        """
        try:
            self.connecting = True
            self.connected = False
            self.device_poller.add_connecting_device(self)
            self.handle_connect_event()
        except DeviceError:
            self.logger.exception(u"Connection exception")
            return

    def handle_readout_callback(self, callback, attribute, output):
        """

        :param callback: callable
        :param attribute: [ATTRIBUTE]
        :param output: mixed
        :return: None
        """
        if callback is None:
            return
        else:
            assert callable(callback)
            callback(attribute, output)

    def handle_connect_event(self):
        """
        Handle connect event.
        This method is a wrapper in which connection is handled.
        Set everything important in handle_connect().
        """
        try:
            self.handle_connect()
            self.connected = True
            self.connecting = False
            self.handle_configuration_event()
        except DeviceError:
            """
            Here we encountered connection error.
            Log error and wait for reconnection.
            """
            self.logger.exception(u"Error during connection")

    def handle_connect(self):
        """
        Load configuration in this method.
        """
        self.set_status(STATUS_CONNECTED)
        self.logger.info(u"Device connection took {} sec.".format(time.time() - self.init_time))
        self.request_timestamp = self.response_timestamp = time.time()

    def handle_configuration_event(self):
        """
        Event from connected device to handle configuration.
        It servers as a wrapper around configuration routine.
        :return:
        """
        try:
            self.set_status(STATUS_CONFIGURING)
            self.handle_configuration()
        except DeviceError:
            self.logger.exception(u"Error during configuration")

    def handle_configuration(self):
        """
        Method is called whenever device is connected and ready to be configured
        :return: None
        """
        raise NotImplementedError(u"Must be implemented in subclass")

    def handle_response_error(self, message=None):
        """
        Method to handle response error of device
        :param message: cause of response error
        :return:
        """
        self.logger.error(message)
        self.response_error = True
        self.close_connection()

    def handle_connection_error(self, message=None):
        """
        Method to handle state of connection error
        :param message: cause of connection error
        :return: None
        """
        self.logger.error(message)
        self.connection_error = True
        self.close()

    def handle_command_error(self, readout_command, readout_output):
        """
        Method to handle state of command error
        :param readout_command: original command
        :param readout_output: error response from device
        :return: None
        """
        self.set_value(ATTR_LAST_ERROR, str(readout_output))
        self.logger.error(
            u"Command error\nCommand: {!r}\nOutput: {!r}\nCommand buffer: {!r}".format(readout_command, readout_output,
                                                                                       self.commands_buffer))

    def handle_observer_attached(self, observer):
        """
        Callback whenever observer is detached from the Subject
        :param observer: Observer
        :return: None
        """
        observer.subject_update(ATTR_STATUS, self.get_value(ATTR_STATUS), self)

    def handle_observer_detached(self, observer):
        """
        Callback whenever observer is attached to the Subject
        :param observer: Observer
        :return:
        """
        pass

    def handle_readout(self, readout_buffer):
        """
        We have data in readoutBuffer.
        Return tuple attribute, joined readoutBuffer
        :param readout_buffer:
        :return: str, str
        """
        self.response_timestamp = time.time()

        try:
            (attribute, token, callback, returning), command_init_timestamp = self.commands_buffer.popleft()
            latency = (time.time() - command_init_timestamp) * 1000
            self.latency_buffer.append(latency)
            if len(self.latency_buffer) == 20:
                self.set_attribute((ATTR_LATENCY, VALUE), sum(self.latency_buffer) / 20.)
                self.set_value(ATTR_HANGING_COMMANDS, len(self.commands_buffer))
                self.latency_buffer = []
        except IndexError:
            self.handle_response_error(
                u"Trying to pop from empty command buffer. Content of readout buffer is: {}".format(readout_buffer))
            return RESPONSE_ERROR, "", None, False

        return attribute, "".join(readout_buffer), callback, token

    def disconnect(self):
        """
        Call this function to cleanly close connection.
        After disconnect Device won't reconnect.
        :return:
        """
        if self.closing:
            return False
        elif self.connected:
            self.close_connection()
        elif self.connecting:
            self.close()

    def close(self):
        """
        Handle all devices closing stuff here.
        Close socket, close port, etc...
        """
        if self.closing:
            return False
        else:
            self.closing = True
            self.connected = False
            self.set_status(STATUS_DISCONNECTED)
            self.closing = False
            self.connected = False

    def reconnect(self):
        """
        Reconnect devices.
        If Device was reconnect return True, False otherwise.
        :return: bool
        """
        if self.reconnect_allowed():
            mapping = self.yaml_mapping()
            self.__init__(**mapping)
            return True
        else:
            return False

    def get_value(self, attribute):
        """
        Get attributes value
        :param attribute: list, dict, str
        :return: None
        """
        if isinstance(attribute, tuple):
            return self._get(attribute + (VALUE,))
        elif isinstance(attribute, list):
            return self._get(attribute + [VALUE])
        else:
            return self._get((attribute, VALUE))

    def get_value_and_unit(self, attribute):
        """
        Get attributes value
        :param attribute: list, dict, str
        :return: None
        """
        if isinstance(attribute, tuple):
            value, unit = self._get(attribute + (VALUE,)), self._get(attribute + (UNIT,))
        elif isinstance(attribute, list):
            value, unit = self._get(attribute + [VALUE]), self._get(attribute + [UNIT])
        else:
            value, unit = self._get((attribute, VALUE)), self._get((attribute, UNIT))

        return units.Quantity(value, unit)

    def set_value(self, attribute, value):
        """
        Set attributes value
        :param attribute: list, dict, str
        :param value: mixed
        :return: None
        """
        if isinstance(attribute, tuple):
            self._set(attribute + (VALUE,), value)
        elif isinstance(attribute, list):
            self._set(attribute + [VALUE], value)
        else:
            self._set((attribute, VALUE), value)

    def set_status(self, status):
        """
        Set attributes status value.
        :param status: str
        :return: None
        """
        self.set_value(ATTR_STATUS, status)

    def is_status(self, status):
        """
        Check status value against current device status
        :param status: STATUS
        :return: bool
        """
        return self.get_value(ATTR_STATUS) == status

    def in_statuses(self, statuses):
        """
        Check list of statuses against current device status
        :param statuses: list, tuple
        :return: bool
        """
        return self.get_value(ATTR_STATUS) in statuses

    def set_device_server(self, device_server):
        """
        Set device server
        :param device_server: DeviceServer
        :return: None
        """
        self.device_server = device_server

    def clear_device_server(self):
        self.device_server = None

    def stop_polling(self):
        """
        Remove Device from device_poller loop.
        """
        self.device_poller.stop_polling(self)

    def start_polling(self):
        """
        Add Device attributes to be polled in devicePoller loop.
            self.devicePoller.add(devices, command, time in milliseconds)
            self.devicePoller.add(self, 'cmd0', 400)
        """
        self.response_timestamp = self.request_timestamp = time.time()

    def close_connection(self):
        """
        Call this function when closing connected Devide.
        Stop polling and continue with close() method.
        """
        self.stop_polling()
        self.close()

    def push(self, data):
        """
        Send command to Device.
        This method will send data directly to the Device connection line.
        Use command() for sending commands from clients, etc.
        :param data: str
        """
        pass

    def command(self, command, callback=None, with_token=False, returning=True):
        """
        Send command to devices.
        Use only this function to send command to Device.
        Commands are stored into buffer and are flushed every pollDevice tick.
        :param command:
        :param callback:
        :param with_token:
        :param returning: bool
        :return:
        """
        if not self.valid_command_format(command):
            raise CommandFormatException(u"Command '{}' form is invalid".format(command))

        if self.connected or self.connecting:
            token = 0
            if with_token is True:
                token = next(self.token_generator)
            elif with_token >= 1:
                token = with_token
            self.device_poller.prepare_command(self, (command, token, callback, returning))
            return token

    def remove(self):
        """
        This method aims to remove device from runtime.
        :return:
        """
        self.disconnect()
        if self.logger is not None:
            for handler in self.logger.handlers[:]:
                handler.close()

        self.logger = None
        if self.session is not None:
            self.session.remove_device(self)

        self.attributes = None
        self.exposed_methods = None
        self.token_generator = None
        self.connecting_time = None
        self.response_timestamp = None
        self.request_timestamp = None
        self.connected = None
        self.connecting = None
        self.closing = None
        self.closed = None
        self.connection_error = None
        self.response_error = None
        self.commands_buffer = None

    def valid_command_format(self, command):
        """
        Check if command format is valid.
        Return False or optionally raise CommandFormatException.
        Re-implement this method for any other device.
        :param command:
        :return:
        """
        if command is not None:
            return True
        else:
            return False

    def send_command(self, commands):
        """
        Send command using defined interface (TCP/IP, RS232, ...).
        Unicode command is always .encode() into ASCII before it's send to the interface.
        :param commands: list of command to be send
        :return: list of NOT sent commands
        """
        try:
            if self.connected:
                command_string = u""
                commands_to_push_counter = 0
                while commands:
                    command = commands.pop(0)
                    commands_to_push_counter += 1
                    command_string += command[0]
                    if len(command_string) > self.push_buffer_size:
                        commands.insert(0, command)
                        command_string = command_string[:-len(command[0])]
                        break
                    if command[3]:  # If command is returning
                        self.commands_buffer.append((command, time.time()))
                    else:  # Command is not returning, simulate immediate execution
                        self.response_timestamp = time.time()
                    if commands_to_push_counter >= self.push_commands_max:
                        break
                self.push(command_string.encode())
            else:
                self.handle_response_error(u"Device is not connected")
        except IndexError:
            self.handle_connection_error(u"Device {} buffer error".format(self.device_id))
        except (WriteException, serial.SerialException):
            self.handle_response_error(u"Device {} writing error".format(self.device_id))
        finally:
            return commands

    def retry_command(self):
        """
        Retry to send command.
        :return: bool
        """
        if self.command_retry_count < self.max_command_retry:
            waiting_commands = self.commands_buffer.copy()
            self.commands_buffer = deque()
            for command in waiting_commands:
                self.device_poller.prepare_command(self, command[0])
            self.response_timestamp = time.time()
            self.command_retry_count += 1
            return True
        else:
            return False

    def accepting_commands(self):
        """
        Check if device is ready to send another commands.
        :return: bool
        """
        self.request_timestamp = time.time()
        if not self.connected or len(self.commands_buffer) > 0:
            return False
        else:
            return True

    def poll_command(self, command, interval):
        """
        Add command to device poller to be polled in desired interval.
        :param command: unicode string
        :param interval: interval in ms
        :return:
        """
        self.device_poller.add(self, command, interval)

    def remove_poll_command(self, command, interval):
        """
        Remove command from device poller.
        :param command:
        :param interval:
        :return:
        """
        self.device_poller.remove(self, command, interval)

    def _config_attributes(self):
        """
        Set attributes to desired values found in config.
        :return: None
        """
        if self.config:
            for attribute, value in self.config.get("attributes", {}).items():
                unit = self.get_attribute(attribute[:-1])[UNIT]
                if unit in (None, "") or attribute[-1] == UNIT:
                    self.set_attribute(attribute, value)
                else:
                    if isinstance(value, list):
                        set_value = []
                        for v in value:
                            try:
                                set_value.append(device_units(self, list(attribute[:-1]), v).m)
                            except (UndefinedUnitError, DimensionalityError):
                                set_value.append(v)
                    else:
                        try:
                            set_value = device_units(self, list(attribute[:-1]), value).m
                        except (UndefinedUnitError, DimensionalityError):
                            set_value = value
                    self.set_attribute(attribute, set_value)

    def _config_commands(self):
        """
        Execute required methods found in commands section of config
        :return: None
        """
        if self.config:
            for command in self.config.get("commands", []):
                self.command(command)

    def _expose_methods_to_clients(self):
        """
        Call this method if You wish to expose method decorated with @expose_method.
        This method is not called by default for Device!!!
        :return: None
        """
        for method in dir(self):
            method = getattr(self, method)
            if callable(method) and hasattr(method, "exposed_parameters"):
                self.exposed_methods.append((method.__name__, method.exposed_parameters))

    def wait_for_status(self, statuses, retry_timeout=1000, callback=None):
        """
        Wait until device change it's status in one defined in statuses.
        If callback is set, then method is executed in non blocking thread.
        :param statuses: List of one or multiple statuses to check against
        :param retry_timeout: Maximum time in ms to wait for status
        :param callback: Function to call after check in non blocking execution
        :return: True if device is in one of statuses
        """

        def _wait(_callback=None):
            return_value = False
            retry_counter = 0
            while not self.in_statuses(statuses) and self.connected:
                time.sleep(0.05)
                if retry_counter >= retry_timeout:
                    break
                retry_counter += 50
            if _callback is not None:
                _callback(return_value)
            else:
                return True

        if callback is None:
            return _wait()
        else:
            Thread(target=_wait, args=[callback]).start()

    def is_alive(self):
        if not self.connected or self.closing or self.response_error:
            return False

        time_diff = self.request_timestamp - self.response_timestamp
        if time_diff >= self.response_timeout * 1e-3:
            if not self.retry_command():
                print(self.commands_buffer, self.commands_buffer)
                self.handle_response_error(u"Device response timeout")