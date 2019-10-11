from ctypes import CDLL

# from msl.loadlib import LoadLibrary, Server32
from kamzik3.devices.attribute import Attribute
from kamzik3.constants import *
from kamzik3 import DeviceError
from kamzik3.devices.device import Device

# class MyServer(Server32):
#     """A wrapper around a 32-bit C++ library, 'cpp_lib32.dll', that has an 'add' function."""
#
#     def __init__(self, host, port, quiet, **kwargs):
#         # Load the 'cpp_lib32' shared-library file using ctypes.CDLL.
#         super(MyServer, self).__init__('cpp_lib32.dll', 'cdll', host, port, quiet)
#
#     def add(self, a, b):
#         # The Server32 class has a 'lib' property that is a reference to the ctypes.CDLL object.
#         # The shared library’s 'add' function takes two integers as inputs and returns the sum.
#         return self.lib.add(a, b)

class DeviceOsLibrary(Device):

    def __init__(self, os_library, device_id=None, config=None):
        self.os_library = os_library
        self.lib = None
        super().__init__(device_id, config)
        self.connect()

    def connect(self, *args):
        """
        Call only this function to connect devices to port / socket / library / ...
        :param args: connect attributes
        """
        self.connecting = True
        self.handle_configuration_event()
        try:
            self.lib = CDLL(self.os_library)
            # self.lib = LoadLibrary(self.os_library)
        except OSError as e:
            raise DeviceError("Error loading library {}. {}".format(self.os_library, e))
        self.connected = True
        self.connecting = False
        self.set_status(STATUS_IDLE)

    def _init_attributes(self):
        Device._init_attributes(self)
        self.attributes.update({
            ATTR_LIBRARY: Attribute(self.os_library, readonly=True),
        })
    