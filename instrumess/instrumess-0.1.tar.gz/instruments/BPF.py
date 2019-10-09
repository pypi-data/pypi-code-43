# -*- coding: utf-8 -*-
"""
Created on Tuesday 19-February-2019 at 19:52

@author: Rastko Pajković
"""

from instrument_v31 import Instrument
import utilities as ut


class BPFTB9(Instrument):
    """Driver for JDS Uniphase TB9 Optical Grating Filter"""

    commands = {
        'wavelength': 'wvl {:.2f}nm'
    }
    com = ut.Dotdict(commands)  # this makes dictionary keys easier to access

    # ----- Instrument properties ---------------------------------------------
    wl = Instrument.prop(com.wavelength, docs="Set wavelength in nm",
                         in_range=(1460, 1575), in_set=None, name='Value')
    # -------------------------------------------------------------------------

    def reset(self):
        """Return the instrument to the default setting"""
        pass

    def setup(self, wl_nm=None):
        """Set the band pass wavelength in nm"""
        if wl_nm is not None:
            self.wl = wl_nm


if __name__ == '__main__':
    with BPF(address='GPIB::3::INSTR') as bpf:
        bpf.setup(wl_nm=1523)
