# -*- coding: utf-8 -*-
"""
Created on Tuesday 24-July-2018 at 17:16

@author: Rastko Pajković
"""

# from pathlib import Path
import visa
import utilities as ut
import pandas as pd
import utilities as ut


class Wavemeter():
    """Ando AQ6141 Wavelength meter driver class"""

    def __init__(self, address="GPIB0::8::INSTR", online=True):
        """Initialize the instance by setting address and online state"""
        self.address = address
        self.online = online

    def __enter__(self):
        rm = visa.ResourceManager()
        self.instr = rm.open_resource(self.address)
        self.reset()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        ut.wait_s(0.2)
        self.instr.control_ren(0)  # go to local, works
        self.instr.close()

    def sweep(self):
        """Perform a new sweep, return nothing"""
        self.instr.write('*TRG')

    def get_peaks_df(self, sweep_first=True):
        """Return a list of peaks as a DataFrame with columns wl p and ts"""
        if sweep_first:
            self.sweep()
        wl_raw = self.instr.query(':CALC2:DATA? Wav')
        p_raw = self.instr.query(':CALC2:DATA? POW')
        ts = ut.get_time()
        wl, p = [ut.parse_floats(el) for el in [wl_raw, p_raw]]
        res = pd.DataFrame(data={'wl': wl,
                                 'p': p,
                                 'ts':[ts]}
                           )
        return res.sort_values('p', ascending=False)

    def get_peaks(self, sweep_first=True):
        """Returns first two peak information: wl1, p, wl2, smsr"""
        if sweep_first:
            self.sweep()
        wl_raw = self.instr.query(':CALC2:DATA? Wav')
        p_raw = self.instr.query(':CALC2:DATA? POW')
        wl, p = [ut.parse_floats(el, iterable=True) for el in [wl_raw, p_raw]]
        if len(wl)==0:
            wl1, p, wl2, smsr = [None]*4
        elif len(wl)==1:
            wl1, p = wl[0], p[0]
            wl2, smsr = [None]*2
        else:
            wl1, p, wl2, smsr = wl[0], p[0], wl[1], p[0]-p[1]
        return wl1, p, wl2, smsr

    def reset(self):
        """Reset the instrument to a known state"""
        self.instr.read_terminantion = '\r\n'
        self.instr.timeout = 5000
        self.instr.write(':UNIT DBM')
        self.instr.write(':UNIT:WL:WAV')
        self.instr.write(':CALC2:WLIM:STAR 1500e-9')
        self.instr.write(':CALC2:WLIM:STOP 1560e-9')
        self.instr.write(':CALC2:VERT:REF:DBM -10')
        self.instr.write(':CALC2:VERT:SCALE 10')

# testing
if __name__ == '__main__':
    with Wavemeter(address="GPIB0::8::INSTR") as wm:
        wm.sweep()
        # res = wm.get_peaks()
        peaks = []
        iterations = 10
        for i in range(iterations):
            peaks.append(wm.get_peaks_df())
