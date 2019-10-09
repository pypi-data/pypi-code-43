# -*- coding: utf-8 -*-
"""
Created on Monday 06-August-2018 at 14:58

@author: Rastko Pajković
"""

from instrument_v3 import Instrument
import numpy as np
import matplotlib.pyplot as plt
import utilities as ut
from plot_aux import fig_new  # , save_last_fig, fig_label, interactive_legend,\

plt.rcParams.update({'font.size': 14})  # set default font size for all plots


class Keithley2400(Instrument):
    """Driver for Keithley 2400

    Remarks:
    --------
    If your commands aren't registered wait between commands for ex. 0.1s
    """

    commands = {
        'output': ':OUTP {}',  # 'ON' or 'OFF'
        'read'  : ':READ?',  # read a data string (v,i,r,), 1e37 is not measured
        'source': ':SOUR:FUNC {}',  # takes 'CURR', 'VOLT'
        'set_v' : ':SOUR:VOLT:LEV {}',
        'set_i' : ':SOUR:CURR:LEV {}',
        'get_i' : ':SOUR:CURR:LEV?',  # get the set value of current
        'sense' : ':SENS:FUNC:ON {}',  # '"RES", "CURR", "VOLT"' with ""!
        'all_m' : ':SENS:FUNC:{}:ALL',  # turn all meas func 'ON' or 'OFF'
        'lim_i' : ':SENS:CURR:PROT {}',  # complience current in A
        'lim_v' : ':SENS:VOLT:PROT {}',  # complience voltage in V
        'nplc'  : ':VOLT:NPLC {}',  # 0.01..10 integration time in number of
                                    # power line cycles 10 = 10*1/50 = 1/5 s
                                    # global setting, affects all measurements

               }
    com = ut.Dotdict(commands)

    def __init__(self, address='GPIB0::24::INSTR'):
        """Oneline docString"""
        super(Keithley2400, self).__init__(address=address)

    def __enter__(self):
        self.instr = self._rm.open_resource(self._address)
        # self.reset()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        ut.wait_s(0.2)
        # self.output = 'off'
        ut.wait_s(0.2)
        self.instr.control_ren(0)  # go to local
        self.instr.close()         # close visa connection
    
    def reset(self):
        """One-line docString"""
        self.write('*RST')  # restart the device settings
    
    # --- define instrument properties -----------------------------------------
    output = Instrument.prop(com.output, "Set output 'ON' or 'OFF'",
                             in_set=['ON', 'OFF'], name='output')
    source = Instrument.prop(com.source,
                             "Set source function to 'current' or 'voltage'",
                             in_set={'current': 'CURR',
                                     'voltage': 'VOLT',
                                     },
                             name='Source')
    sense = Instrument.prop(com.sense,
                            """Set sens (measure) funstion to 'current',
                            'voltage' or 'resistance'""",
                            in_set={'current': '"CURR"',
                                    'voltage': '"VOLT"',
                                    'resistance': '"RES"'
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

    def source_voltage(self, lim_i_mA=None, sense='current', nplc=4):
        """Set the behavior of the SMU to source Voltage"""
        self.source = 'voltage'
        ut.wait_s(0.2)
        if lim_i_mA is not None:
            self.lim_i = lim_i_mA/1e3
            ut.wait_s(0.2)
        self.sense = sense
        ut.wait_s(0.2)
        self.nplc = nplc
        ut.wait_s(0.2)
        self.output = 'on'

    def source_current(self, lim_V=None, sense='voltage', nplc=4):
        """Set the behavior of the SMU to source Current"""
        self.source = 'current'
        ut.wait_s(0.2)
        if lim_V is not None:
            self.lim_v = lim_V
            ut.wait_s(0.2)
        self.sense = sense
        ut.wait_s(0.2)
        self.output = 'on'

    def set_voltage(self, V=0):
        """Set voltage"""
        self.write(self.com.set_v.format(V))

    def set_current(self, i_ma=0, slow_start=True, wait=0.1, step=2):
        """Set current in mA"""
        if slow_start:
            start=self.get_current()
            currents = ut.array(start=start, step=step, stop=i_ma)
            for i in currents:
                self.write(self.com.set_i.format(i/1e3))
                ut.wait_s(wait)
                self.measure()
        self.write(self.com.set_i.format(i_ma/1e3))
        self.measure()

    def get_current(self):
        """Get the value of current in mA that is set, does not measure"""
        raw = self.query(self.com.get_i)
        return ut.parse_floats(raw, iterable=False)*1e3  # converts A to mA

    def measure(self):
        """Read measurements, parse and return
        
        Returns
        -------
        3x float
            Returns measured voltage [V], current [mA] and resistance [Ohm]
        """
        res_raw = self.query(self.com.read)
        res = ut.parse_floats(res_raw)
        v, i, r = res[0], res[1]*1e3, res[2]
        return v, i, r


def setup(source=None, measure=None, lim_i_mA=None, lim_v=None, nplc=None):
    """Setup basic functionality"""
    with Keithley2400(address='GPIB0::24::INSTR') as k:
        if source is not None:
            k.source = source
            ut.wait_s(0.1)
        if measure is not None:
            k.measure = measure
            ut.wait_s(0.1)
        if lim_i_mA is not None:
            k.lim_i = lim_i_mA/1e3
            ut.wait_s(0.1)
        if lim_v is not None:
            k.lim_v = lim_v
            ut.wait_s(0.1)
        if nplc is not None:
            k.nplc = nplc
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
