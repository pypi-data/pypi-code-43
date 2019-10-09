import nidaqmx
from time import sleep
from instrument import Instrument


system = nidaqmx.system.System.local()
#print(system.driver_version)
for device in system.devices:
    print('NI-DAQ online device: ', device)


class NiDaq_ao(Instrument):
    """Driver for NI cDAQ 16xAnalog output module"""

    def __init__(self, address='Dev1', online=True, name=None):
        """One-line docString"""
        super().__init__(address=address, online=online, name=name)
        self.voltages = None

    def __enter__(self):
        self.reset()
        self.init()

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def init(self):
        """Initialize instrument communication"""
        if super()._is_offline():
            return
        self._task = nidaqmx.Task('analog_output')

    def set_channels(self, channels_string):
        """define output channels in e.g. '0, 2, 4:8' format """
        if super()._is_offline():
            return
        self._task.ao_channels.add_ao_voltage_chan(self._address+'/ao'+channels_string)
        self._task.start()
        self.channels = self._parse_channels(channels_string)

    def _parse_channels(self, channels_string):
        channels = []
        elems = channels_string.split(',')
        for elem in elems:
            if ':' in elem:
                first, *middle, last = map(int,elem.split(':'))
                channels += list(range(first, last+1))
            else:
                channels += int(elem)
        return channels

    def set_voltages(self, voltages):
        """set voltages on the output channels """
        self.voltages = voltages
        if super()._is_offline():
            return
        self._task.write(voltages)

    def reset(self):
        """Resed the insrrument to a known state and preapre communication"""
        if super()._is_offline():
            return
        self._task.write([0]*len(self.channels))

    def close(self):
        """Close instrument communication"""
        if super()._is_offline():
            return
        self.reset()
        self._task.close()

