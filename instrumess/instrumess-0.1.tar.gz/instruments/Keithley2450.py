# -*- coding: utf-8 -*-
"""
Created on Monday 06-August-2018 at 14:58

@author: Rastko Pajković
"""

from instrument_v3 import Instrument
import matplotlib.pyplot as plt
import utilities as ut

plt.rcParams.update({'font.size': 14})  # set default font size for all plots


class Keithley2450(Instrument):
    """Driver for Keithley 2450

    Remarks:
    --------
    If your commands aren't registered wait between commands for ex. 0.1s
    """

    commands = {
        'output'   : 'smu.source.output = smu.{:s}',  # 0 or 1, 1 is ON
        'measure'  : 'print(smu.measure.read())',       # read a data string (v,i,r,), 1e37 is not measured
        'source'   : 'smu.source.func = smu.{}',
        'sense'    : 'smu.measure.func = smu.{:s}',
        'set_v'    : 'smu.source.level = {:f}',
        'set_i'    : 'smu.source.level = {:f}',
        'get_i'    : 'print(smu.source.level)',
        'lim_i'    : 'smu.source.ilimit.level = {:f}',   # complience current in A
        'lim_v'    : 'smu.source.vlimit.level = {:f}',   # complience voltage in V
        'nplc'     : 'smu.measure.nplc = {:f}',  # 0.01..10 integration time in number of
                                                 # power line cycles 10 = 10*1/50 = 1/5 s
                                                 # global setting, affects all measurements
        'comm_lang': '*LANG?',
               }
    com = ut.Dotdict(commands)

    # --- define instrument properties -----------------------------------------
    output = Instrument.prop(com.output, "Set output 'ON' or 'OFF'",
                             in_set={'on' :'ON',
                                     'off':'OFF'},
                             name='output')
    source = Instrument.prop(com.source,
                             "Set source function to 'current' or 'voltage'",
                             in_set={'current': 'FUNC_DC_CURRENT',
                                     'voltage': 'FUNC_DC_VOLTAGE',
                                     },
                             name='Source')
    sense = Instrument.prop(com.sense,
                            """Set sens (measure) funstion to 'current',
                            'voltage' or 'resistance'""",
                            in_set={'current': 'FUNC_DC_CURRENT',
                                    'voltage': 'FUNC_DC_VOLTAGE',
                                    'resistance': 'FUNC_RESISTANCE',
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

    def __init__(self, address='GPIB0::24::INSTR'):
        """Oneline docString"""
        super(Keithley2450, self).__init__(address=address)

    def __enter__(self):
        self.instr = self._rm.open_resource(self._address)
        self.instr.read_termination = '\n'
        self.instr.write_termination = '\n'
        answer = self.query(self.com.comm_lang)
        if 'TSP' not in answer:
            _ = input('Set communication protocol to TSP on Keithley 2450 and press ENTER.')
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
        self.output = 'ON'

    def source_current(self, lim_V=None, sense='voltage', nplc=4):
        """Set the behavior of the SMU to source Current"""
        self.source = 'current'
        ut.wait_s(0.2)
        if lim_V is not None:
            self.lim_v = lim_V
            ut.wait_s(0.2)
        self.sense = sense
        ut.wait_s(0.2)
        self.output = 'ON'

    def set_voltage(self, V=0):
        """Set voltage"""
        self.write(self.com.set_v.format(V))

    def get_current(self):
        """Read the set current (does not measure)"""
        answer = self.query(self.com.get_i)
        return ut.parse_floats(answer)*1e3  # mA

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

    def measure(self, prop='i'):
        """Read measurement of whatever the sense function is set to"""
        res_raw = self.query(self.com.measure)
        res = ut.parse_floats(res_raw)
        if prop=='i':
            res=res*1e3
        return res
                            
    def setup(self, output=None, source=None, sense=None):
        """Set output ('on', 'off') source and sense f ('current', 'voltage')"""
        if output is not None:
            self.output = output
        if source is not None:
            self.source = source
        if sense is not None:
            self.sense = sense
