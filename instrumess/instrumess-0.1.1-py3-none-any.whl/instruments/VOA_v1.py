# -*- coding: utf-8 -*-
"""
Created on Tuesday 19-February-2019 at 14:53

@author: Rastko Pajković
"""

from instrument_v31 import Instrument
import utilities as ut
import visa

class VOA(Instrument):
    """Driver for JDS Uniphase optical attenuator model HA9"""

    commands = {
        'attenuation': 'att {:.2f} db',
        'wavelength' : 'wvl {:.2f} nm',
        'block'      : 'D {:d}'
    }
    com = ut.Dotdict(commands)  # this makes dictionary keys easier to access

    # ----- Instrument properties ----------------------------------------------
    att = Instrument.prop(com.attenuation, docs="Set attenuation in dB",
                          in_range=(0,100), name='attenuation')
    wl  = Instrument.prop(com.wavelength, docs="Set wavelength in nm",
                          in_range=(1400, 1700), in_set=None, name='Value')
    block = Instrument.prop(com.block, docs="Turn the shutter on 1 or off 0",
                            in_set=(0,1), name='shutter')
    # --------------------------------------------------------------------------

    def __enter__(self):
        if super()._is_offline():
            return
        self._rm = visa.ResourceManager()
        self.instr = self._rm.open_resource(self._address)
        self.instr.write_termination = '\n'
        self.instr.read_termination = '\n'
        return self

    def reset(self):
        """Return the instrument to the default setting"""
        pass

    def setup(self, wl_nm=None, att_db=None, block=None):
        """Set the attenuation and wavlength"""
        if wl_nm is not None:
            self.wl = wl_nm
        if att_db is not None:
            self.att = att_db
        if block is not None:
            self.block = block

# test
if __name__ == '__main__':
    with VOA(address='GPIB::6::INSTR') as voa:
        voa.setup(wl_nm=1523, att_db=12.34, block=0)
