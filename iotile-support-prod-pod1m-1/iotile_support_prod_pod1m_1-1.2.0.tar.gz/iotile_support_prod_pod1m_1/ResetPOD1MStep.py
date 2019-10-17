from __future__ import (unicode_literals, print_function, absolute_import)
from builtins import str
from iotile.core.hw.hwmanager import HardwareManager
from iotile.core.exceptions import ArgumentError

class ResetPOD1MStep(object):
    """A Recipe Step used to clean all readings and nodes
    """
    REQUIRED_RESOURCES = [('connection', 'hardware_manager')]

    def __init__(self, args):
        pass

    def run(self, resources):
        hw = resources['connection'].hwman
        sg = hw.controller().sensor_graph()
        sg.clear()

        if sg.count_readings()['storage'] != 0:
            raise ArgumentError('Data on controller tile failed to clear.')
        
        accel = hw.get(12)
        sm = accel.setup_manager()
        sm.admin_reset()

        if accel.count_shocks() != 0:
            raise ArgumentError('Waveforms on accel tile failed to clear.')
