import json
import logging
from collections import deque
from threading import Thread, Event

import zmq

import kamzik3
from kamzik3 import SEP, CommandFormatException, DeviceServerError, DeviceError
from kamzik3.constants import *
from kamzik3.snippets.snippetDataAccess import rgetattr
from kamzik3.snippets.snippetsJson import JsonPintHook
from kamzik3.snippets.snippetsYaml import YamlSerializable


class DeviceServer(YamlSerializable):
    publisher_tick = 10  # ms
    server_thread = None

    def __init__(self, host, server_port, publisher_port):
        self.logger = logging.getLogger(u"Console.DeviceServer@{}:{}".format(host, server_port))
        self.host = host
        self.server_port = server_port
        self.publisher_port = publisher_port
        self.messages_queue = deque()
        self.devices = {}
        self.close_event = Event()
        self._init_publisher_thread()
        self._init_server_thread()
        kamzik3.session.set_device_server(self)

    def _init_server_thread(self):
        """
        Initialize connection to Device server as a client.
        Connection is done via ZMQ REP socket.
        :return: None
        """
        self.logger.info(u"Initializing server thread")
        self.server_socket = zmq.Context.instance().socket(zmq.REP)
        # Set receive timeout to 1000 ms
        self.server_socket.setsockopt(zmq.RCVTIMEO, 1000)
        # Don't let socket linger after close
        # This is VERY IMPORTANT not to set to anything but 0
        self.server_socket.setsockopt(zmq.LINGER, 0)
        self.server_socket.bind("tcp://{}:{}".format(self.host, self.server_port))
        self.server_thread = Thread(target=self._server_thread)
        self.server_thread.start()

    def _server_thread(self):
        while not self.close_event.isSet():
            try:
                data = self.server_socket.recv().decode().split(SEP)
                device_id, instruction = data[0], data[1]

                # Execute command directly on devices
                if instruction == COMMAND:
                    command, with_token = data[2], int(data[3])
                    token = self.get_device(device_id).command(command, with_token=int(with_token))
                    status, response = RESPONSE_OK, len(data[3])

                # Get devices attribute
                elif instruction == GET:
                    attribute = json.loads(data[2], object_hook=JsonPintHook)
                    response = self.get_device(device_id)._get(attribute)
                    response = json.dumps(response, ensure_ascii=True)
                    status, token = RESPONSE_OK, 0

                # Set devices attribute
                elif instruction == SET:
                    attribute, attribute_value = json.loads(data[2], object_hook=JsonPintHook)
                    set_token = self.get_device(device_id).set_attribute(attribute, attribute_value)
                    status, token, response = RESPONSE_OK, set_token, len(data[2])

                # Execute devices method with attributes
                elif instruction == METHOD:
                    method, attributes = data[2], json.loads(data[3], object_hook=JsonPintHook)
                    device = self.get_device(device_id)
                    response = rgetattr(device, method)(**attributes)
                    response = json.dumps(response, ensure_ascii=True)
                    status, token = RESPONSE_OK, 0

                # Poll devices for activity
                elif instruction == POLL:
                    status, token, response = RESPONSE_OK, 0, 1

                # Init devices
                elif instruction == INIT:
                    device = self.get_device(device_id)

                    if device is None:
                        raise DeviceServerError(
                            "Device {} is not registered on the server or publisher is not ready".format(device_id))
                    elif self.publisher_port is None:
                        raise DeviceServerError("Server publisher is not ready")
                    elif not device.in_statuses(READY_DEVICE_STATUSES):
                        raise DeviceServerError("Device is not ready")
                    else:
                        response = json.dumps(
                            (self.publisher_port, device.attributes, device.attributes_sharing_map,
                             device.exposed_methods, device.qualified_name),
                            ensure_ascii=True)
                        status, token = RESPONSE_OK, 0

                # None of above, request not implemented
                else:
                    status, token, response = RESPONSE_ERROR, 0, len(data[3])

                self.server_socket.send(SEP.join((str(status), str(token), str(response))).encode())
            except zmq.Again:
                """
                This exception is raised due mq.RCVTIMEO set to 1000ms.
                We interrupt recv loop to check if devices is still connected
                If not socket will be cleanly closed
                """
                pass
            except CommandFormatException:
                status, token, response = RESPONSE_ERROR, 0, u"Command format error"
                self.server_socket.send(SEP.join((str(status), str(token), str(response))).encode())
            except DeviceServerError:
                status, token, response = RESPONSE_ERROR, 0, u"Device server error"
                self.server_socket.send(SEP.join((str(status), str(token), str(response))).encode())
            except DeviceError as e:
                status, token, response = RESPONSE_ERROR, 0, u"Command error: {}".format(e)
                self.server_socket.send(SEP.join((str(status), str(token), str(response))).encode())
        self.handle_closing_server()

    def _init_publisher_thread(self):
        self.logger.info(u"Initializing publisher thread")
        self.publisherSocket = zmq.Context.instance().socket(zmq.PUB)
        self.publisherSocket.bind("tcp://{}:{}".format(self.host, self.publisher_port))
        Thread(target=self._publisher_thread).start()

    def _publisher_thread(self):
        while not self.close_event.wait(self.publisher_tick * 1e-3):
            while self.messages_queue:
                header, message = self.messages_queue.popleft()
                try:
                    out_message = header + SEP + json.dumps(message, ensure_ascii=True)
                    self.publisherSocket.send(out_message.encode())
                except TypeError:
                    print(message)

    def add_device(self, device):
        self.logger.info(u"Adding {} into server".format(device.device_id))
        if device.device_id not in self.devices:
            self.devices[device.device_id] = device
            device.set_device_server(self)
            return True
        else:
            return False

    def remove_device(self, device):
        self.logger.info(u"Removing {} from server".format(device.device_id))
        try:
            del self.devices[device.device_id]
            device.clear_device_server()
            return True
        except ValueError:
            return False

    def get_device(self, device_id):
        return self.devices.get(device_id, None)

    def push_message(self, device_id, message, token=None):
        try:
            if token:
                header = "{}.{}".format(device_id, token)
            else:
                header = device_id
            self.messages_queue.append((header, message))
        except TypeError:
            self.logger.exception(u"Error pushing message to client")

    def handle_closing_server(self):
        if self.server_socket:
            self.server_socket.close()

    def close(self):
        self.logger.info(u"Closing server")
        self.close_event.set()
        if self.server_thread is not None:
            self.server_thread.join(1)
