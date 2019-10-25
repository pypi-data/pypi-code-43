import asynchat
import asyncore
import copy
import logging
import socket
import time
from collections import OrderedDict
from threading import Thread, Event, Lock

from kamzik3 import DeviceClientError
from kamzik3.constants import *


class PortReadLoop(Thread):

    def __init__(self):
        super(PortReadLoop, self).__init__()
        self.map = []
        self.stopped = Event()

    def add_device(self, device):
        if device not in self.map:
            self.map.append(device)
            return True
        else:
            return False

    def remove_device(self, device):
        if device in self.map:
            self.map.remove(device)
            return True
        else:
            return False

    def run(self):
        while not self.stopped.wait(0.01):
            for device in self.map:
                try:
                    device.handle_read()
                except IOError:
                    device.handle_response_error(u"Port read error")

    def stop(self):
        self.stopped.set()


class DevicePoller(Thread):
    min_poll = 10  # Minimum polling interval default is 10 ms

    def __init__(self):
        super(DevicePoller, self).__init__()
        self.stopped = Event()
        self.lock = Lock()
        self.connect_lock = Lock()
        self.connecting_devices = []
        self.commands_buffer = {}
        self.logger = logging.getLogger(u"Console.DevicePoller")
        self.polling_schedule = OrderedDict()
        self.schedule = []

    def run(self):
        self.logger.info(u"Starting devices poller Thread")
        schedule_at = self.min_poll
        check_connection_at = 1000
        min_poll_tick = self.min_poll * 1e-3

        while not self.stopped.wait(timeout=min_poll_tick):
            if check_connection_at <= 0:
                for device in self.commands_buffer.keys():
                    device.is_alive()

            with self.lock:
                for pollAt in self.schedule:
                    if pollAt > schedule_at:
                        break
                    elif schedule_at % pollAt == 0:
                        for device, attributes in self.polling_schedule[pollAt].items():
                            if device.accepting_commands():
                                self.commands_buffer[device] += attributes
                for device, commands in copy.copy(self.commands_buffer).items():
                    if commands and device.accepting_commands():
                        self.commands_buffer[device] = device.send_command(commands)
                        device.set_value(ATTR_BUFFERED_COMMANDS, len(self.commands_buffer[device]))

            # Check connection only @ 1Hz
            if check_connection_at <= 0:
                self.check_devices_connection_timeout()
                check_connection_at = 1000
            else:
                check_connection_at -= self.min_poll

            if not self.schedule or schedule_at >= self.schedule[-1]:
                schedule_at = self.min_poll
            else:
                schedule_at += self.min_poll

    def stop(self):
        self.logger.info(u"Stopping devices poller Thread")
        self.stopped.set()

    def add(self, device, attribute, poll_at, callback=None, returning=True, force_add=False):
        with self.lock:
            if poll_at not in self.polling_schedule:
                self.polling_schedule[poll_at] = OrderedDict()
            if device not in self.polling_schedule[poll_at]:
                self.polling_schedule[poll_at][device] = []
            if device not in self.commands_buffer:
                self.commands_buffer[device] = []

            polling_quadruplet = (attribute, None, callback, returning)
            if force_add or polling_quadruplet not in self.polling_schedule[poll_at][device]:
                self.polling_schedule[poll_at][device].append(polling_quadruplet)

            self.schedule = sorted(self.polling_schedule.keys())

    def remove(self, device, attribute, poll_at, callback=None, returning=True):
        with self.lock:
            try:
                self.polling_schedule[poll_at][device].remove((attribute, None, callback, returning))
                if len(self.polling_schedule[poll_at][device]) == 0:
                    del self.polling_schedule[poll_at][device]
                if len(self.polling_schedule[poll_at]) == 0:
                    del self.polling_schedule[poll_at]

                self.schedule = sorted(self.polling_schedule.keys())
            except (ValueError, KeyError):
                pass

    def stop_polling(self, device):
        with self.lock:
            for polledDevices in self.polling_schedule.values():
                try:
                    if device in polledDevices:
                        del polledDevices[device]
                        self.commands_buffer[device] = []
                except (ValueError, KeyError):
                    pass  # device is no longer within polled devices

    def prepare_command(self, device, command):
        with self.lock:
            self.commands_buffer[device].append(command)

    def prepend_command(self, device, command):
        with self.lock:
            self.commands_buffer[device].insert(0, command)

    def add_connecting_device(self, device):
        with self.lock:
            self.commands_buffer[device] = []
            if device not in self.connecting_devices:
                self.connecting_devices.append(device)

    def remove_connecting_device(self, device):
        with self.lock:
            try:
                self.connecting_devices.remove(device)
            except ValueError:
                pass  # device is no longer within connecting devices

    def check_devices_connection_timeout(self):
        for device in self.connecting_devices[:]:
            if device.connecting_time >= device.connection_timeout:
                self.remove_connecting_device(device)
                device.handle_connection_error(u"Connection timeout")
            elif device.connected or (not device.connecting and not device.closing):
                self.remove_connecting_device(device)
            else:
                device.connecting_time += 1000


class DeviceClientPoller(Thread):
    poll_tick = 2000

    def __init__(self):
        super(DeviceClientPoller, self).__init__()
        self.stopped = Event()
        self.connect_lock = Lock()
        self.commands_buffer = {}
        self.connecting_devices = []
        self.logger = logging.getLogger(u"Console.DeviceClientPoller")

    def run(self):
        self.logger.info(u"Starting devices client poller Thread")
        while not self.stopped.wait(self.poll_tick * 1e-3):
            self.check_devices_connection_timeout()

    def stop(self):
        self.stopped.set()

    def check_devices_connection_timeout(self):
        """
        Check if ZMQ client can communicate with opened port.
        The is that we can connect to the port even if that one is not connected
        on serve side. To check if socket is available we simply try to
        send poll command. If we can get answer proceed with init routine.
        If not, then try it reconnect and try it again.
        :return: None
        """
        for device in self.connecting_devices[:]:
            if self.stopped.is_set():
                break
            if device.poll():
                try:
                    device.handle_connect_event()
                    self.remove_connecting_device(device)
                except DeviceClientError:
                    device.handle_response_error(u"Client initialization failed")
            else:
                if device in self.connecting_devices:
                    device.reconnect()

    def add_connecting_device(self, device):
        with self.connect_lock:
            if device not in self.connecting_devices:
                self.connecting_devices.append(device)

    def remove_connecting_device(self, device):
        with self.connect_lock:
            if device in self.connecting_devices:
                self.connecting_devices.remove(device)


class DeviceAsyncoreLoop(Thread):
    dummy_device = None

    def __init__(self):
        super(DeviceAsyncoreLoop, self).__init__()
        self.dummy_device = asynchat.async_chat()
        self.dummy_device.create_socket(socket.AF_INET, socket.SOCK_STREAM)
        self.dummy_device.socket.setblocking(False)
        self.setDaemon(True)

    def run(self):
        asyncore.loop(use_poll=True, timeout=0.1)

    def stop(self):
        if self.is_alive():
            self.dummy_device.close()

        asyncore.close_all()


control_asyncore_loop = DeviceAsyncoreLoop()
control_device_poller = DevicePoller()
control_port_read_loop = PortReadLoop()
control_device_client_poller = DeviceClientPoller()
