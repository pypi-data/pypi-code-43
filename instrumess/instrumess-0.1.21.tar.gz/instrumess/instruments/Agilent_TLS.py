# -*- coding: utf-8 -*-
"""
Created on Wednesday 15-August-2018 at 15:27

@author: Rastko Pajković
"""

from instrument_v3 import Instrument
import utilities as ut

# =============================================================================
#  WARNING: read the equipment manual, this code thinks you are smart  ! ! !
# =============================================================================


class AgilentTLS(Instrument):
    """Driver for Agilent frames TLS modules"""

    commands = {
        'output': 'sour{slot:d}:pow:stat {on1off0:d}; *OPC?',
        'p'     : 'sour{slot:d}:pow {p_dBm:.3f}dbm; *OPC?',
        'wl'    : 'sour{slot:d}:wav {wl_m:.7E}; *OPC?',
        'reset' : '*RST',
    }
    com = ut.Dotdict(commands)
    
    def __init__(self, address='GPIB::11::INSTR', slot=1,
                 online=True, name=None):
        """Generate instance of class NiDaq_ao"""
        super().__init__(address=address, online=online, name=name)
        self._slot = slot

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

    def __exit__(self, exception_type, exception_value, traceback):
        if super()._is_offline():
            return
        # self.write(self.com.output.format(slot=self._slot,
        #                                   on1off0=0))
        ut.wait_s(0.2)
        self.instr.control_ren(0)  # go to local
        self.instr.close()         # close visa connection

    def setup(self, wl_nm=None, p_dBm=None):
        """Set TLS wavelength and/or power"""
        if wl_nm is not None:
            self.query(self.com.wl.format(slot=self._slot, wl_m=wl_nm/1e9))
        if p_dBm is not None:
            self.query(self.com.p.format(slot=self._slot, p_dBm=p_dBm))

    def output(self, on_off='OFF'):
        """Turn TLS on or off"""
        on_off_flag = 1 if 'on' == on_off.lower() else 0
        self.query(self.com.output.format(slot=self._slot,
                                          on1off0=on_off_flag))

if __name__ == '__main__':
    with AgilentTLS(address='GPIB::20::INSTR') as tls:
        tls.setup(wl_nm=1522, p_dBm=13)
        ut.wait_s(0.1)
        tls.output('on')
