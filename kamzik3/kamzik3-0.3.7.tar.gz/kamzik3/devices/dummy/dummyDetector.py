import time
from threading import Event, Thread

import numpy as np

from kamzik3 import DeviceError
from kamzik3.constants import *
from kamzik3.devices.attribute import Attribute
from kamzik3.devices.device import Device
from kamzik3.snippets.snippetsDecorators import expose_method
from kamzik3.snippets.snippetsUnits import device_units

ATTR_ACQUIRED_FRAMES = "Acquired frames"
ATTR_FRAME_NAME = u"Frame name"
ATTR_FRAME_FILE = u"Frame file"


class DummyDetector(Device):

    def __init__(self, device_id=None, config=None):
        self.acquisition_running = Event()
        Device.__init__(self, device_id, config)
        self._expose_methods_to_clients()
        self.connect()

    def _init_attributes(self):
        Device._init_attributes(self)
        self.attributes.update({
            ATTR_EXPOSURE_TIME: Attribute(0, readonly=False, default_type=np.float, unit="ms", min_value=1),
            ATTR_FRAME_IMAGE: Attribute(0, readonly=True, default_type=np.uint64),
            ATTR_FRAME_NAME: Attribute("Frame", readonly=False),
            ATTR_FRAME_FILE: Attribute(0, readonly=True),
            ATTR_SUMMED_FRAMES: Attribute(0, readonly=False, default_type=np.uint64, min_value=1),
            ATTR_ACQUIRED_FRAMES: Attribute(0, readonly=True, default_type=np.uint64),
        })

    def connect(self, *args):
        """
        Call only this function to connect devices to port / socket / library / ...
        :param args: connect attributes
        """
        self.connecting = True
        self.handle_configuration_event()
        self.connected = True
        self.connecting = False
        self.set_status(STATUS_IDLE)

    def handle_configuration(self):
        start_at = time.time()
        self.set_status(STATUS_CONFIGURED)
        self.logger.info(u"Device configuration took {} sec.".format(time.time() - start_at))

    @expose_method()
    def stop(self):
        self.acquisition_running.clear()

    @expose_method({"Name": ATTR_FRAME_NAME, "Frames": ATTR_SUMMED_FRAMES, "Exposure": ATTR_EXPOSURE_TIME})
    def start_acquisition(self, Name, Frames, Exposure):
        if self.acquisition_running.isSet():
            raise DeviceError("Another acquisition is already running")
        self.acquisition_running.set()
        Frames = device_units(self, ATTR_SUMMED_FRAMES, Frames)
        Exposure = device_units(self, ATTR_EXPOSURE_TIME, Exposure)

        self.set_status(STATUS_BUSY)
        self.set_value(ATTR_FRAME_NAME, Name)
        self.set_value(ATTR_SUMMED_FRAMES, Frames)
        self.set_value(ATTR_EXPOSURE_TIME, Exposure)
        self.set_value(ATTR_ACQUIRED_FRAMES, 0)

        def _acquire():
            exposure_time_increment = 100
            current_exposure_time = 0

            while self.acquisition_running.isSet():
                time.sleep(exposure_time_increment * 1e-3)
                current_exposure_time += exposure_time_increment
                acquired_frames = int(current_exposure_time / Exposure.m)

                if acquired_frames >= Frames:
                    self.set_value(ATTR_ACQUIRED_FRAMES, Frames)
                    break
                else:
                    self.set_value(ATTR_ACQUIRED_FRAMES, acquired_frames)

            if self.connected:
                self.acquisition_running.clear()
                self.set_status(STATUS_IDLE)

        Thread(target=_acquire).start()
