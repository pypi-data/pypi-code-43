# -*- coding: utf-8 -*-
"""
Created on Fri May 10 11:34:09 2019

@author: 20185069
"""
from instrument_v5 import Instrument
import numpy as np
import matplotlib.pyplot as plt
import utilities as ut
from plot_aux import fig_new
import validate


class Keithley2602B(Instrument):
    """Driver for Keithley 2400

    Remarks:
    --------
    If your commands aren't registered wait between commands for ex. 0.1s
    """
# 'output': 'sour{}:pow:stat {}; *OPC?',
#        'p_dBm' : 'sour{}:pow {}dbm; *OPC?',
#        'wl_nm' : 'sour{}:wav {}nm; *OPC?',
#        'reset' : '*RST',
    commands = {
        'source' : 'smu{}.source.func = smu{}.{}',
        'measure': 'print(smu{}.measure.{}())',
        'sense'  : 'display.smu{}.measure.func = display.{}',
        'output' : 'smu{}.source.output = smu{}.{}',
        'set_v'  : 'smu{}.source.levelv = {}',
        'set_i'  : 'smu{}.source.leveli = {}',
        'lim_i'  : 'smu{}.source.limiti = {}',  # complience current in A
        'lim_v'  : 'smu{}.source.limitv = {}',  # complience voltage in V
        'nplc'   : 'smu{}.measure.nplc = {}',   # 0.01..10 integration time in number of
                                                # power line cycles 10 = 10*1/50 = 1/5 s
                                                # global setting, affects all measurements
        'get_i' :  'print(smu{}.measure.i())',  # get the set value of current

               }
    com = ut.Dotdict(commands)

    # --- define instrument properties -----------------------------------------
    output = Instrument.prop(com.output, "Set output 'ON' or 'OFF'",
                             in_set={'ON': 'OUTPUT_ON',
                                     'OFF': 'OUTPUT_OFF',
                                     },
                             name='output')
    source = Instrument.prop(com.source,
                             "Set source function to 'current' or 'voltage'",
                             in_set={'current': 'OUTPUT_DCAMPS',
                                     'voltage': 'OUTPUT_DCVOLTS',
                                     },
                             name='Source')
    sense = Instrument.prop(com.sense,
                            """Set sens (measure) funstion to 'current',
                            'voltage' or 'resistance'""",
                            in_set={'current': 'MEASURE_DCAMPS',
                                    'voltage': 'MEASURE_DCVOLTS',
#                                    'resistance': 'MEASURE_DCAMPS'
                                    },
                            name='Sense (measure)')
    lim_i = Instrument.prop(com.lim_i,
                            """Complience current in A""",
                            in_range=(-3.15, 3.15),
                            name='Current limit [A]')
    lim_v = Instrument.prop(com.lim_v,
                            """Complience voltage in V""",
                            in_range=(-105, 105),
                            name='Voltage limit [V]')
    nplc = Instrument.prop(com.nplc,
                           """Set the integration time as multiple of 1/50s""",
                           in_range=(0.01, 10),
                           name='Number of power line cycles (t_int)')
    # --------------------------------------------------------------------------
    def __init__(self, address='GPIB0::24::INSTR', channel='a'):
        """Oneline docString"""
        channel = validate.in_set(channel, ['a', 'b'], 'channel')
        self._channel = channel
        super(Keithley2602B, self).__init__(address=address)

    def __enter__(self):
        self.instr = self._rm.open_resource(self._address)
        self.reset()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        ut.wait_s(0.2)
        self.output = self._channel, self._channel, 'OFF'
        ut.wait_s(0.2)
        self.instr.control_ren(0)  # go to local
        self.instr.close()         # close visa connection
    
    def reset(self):
        """One-line docString"""
        self.write('*RST')  # restart the device settings

    def source_voltage(self, lim_i_mA=None, sense='current', nplc=4):
        """Set the behavior of the SMU to source Voltage"""
        self.source = self._channel,self._channel, 'voltage'
        ut.wait_s(0.2)
        if lim_i_mA is not None:
            self.lim_i = self._channel, lim_i_mA/1e3
            ut.wait_s(0.2)
        self.sense = self._channel, sense
        ut.wait_s(0.2)
        self.nplc = self._channel, nplc
        ut.wait_s(0.2)
        self.output = self._channel, self._channel, 'on'

    def source_current(self, lim_V=None, sense='voltage', nplc=4):
        """Set the behavior of the SMU to source Current"""
        self.source = self._channel,self._channel, 'current'
        ut.wait_s(0.2)
        if lim_V is not None:
            self.lim_v = self._channel, lim_V
            ut.wait_s(0.2)
        self.sense = self._channel, sense
        ut.wait_s(0.2)
        self.output = self._channel, self._channel, 'ON'

    def set_voltage(self, V=0):
        """Set voltage"""
        self.write(self.com.set_v.format(self._channel, V))

    def get_current(self):
        """Measure and return the current value in mA"""
        answer = self.query(self.com.get_i.format(self._channel))
        current_ma = ut.parse_floats(answer)*1e3
        return current_ma

    def set_current(self, i_ma=0, slow_start=True, wait=0.1, step=2):
        """Set current in mA"""
        if slow_start:
            start=self.get_current()
            currents = ut.array(start=start, step=step, stop=i_ma)
            for i in currents:
                self.write(self.com.set_i.format(self._channel, i/1e3))
                ut.wait_s(wait)
                self.measure()
        self.write(self.com.set_i.format(self._channel, i_ma/1e3))
        self.measure()


    def measure(self, prop='i'):
        """Read measurement, i, v, r or p, parse and return
        
        Returns
        -------
        float
            Returns measured voltage [V], current [mA], resistance [Ohm], or Power [W]
        """
        res_raw = self.query(self.com.measure.format(self._channel, prop))
        res = ut.parse_floats(res_raw)
        if prop=='i':
            res=res*1e3
        return res


    def setup(self, source=None, measure=None, lim_i_mA=None, lim_v=None, nplc=None):
        """Setup basic functionality"""
        if source is not None:
            self.source = self._channel,self._channel, source
            ut.wait_s(0.1)
        if measure is not None:
            self.measure = self._channel, measure
            ut.wait_s(0.1)
        if lim_i_mA is not None:
            self.lim_i = self._channel, lim_i_mA/1e3
            ut.wait_s(0.1)
        if lim_v is not None:
            self.lim_v = self._channel, lim_v
            ut.wait_s(0.1)
        if nplc is not None:
            self.nplc = self._channel, nplc
            ut.wait_s(0.1)

# testing
# if __name__ == "__main__":
#     voltage = -np.arange(0,4.01,0.1)
#     # voltage = [1]*20
#     a = Keithley2400()
#     with a:
#         a.source_voltage(lim_i_mA=-0.1, sense='current')
#         current = []

#         for v in voltage:
#             ut.wait_s(0.1)
#             a.set_voltage(v)
#             ut.wait_s(0.1)
#             _, i, _ = a.measure()
#             current.append(i)
#         ut.wait_s(0.1)
    
#     fig, ax = fig_new(name='IV characteristic of a 100kOhm resistor')
#     ax.plot(voltage, current)
#     ax.set(
#         xlabel='V',
#         ylabel='mA',
#     )
#     fig.tight_layout()
                            
#     # with a:
#     #     a.source_voltage(lim_i_mA=20, sense='resistance')
#     #     a.output = 'on'
#     #     a.set_voltage(1)
#     #     ut.wait_s(0.2)
#     #     print(a.query(a.com.read))
#     #     ut.wait_s(2)
#     #     a.output = 'off'
