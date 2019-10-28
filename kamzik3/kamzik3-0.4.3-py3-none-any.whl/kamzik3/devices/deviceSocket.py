import asynchat
import socket
from threading import Lock

from kamzik3.constants import *
from kamzik3.devices.device import Device
from kamzik3.snippets.snippetsControlLoops import control_asyncore_loop


class DeviceSocket(asynchat.async_chat, Device):
    terminator = b"\r\n"
    ac_in_buffer_size = 4096
    ac_out_buffer_size = 4096
    host = None
    port = None
    send_lock = Lock()

    def __init__(self, host, port, device_id=None, config=None):
        Device.__init__(self, device_id, config)
        self.asyncore_loop = control_asyncore_loop
        self.host = host
        self.port = port
        asynchat.async_chat.__init__(self)
        self.create_socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.setblocking(False)
        self.buffer = []
        self.connect((host, port))

    def initiate_send(self):
        try:
            with self.send_lock:
                asynchat.async_chat.initiate_send(self)
        except IndexError:
            # Sending queue is already empty
            # Ignore this error
            self.logger.error(u"Send buffer is already empty")
            pass

    def connect(self, address):
        try:
            asynchat.async_chat.connect(self, address)
            self.device_poller.add_connecting_device(self)
        except socket.error:
            u"""
            Socket could not be connected. Non fatal error.
            We don't want to reconnect immediately but rather wait for connection timeout.
            Set devices as connecting, add it to devicepoller and wait until connection timeout.  
            """
            self.logger.exception("Socket creation exception")
            self.connecting = True
            self.device_poller.add_connecting_device(self)
        except (OverflowError, TypeError):
            self.logger.exception("Socket creation exception")
            self.close()

    def collect_incoming_data(self, data):
        self.buffer.append(data.decode("utf-8"))

    def found_terminator(self):
        self.handle_readout(self.buffer)
        self.buffer = []

    def handle_connect(self):
        Device.handle_connect(self)

    def handle_connect_event(self):
        try:
            asynchat.async_chat.handle_connect_event(self)
            self.handle_configuration_event()
        except socket.error:
            self.logger.exception(u"Socket creation exception")
            self.close()

    def close_connection(self):
        self.stop_polling()
        return asynchat.async_chat.close_when_done(self)

    def close(self):
        asynchat.async_chat.close(self)
        self.set_status(STATUS_DISCONNECTED)
        if self.response_error or self.connection_error:
            self.reconnect()

    def handle_expt_event(self):
        self.logger.error("Socket error")
        self.connection_error = True
        asynchat.async_chat.handle_expt_event(self)

    def handle_error(self):
        self.logger.exception("Uncaught exception")
        self.handle_response_error()

    def handle_configuration(self):
        raise NotImplementedError(u"Must be implemented in subclass")
