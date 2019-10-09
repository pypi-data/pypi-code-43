# -*- coding: utf-8 -*-
"""
Created on Mon Jul  9 12:05:20 2018
 
@author: 20171304
"""
 
# driver for pro800
import visa
import re
import time
from datetime import datetime
# import matplotlib.pyplot as plt
import numpy as np

from plot_aux import fig_new
from LDC import Ldc
 
address = "GPIB0::18::INSTR"
 
# rm = visa.ResourceManager()
  
# tec = rm.open_resource(address)
# print(tec.query("*IDN?"))
# print(tec.query(":SLOT?"))
# print(tec.query(":TEC?"))
# print(tec.write(":TEMP:SET 18.07"))  # works
# print(tec.query(":TEMP:SET?"))
# print(tec.write("GTL"))
# print(tec.write("LLO"))
# tec.close()
 
# write a function that:
# set tepmerature
# get temparature
# t-on/off
 

class Tec():
    """PRO8000 TEC driver"""

    def __init__(self, address="GPIB0::18::INSTR", online=True):
        """Initialize the instrument"""
        self.address = address
        self.online = online
     
    def __enter__(self):
        rm = visa.ResourceManager()
        self.instr = rm.open_resource(self.address)
        self.instr.timeout = 5000
        return self
         
    def __exit__(self, exc_type, exc_val, exc_tb):
        # self.instr.write("GTL")    # go to local, doesn't work
        # self.output(state='OFF')
        self.instr.control_ren(0)  # go to local, works
        self.instr.close()
     
    def set_pid(self, p=None, i=None, d=None, i_on=None):
        """Set PID shares in % and switch I on or off"""
        if p is not None:
            if p < 2.5:
                print('Minimal accepted value for PID is 2.5%.')
            self.instr.write(':SHAREP:SET {:.1f}'.format(p))
        if i is not None:
            if i < 2.5:
                print('Minimal accepted value for PID is 2.5%.')
            self.instr.write(':SHAREI:SET {:.1f}'.format(i))
        if d is not None:
            if d < 2.5:
                print('Minimal accepted value for PID is 2.5%.')
            self.instr.write(':SHARED:SET {:.1f}'.format(d))
        if i_on is not None:
            if i_on.lower() in ['on', 'off']:
                self.instr.write(':INTEG {:s}'.format(i_on.upper()))
        self.get_pid()

    def get_pid(self):
        commands = [':SHAREP:SET?',
                    ':SHAREI:SET?',
                    ':SHARED:SET?',
                    ':INTEG?',]
        p, i, d, ion = [self.instr.query(c) for c in commands]  # raw
        p, i ,d = [self._parse_first_float(elem) for elem in [p,i,d]]
        if 'OFF' in ion:
            i = 0
        print('P: {:5.1f}%'.format(p))
        print('I: {:5.1f}%'.format(i))
        print('D: {:5.1f}%'.format(d))
        return p, i, d

    def test_stabilization(self, duration=10, p=None, i=None, d=None,
                           i_on=None, plot_res=True):
        """Set the PID values, swing Tset from 18 to 20deg, monitor temp"""
        self.set_pid(p=p, i=i, d=d, i_on=i_on)
        t_set = self.get_temp()
        if 17.9 < t_set < 18.1:
            lvl=20
            self.set_temp(20)
        elif 19.9 < t_set < 20.1:
            lvl=18
            self.set_temp(18)
        else:
            raise ValueError('Set temperature should be 18 or 20deg, not {:.1f}'
                             .format(t_set))
        t0 = time.time()
        temp = []
        t = []
        np
        while time.time()-t0 < duration:
            temp.append(self.meas_temp())
            t.append(time.time()-t0)
        if plot_res:
            fig, ax = fig_new(name='TEC response')
            ax.axhline(lvl, c='r')
            ax.plot(t, temp)
            ax.set(
                xlabel='Time [s]',
                ylabel='Temperature [°C]',
            )
        return t, temp

    def test_distribution(self, duration=30, avg=1, nbin=60, wait_s=None, show=True):
        """Record temperature over duration seconds and plot histogram"""
        t0 = time.time()
        temp = []
        t = []
        while time.time()-t0 < duration:
            temp.append(self.meas_mean_temp(n_iter=avg))
            t.append(time.time()-t0)
            if wait_s:
                time.sleep(wait_s)
        if show:
            fig, ax = fig_new(name='Temp histogram')
            ax.hist(temp, bins=nbin)
            ax.set(
                xlabel='Temp [°C]',
                ylabel='N occurences/bin',
            )
        return t, temp

    def get_temp_sampling_f(self, duration=10, wait_s=0, show_distr=True):
        """Sample temperature and get sampling frequency"""
        t, _ = self.test_distribution(duration=duration, wait_s=wait_s, show=False)
        dt = np.diff(t)
        if show_distr:
            fig, ax = fig_new(name='Time between temp samples')
            ax.hist(dt)
            ax.set(
                xlabel='Time [s]',
                ylabel='Count in bin',
            )
            fig.tight_layout()
        return 1/np.mean(dt)

    def set_channel(self, ch=1):
        """Todo"""
        pass
     
    def get_channel(self):
        """Return active channel"""
        return self.instr.query(":SLOT?")
     
    def set_temp(self, temp):
        """Set target temperature"""
        command = ":TEMP:SET {}".format(str(temp))
        self.instr.write(command)
        return command
     
    def get_temp(self):
        """Get the set temperature value"""
        answer_raw = self.instr.query(":TEMP:SET?")
        return self._parse_first_float(answer_raw)
    
    def meas_temp(self):
        """Measure temperature"""
        answer_raw = self.instr.query(":TEMP:ACT?")
        return self._parse_first_float(answer_raw)
    
    def meas_mean_temp(self, n_iter=9):
        """Measure mean temperature over n iterations"""
        return np.mean([self.meas_temp() for _ in range(n_iter)])
    
    def output(self, state='OFF'):
        """Turn the temperature control on or off"""
        if state.lower() == 'off':
            state = state.upper()
        elif state.lower() == 'on':
            state = state.upper()
        else:
            raise ValueError("Tec.output state can only be 'ON' or 'OFF', not {}"
                             .format(state))
        self.instr.write(":TEC "+state)
                 
    def _parse_first_float(self, string):
        """Parse first float in a string"""
        re_float = r"[-+]?(?:\d+(?:\.\d*)?|\.\d+)(?:[eE][-+]?\d+)?"
        float_string = re.findall(re_float, string)[0]
        return float(float_string)
 
# tec = Tec()
# tec.__enter__()
        
# fig = plt.figure()
# ax = fig.subplots(1)
# plt.show()
# with Tec() as tec:
#    tec.set_temp(18.7)
#    tec.output('ON')
#    temp = []
#    sleep(10)
#    tec.set_temp(18.8)
#    for i in range(50):
#        temp.append(tec.meas_mean_temp())
#        ax.plot(temp)
#        sleep(0.05)
#        plt.cla()
#    tec.output('OFF')


def start(i=120):
    """Startup the TEC and LDC slowly"""
    with Tec(address="GPIB0::18::INSTR", online=True) as tec, \
         Ldc(address="GPIB0::18::INSTR", online=True) as ldc:
        tec.set_temp(18)
        tec.output(state='ON')
        time.sleep(5)
        ldc.set_current_mA(0)
        ldc.output(state='ON')
        ldc.slow_start_mA(i=i, step=5, wait=0.1)


def stop():
    """Turn the TEC output off"""
    with Tec(address="GPIB0::18::INSTR", online=True) as tec,\
         Ldc(address="GPIB0::18::INSTR", online=True) as ldc:
        ldc.slow_stop(step=5, wait=0.1)
        time.sleep(1)
        tec.output(state='OFF')
