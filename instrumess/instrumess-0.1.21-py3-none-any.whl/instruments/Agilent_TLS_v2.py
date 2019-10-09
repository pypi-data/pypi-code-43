# -*- coding: utf-8 -*-
"""
Created on Wednesday 15-August-2018 at 15:27

@author: Rastko Pajković
"""

from instrument_v4 import Instrument
import utilities as ut

# =============================================================================
#  WARNING: read the manual to know the limits of the specific equipment ! ! !
# =============================================================================


class AgilentTLS(Instrument):
    """Driver for Agilent frames TLS modules"""

    commands = {
        'output': 'sour{}:pow:stat {}; *OPC?',
        'p_dBm' : 'sour{}:pow {}dbm; *OPC?',
        'wl_nm' : 'sour{}:wav {}nm; *OPC?',
        'reset' : '*RST',
    }
    com = ut.Dotdict(commands)
    
    def __init__(self, address='GPIB::11::INSTR', slot=1,
                 online=True, name=None):
        """Generate instance of class NiDaq_ao"""
        super().__init__(address=address, online=online, name=name)
        self._slot = slot

    # ----- Instrument properties ----------------------------------------------
    on = Instrument.prop(com.output, "Set output 'ON' or 'OFF'",
                         in_set=[0, 1], name='output')
    p_dBm = Instrument.prop(com.p_dBm, docs="Set output power in dBm",
                            in_range=(-10,14),  # dBm
                            name='power')
    wl_nm = Instrument.prop(com.wl_nm, docs="Set output wavelength in m",
                            in_range=(1440,1595),
                            name='wavelength')
    # --------------------------------------------------------------------------

    def __enter__(self):
        if super()._is_offline():
            return
        self.instr = self._rm.open_resource(self._address)
        return self

    def reset(self):
        """Reset instrument to a known state and setup communication"""
        if super()._is_offline():
            return
        self.write(self.com.reset)

    def setup(self, wl_nm=None, p_dBm=None):
        """Set TLS wavelength and/or power"""
        if wl_nm is not None:
            self.wl_nm = self._slot, wl_nm  # tuple
        if p_dBm is not None:
            self.p_dBm = self._slot, p_dBm  # tuple

    def output(self, on_off='OFF'):
        """Turn TLS on or off"""
        if 'on' == on_off.lower():
            self.on = self._slot,1
        else:
            self.on = self._slot,0

    def unlock(self, on1off0=0):
        """Turn the lock off"""
        self.write('lock {},1234'.format(on1off0))

    def __exit__(self, exception_type, exception_value, traceback):
        if super()._is_offline():
            return
        # self.output('off')
        ut.wait_s(0.2)
        self.instr.control_ren(0)  # go to local
        self.instr.close()         # close visa connection

