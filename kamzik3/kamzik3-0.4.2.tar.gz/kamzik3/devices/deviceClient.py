import json
import time
from threading import Thread, Event, Lock

import zmq

import kamzik3
from kamzik3 import SEP, DeviceClientError
from kamzik3.constants import *
from kamzik3.devices.attribute import Attribute
from kamzik3.devices.device import Device
from kamzik3.snippets.snippetDataAccess import get_from_dict, set_in_dict
from kamzik3.snippets.snippetsControlLoops import control_device_client_poller
from kamzik3.snippets.snippetsJson import JsonKamzikEncoder

""" Example of yaml configuration
DeviceClient0: &DeviceClient0 !Device:kamzik3.devices.deviceClient.DeviceClient
    host: &Server 127.0.0.1
    port: &Port 60000
    device_id: DeviceIdOnServer
"""


class DeviceClient(Device):
    """
    : connect()
    : handle_connect_event()
            : handle_connect()
            : handle_configuration_event()
                : handle_configuration()
    """
    initial_status = STATUS_DISCONNECTED

    def __init__(self, host, port, device_id=None, config=None):
        Device.__init__(self, device_id, config)
        self.client_comm_lock = Lock()
        self.device_poller = control_device_client_poller
        self.host = host
        self.port = port
        self.removing = False
        self.subscriber_port = None
        self.socket = None
        self.subscriber_socket = None
        self.callbacks = {}
        self.stopped = Event()
        self.subscribe_starts_with_list = []
        self.connect()

    def connect(self):
        """
        Here we want to connect first to ZMQ main server.
        We have to verify connection and do it in non blocking fashion.
        We just push devices in a pool and verify it in device_poller Thread.
        :return:
        """
        self.logger.info(u"Initiating connection to the server {}:{}".format(self.host, self.port))
        self.connecting = True
        self.connected = False
        self.set_status(STATUS_CONNECTING)
        # Get REQ type of socket
        self.socket = zmq.Context.instance().socket(zmq.REQ)
        # Set receive timeout to 3000 ms
        self.socket.setsockopt(zmq.RCVTIMEO, 3000)
        # Don't let socket linger after close
        # This is VERY IMPORTANT not to set to anything but 0
        self.socket.setsockopt(zmq.LINGER, 0)
        try:
            self.socket.connect("tcp://{}:{}".format(self.host, self.port))
            # Add socket to connection loop and return from connect method
            self.device_poller.add_connecting_device(self)
        except zmq.ZMQError:
            self.handle_connection_error(u"Fatal connection error")
            return

    def handle_connect_event(self):
        """
        This method is called after we verified connection with main server.
        We continue with init method to subscribe to devices publisher.
        :return: None
        """
        if self.init():
            self.connected = True
            self.connecting = False
            self.handle_configuration_event()

            self.set_status(self.get_attribute([ATTR_STATUS, VALUE]))

            # Subscribe for all attribute changes
            token = self.get_token(TOKEN_ATTRIBUTE)
            self._subscribe(token)
            self.subscribe_starts_with_list = token

            # Check for attribute sharing and subscribe to them
            if len(self.attributes_sharing_map) > 0:
                self.subscribe_starts_with_list = [self.subscribe_starts_with_list]
                for device_id, groups in self.attributes_sharing_map.items():
                    token = self.get_token(TOKEN_ATTRIBUTE, device_id)
                    for source_group, (target_group, source_attributes) in groups.items():
                        if source_group != "null":
                            sub_token = ".".join((token, source_group))
                            self.subscribe_starts_with_list.append("{}.{}".format(token, source_group))
                        else:
                            sub_token = token
                            self.subscribe_starts_with_list.append(sub_token)
                        if source_attributes == ALL:
                            self._subscribe(sub_token)
                        else:
                            for source_attribute in source_attributes:
                                self._subscribe(".".join((sub_token, source_attribute)))
                        self.subscribe_starts_with_list.append(sub_token)
                self.subscribe_starts_with_list = tuple(self.subscribe_starts_with_list)

    def reconnect_allowed(self):
        if self.connected:
            return False
        else:
            return self.allow_reconnect

    def _init_subscriber_thread(self):
        """
        We are connected to the main server.
        Now we want to connect to the devices publisher.
        :return: None
        """
        self.logger.info(u"Initializing {} client subscriber thread".format(self.device_id))
        # Get SUB type of socker
        self.subscriber_socket = zmq.Context.instance().socket(zmq.SUB)
        # Set receive timeout to 1000 ms
        self.subscriber_socket.setsockopt(zmq.RCVTIMEO, 2000)
        # Don't let socket linger after close
        # This is VERY IMPORTANT not to set to anything but 0
        self.subscriber_socket.setsockopt(zmq.LINGER, 0)
        self.subscriber_socket.connect("tcp://{}:{}".format(self.host, self.subscriber_port))
        # Start separate Thread to read data from publisher
        Thread(target=self._subscriber_thread).start()

    def _subscriber_thread(self):
        """
        Continuously collect data from publisher.
        Interrupt every zmq.RCVTIMEO and check if client is connected.
        :return: None
        """
        while not self.stopped.isSet():
            try:
                token, data = self.subscriber_socket.recv().decode().split(SEP)
                data = json.loads(data)
                self.handle_readout(token, data)
            except zmq.Again:
                # This exception is raised due mq.RCVTIMEO set to 1000ms.
                # We interrupt recv loop to check if devices is still connected
                # If not socket will be cleanly closed
                if self.connected and not self.client_comm_lock.locked():
                    self.poll()
            except AttributeError:
                pass  # Socket is not defined

        self.handle_closing_subscriber()

    def _subscribe(self, topic):
        """
        Subscribe for Topic.
        :param topic: string
        :return: None
        """
        self.subscriber_socket.setsockopt_string(zmq.SUBSCRIBE, topic)

    def _unsubscribe(self, topic):
        """
        Unsubscribe Topic.
        :param topic: string
        :return: None
        """
        self.subscriber_socket.setsockopt_string(zmq.UNSUBSCRIBE, topic)

    def set_callback(self, token, callback):
        """
        Set callback when token is received from publisher.
        If remove_after is set, remove callback from buffer and don't repeat it again.
        Callback has to be callable function.
        :param token: string
        :param callback: function(devices, data)
        :return: bool
        """
        assert callable(callback)

        if token not in self.callbacks:
            self.callbacks[token] = []

        callback_data = callback

        if callback_data not in self.callbacks[token]:
            self.callbacks[token].append(callback_data)
            self._subscribe(token)
            self.logger.debug(u"Set callback for token {}".format(token))
            return token
        else:
            self.logger.warning(u"Callback is already set")
            return False

    def handle_readout_callback(self, token, callback_data):
        """
        Handle callback for token.
        :param token: string
        :param callback_data: mixed
        :return: None
        """
        self._unsubscribe(token)
        while len(self.callbacks.get(token)) > 0:
            callback = self.callbacks.get(token).pop()
            callback(*callback_data)

        if len(self.callbacks[token]) == 0:
            del self.callbacks[token]

    def handle_readout(self, token, data):
        if token.startswith(self.subscribe_starts_with_list):
            source_device_id = token.split(".", 1)[0]
            if source_device_id != self.device_id:
                group = data[0][:-1][0]
                try:
                    (target_group, shared_attributes) = self.attributes_sharing_map[source_device_id][group]
                except KeyError:
                    group = "null"
                    (target_group, shared_attributes) = self.attributes_sharing_map[source_device_id][group]
                if group is "null" and target_group is not "null":
                    data[0].insert(0, target_group)
                elif group is not "null" and target_group is "null":
                    del data[0][0]
                else:
                    data[0][0] = target_group
            self._set(*data)
        elif token in self.callbacks:
            self.handle_readout_callback(token, data)

    def init(self):
        """
        Initiate devices connection.
        Get publisher port and devices attributes.
        :return:
        """
        try:
            with self.client_comm_lock:
                self.socket.send(SEP.join((self.device_id, INIT)).encode())
                status, token, response = self.handle_server_response()

            if status == RESPONSE_OK:
                self.subscriber_port, attributes, self.attributes_sharing_map, self.exposed_methods, self.qualified_name = json.loads(
                    response)
                self.initial_status = attributes[ATTR_STATUS][VALUE]
                self._sync_attributes(attributes)
                for method_name, attributes in self.exposed_methods[:]:
                    setattr(self, method_name,
                            lambda method_name=method_name, **kwargs: self.method(method_name, kwargs))
                self._init_subscriber_thread()
                return True
            else:
                raise DeviceClientError(u"Failed to initialize device")

        except (zmq.Again, zmq.ZMQError):
            self.handle_response_error(u"Init error")
            self.reconnect()
            return False

    def _sync_attributes(self, synced_attributes):
        """
        synchronize new attributes with already existing attributes.
        This is important to prevent creating new attribute objects.
        We can just create new attributes, but we would lost all callbacks and all references will become invalid.
        :param synced_attributes: dict
        :return:
        """
        # Walk thru all items of dictionary
        for key, attribute in synced_attributes.items():
            self._sync_attribute(key, attribute)

    def _sync_attribute(self, key, attribute):
        """
        synchronize one attribute from new dict to existing self.attributes
        :param key: string
        :param attribute: dict
        :return:
        """
        if key in self.attributes:
            if Attribute.is_attribute(attribute):
                if key == ATTR_STATUS:
                    return
                # Key exists in self.attributes
                # Prevent attribute changes when syncing with new values
                # with self.attributes[key].update_lock:
                for attr_key in attribute.keys():
                    if self.attributes[key][attr_key] != attribute[attr_key]:
                        self.attributes[key][attr_key] = attribute[attr_key]
            else:
                # Attribute is only sub group, continue syncing deeper
                self._sync_attributes(attribute)
        else:
            # Key des not exists in self.attributes
            if Attribute.is_attribute(attribute):
                # Create completely new Attribute under specified Key
                self.attributes[key] = Attribute.from_dict(attribute)
            else:
                # Attribute is only sub group, continue syncing deeper
                self.attributes[key] = Attribute.from_dict(attribute)

    def get_token(self, topic, device_id=None):
        return "{}.{}".format(self.device_id if device_id is None else device_id, topic)

    def set_attribute(self, attribute, value, callback=None):
        """
        Set attribute on devices server.
        :param attribute:
        :param value:
        :param callback:
        :return:
        """
        if not self.connected or self.closing:
            raise DeviceClientError(
                u"Remote set attribute {} to value {} failed. Device client is not connected".format(attribute, value))
        try:
            attribute_value = json.dumps((attribute, value), ensure_ascii=True)
            with self.client_comm_lock:
                self.socket.send(SEP.join((self.device_id, SET, attribute_value)).encode())
                status, token, response = self.handle_server_response()
            if status == RESPONSE_OK:
                if callback is not None:
                    if token:
                        self.set_callback(self.get_token(token), callback)
                    else:
                        callback(attribute, value)
            else:
                raise DeviceClientError(
                    u"Failed to set remote attribute {} to value {}\n{}".format(attribute, value, response))

            return response

        except (zmq.Again, zmq.ZMQError):
            self.handle_response_error(u"Set error")
            return False

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
        current_value = get_from_dict(self.attributes, attribute)
        if value == current_value:
            return
        set_in_dict(self.attributes, attribute, value)

    def poll(self):
        """
        Poll devices for activity.
        :return:
        """
        if not self.connected and not self.connecting or not self.socket:
            raise DeviceClientError(
                u"Remote server poll failed. Device client is not connected")
        try:
            with self.client_comm_lock:
                self.socket.send(SEP.join((self.device_id, POLL)).encode())
                status, token, response = self.handle_server_response()
            if status == RESPONSE_OK:
                return response
            else:
                raise DeviceClientError(u"Failed to poll remote device")

        except zmq.Again:
            return False
        except zmq.ZMQError as e:
            self.handle_response_error(u"Poll error: {}".format(e))
            return False

    def command(self, command, callback=None):
        """
        Execute raw command directly on devices.
        :param command: string
        :param callback: function(devices, outputOfCommand)
        :return:
        """
        if not self.connected or self.closing:
            raise DeviceClientError(
                u"Remote command {0!r} execution failed. Client is not connected".format(command))

        try:
            with self.client_comm_lock:
                self.socket.send(SEP.join((self.device_id, COMMAND, command, "1" if callback else "0")).encode())
                status, token, response = self.handle_server_response()

            if status == RESPONSE_OK:
                if token and callback is not None:
                    self.set_callback(self.get_token(token), callback)
            else:
                raise DeviceClientError(u"Failed to execute remote command '{}'\n{}".format(command, response))

            return response
        except (zmq.Again, zmq.ZMQError) as e:
            self.handle_response_error(u"Command error: {}".format(e))
            return False

    def method(self, method, attributes=None):
        """
        Execute devices method with associated attributes.
        :param method: string
        :param attributes: json formatted string
        :return:
        """
        if not self.connected or self.closing:
            raise DeviceClientError(
                u"Method {} remote execution failed. Client is not connected".format(method))

        try:
            dumped_attributes = json.dumps(attributes, ensure_ascii=True, cls=JsonKamzikEncoder)
            with self.client_comm_lock:
                self.socket.send(SEP.join((self.device_id, METHOD, str(method), dumped_attributes)).encode())
                status, token, response = self.handle_server_response()
            if status == RESPONSE_OK:
                return json.loads(response)
            else:
                raise DeviceClientError(u"Failed to execute remote method '{}'\n{}".format(method, response))

        except (zmq.Again, zmq.ZMQError) as e:
            self.handle_response_error(u"Method error: {}".format(e))
            return False

    def handle_server_response(self):
        '''
        This is crucial moment here.
        If server takes more then RCVTIMEO time, then we get zmq error.
        In that case modify server response time or increase RCVTIMEO time.
        '''
        response = self.socket.recv().decode()
        status, token, response = response.split(SEP)
        return status, token, response

    def handle_configuration(self):
        start_at = time.time()
        self._config_attributes()
        self._config_commands()
        self.set_status(self.initial_status)
        self.logger.info(u"Device configuration took {} sec.".format(time.time() - start_at))

    def handle_closing_subscriber(self):
        if self.subscriber_socket:
            self.subscriber_socket.close()
        if self.logger is not None:
            self.logger.info(u"Client closed")
        if not self.removing:
            self.set_status(STATUS_DISCONNECTED)
            self.closing = False
            self.connected = False

            if self.response_error or self.connection_error:
                self.reconnect()

    def handle_response_error(self, message=None):
        self.logger.error(message)
        self.response_error = True
        self.close()

    def handle_connection_error(self, message=None):
        self.logger.error(message)
        self.connection_error = True
        self.disconnect()

    def handle_command_error(self, readout_command, readout_output):
        self.logger.error(
            u"Command error\nCommand: {}\nOutput: {}".format(readout_command, readout_output))

    def disconnect(self):
        if self.connecting:
            # Device is connecting, but here we want to disconnect it.
            # To prevent automatic reconnection, just remove it from connecting devices.
            self.device_poller.remove_connecting_device(self)
        else:
            # Device is fully connected and it's not in connecting loop
            # Therefor we can safely close it
            self.close()

    def close(self):
        self.logger.info(u"Closing client")
        self.closing = True
        self.connected = False
        self.set_status(STATUS_DISCONNECTING)
        if self.socket:
            self.socket.close()
        self.stopped.set()
        # Here we doing nothing more
        # After stopped flag is set handle_closing_subscriber is fired and finish
        # client closing procedure

    def remove(self):
        self.removing = True
        Device.remove(self)
