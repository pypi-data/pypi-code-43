from kamzik3.constants import *
from kamzik3.devices.device import Device
from kamzik3.devices.observer import Observer


class DeviceChannel(Device, Observer):

    def __init__(self, device, channel, device_id=None, config=None):
        self.configured = False
        self.device = device
        self.channel = channel
        super(DeviceChannel, self).__init__(device_id, config)
        self._expose_methods_to_clients()
        self.set_status(STATUS_CONNECTING)
        self.device.attach_observer(self)

    def command(self, command, callback=None, with_token=False, returning=True):
        return self.device.command(command, callback, with_token, returning)

    def subject_update(self, key, value, subject):
        if key == ATTR_STATUS:
            if value in READY_DEVICE_STATUSES:
                self.handle_configuration()
            else:
                self.stop_polling()
                self.configured = False
                self.set_status(value)

    def poll_command(self, command, interval):
        self.device.poll_command(command, interval)

    def remove_poll_command(self, command, interval):
        self.device.remove_poll_command(command, interval)

    def handle_configuration(self):
        raise NotImplementedError(u"Must be implemented in subclass")

    def disconnect(self):
        self.stop_polling()
        self.configured = False
        self.device.detach_observer(self)
        self.set_status(STATUS_DISCONNECTED)

    def reconnect(self, *args):
        self.device.attach_observer(self)
        self.handle_configuration()
