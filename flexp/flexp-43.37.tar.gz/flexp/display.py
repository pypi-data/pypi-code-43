# Display++ abstraction
from psychopy.monitors import Monitor
from psychopy.visual import Window
from psychopy.hardware.crs import DisplayPlusPlus


class dppWindow(Window):

    def __init__(self, mode="mono++", **kwargs):
        self.monitor = Monitor('Display++',
                               width=80,
                               distance=57)
        self.monitor.setSizePix((1920, 1080))

        portName = kwargs.pop('portName', '/dev/ttyACM0')
        gamma = kwargs.pop('gamma', 'hardware')

        kwargs.setdefault('screen', 1)
        kwargs['useFBO'] = True
        kwargs['size'] = (1920, 1080)
        kwargs['monitor'] = self.monitor
        super(dppWindow, self).__init__(**kwargs)

        self.dpp = DisplayPlusPlus(self,
                                   portName=portName,
                                   gamma=gamma,
                                   mode=mode,
                                   checkConfigLevel=1)

    def close(self):
        self.dpp.mode = "auto++"
        self.dpp.com.close()
        super(dppWindow, self).close()
