import pizdets.pm
import time
from .ExperimentFiles import ExperimentFiles


class Experiment(directory="NewFolder"):

    def __init__(self, directory, connect=True):
        self.files = ExperimentFiles(directory)
        self.mixer_period = 3000
        self.mixer_pulseWidth = 2500
        if connect:
            self.dev = self.reconnect()
        self._read_pump_calibration()


    def reconnect(self, device_index=0):
        # self.hub = pizdets.pm.PMHub.local()
        self.hub = pizdets.pm.PMHub("tcp://localhost:5555")

        self.dev = self.hub.get_devices()[device_index]
        return self.dev


    def _valvepwm(self, tube, pwm):
        servomap = {3: 0, 4: 1, 5: 2, 6: 3, 2: 4, 1: 5, 0: 6}
        exec("self.dev.request(pm.dev_msg.SetServoStateRequest(servo%d=%d))" % (servomap[tube], pwm))
        time.sleep(0.3)
        exec("self.dev.request(pm.dev_msg.SetServoStateRequest(servo%d=%d))" % (servomap[tube], 0))
    def _select_tube(self, tube):


    def pump_death(self, tube=5, vol=1):


    def pump_peace(self, tube=5, vol=1):


    def vacuum(self, tube=5, vol=1):



    def mix(self, state=1):
        self.dev.request(pm.dev_msg.SetMixerStateRequest(state=state,
                                                         period=self.mixer_period,
                                                         pulseWidth=self.mixer_pulseWidth))

    def get_laser_signal(self, tube,
                         resistor1=100,
                         resistor2=10,
                         laserOnDelay=10,
                         laserOffDelay=1,
                         cycles=10,
                         bias=0):
        tube_mapping = dict(zip(range(7),
                                [0,3,1,5,2,6,4]))
        tube = tube_mapping[tube]
        raw_laser_signal = self.dev.request(pm.dev_msg.ODMeasureRequest(tube=tube,
                                                                        laserOnDelay=laserOnDelay,
                                                                        laserOffDelay=laserOffDelay,
                                                                        cycles=cycles,
                                                                        bias=bias,
                                                                        resistor1=resistor1,
                                                                        resistor2=resistor2))

        return raw_laser_signal

    def record(self, **kwargs):
        return row


    def open_valves(self):
        for t in range(7):
            self.clamp(t, 1)
            time.sleep(0.2)

    def close_valves(self):
        for t in range(7):
            self.clamp(t, 0)
            time.sleep(0.2)