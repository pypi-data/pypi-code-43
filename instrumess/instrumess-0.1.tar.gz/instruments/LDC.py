# -*- coding: utf-8 -*-
"""
Created on Thu Jul  19 2018
 
@author: Rastko Pajković
"""
 
# driver for pro800
import visa
import re
import time
# import matplotlib.pyplot as plt
import numpy as np

from plot_aux import fig_new
 
address = "GPIB0::18::INSTR"
 
# rm = visa.ResourceManager()
  

class Ldc():
    """PRO8000 Laser Diode Controller driver"""

    def __init__(self, address="GPIB0::18::INSTR", online=True):
        """Initialize the instrument"""
        self.address = address
        self.online = online
     
    def __enter__(self):
        rm = visa.ResourceManager()
        self.instr = rm.open_resource(self.address)
        return self
         
    def __exit__(self, exception_type, exception_value, traceback):
        # self.instr.write("GTL")    # go to local, doesn't work
        # self.output(state='OFF')
        self.instr.control_ren(0)  # go to local, works
        self.instr.close()
     
    def set_current_mA(self, i):
        self.instr.write(':ILD:SET {:E}'.format(i/1000))  # mA
        print('Actual current = {:.2f} mA'.format(self.meas_current_mA()))

    def meas_current_mA(self):
        i_raw = self.instr.query(':ILD:ACT?')
        return self._parse_first_float(i_raw)*1000  # mA

    def get_current_mA(self):
        i_raw = self.instr.query(':ILD:SET?')
        return self._parse_first_float(i_raw)*1000  # mA

    def meas_mean_current_mA(self, avg=5):
        return np.mean([self.meas_current_mA() for _ in range(avg)])

    def output(self, state='off'):
        if state.lower() in ['on', 'off']:
            self.instr.write(':LASER {}'.format(state.upper()))
        if state.lower() == '?':
            state_raw =  self.instr.query(':LASER?')
            if 'ON' in state_raw:
                return 'on'
            elif 'OFF' in state_raw:
                return 'off'

    def slow_start_mA(self, i=120, step=5, wait=0.1):
        currents = np.arange(0,i+0.01,step)
        self.set_current_mA(0)
        self.output('on')
        for c in currents:
            self.set_current_mA(c)
            time.sleep(wait)

    def slow_stop(self, step=5, wait=0.1):
        currents = np.arange(0,self.get_current_mA(),step)[::-1]
        for c in currents:
            self.set_current_mA(c)
            time.sleep(wait)
        self.output('off')

    def _parse_first_float(self, string):
        """Parse first float in a string"""
        re_float = r"[-+]?(?:\d+(?:\.\d*)?|\.\d+)(?:[eE][-+]?\d+)?"
        float_string = re.findall(re_float, string)[0]
        return float(float_string)

if __name__ == '__main__':
    with Ldc() as ldc:
        ldc.set_current_mA(20)
        ldc.output(state='on')
        i = ldc.meas_current_mA()
