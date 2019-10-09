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


class AgilentPM(Instrument):
    """Driver for Agilent frames TLS modules"""

    commands = {
        'get_p'     : 'read{}:pow?',
        'set_wl'    : 'sens{}:pow:wav {}nm; *OPC?',
        'set_unit'  : 'sens{}:pow:unit {}',       # 0-dBm, 1-W
        'range_auto': 'sens{}:pow:rang:auto {}',  # 0-off
        'range'     : 'sens{}:pow:rang {}',
        'set_unit'  : 'sens{}:pow:unit {}',  # 0-dBm, 1-W
        'reset'     : '*RST',
    }
    com = ut.Dotdict(commands)
    
    def __init__(self, address='GPIB::11::INSTR', slot=2,
                 online=True, name=None):
        """Generate instance of class NiDaq_ao"""
        super().__init__(address=address, online=online, name=name)
        self._slot = slot

    # ----- Instrument properties ----------------------------------------------
    wl_nm = Instrument.prop(com.set_wl, docs="Set output wavelength in nm",
                            in_range=(1440,1595),
                            name='wavelength')
    range_auto = Instrument.prop(com.range_auto, docs="Set range mode",
                                 in_set=[0,1],
                                 name='range_auto')
    range_max = Instrument.prop(com.range, docs="Set range maximum",
                                in_set=[10, 0 , -10, -20])
    unit = Instrument.prop(com.set_unit, docs="Set unit, 0-dBm, 1-W",
                           in_set=(0,1), name='Unit')
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

    def set_range(self, range='auto'):
        """Set range to auto or maximal expected value in [10, 0, -10, -20]"""
        if range=='auto':
            self.range_auto = self._slot, 1
        else:
            self.range_auto = self._slot, 0
            self.range_max = self._slot, range

    def set_unit(self, unit='dbm'):
        """Set units to w or dbm"""
        if unit.lower()=='w':
            self.unit = self._slot, 1
        elif unit.lower()=='dbm':
            self.unit = self._slot, 0
        else:
            raise ValueError('Unit {} is not recognized, allowed units are "w" and "dbm".'.format(unit))

    def setup(self, wl_nm=None, range=None, units=None):
        """Set TLS wavelength and/or power"""
        if wl_nm is not None:
            self.wl_nm = self._slot, wl_nm  # tuple
        if range is not None:
            self.set_range(range=range)
        if units is not None:
            self.set_unit(unit=units)

    def get_power(self):
        """Get the power reading, in set unit"""
        raw = self.query(self.com.get_p.format(self._slot))
        power = ut.parse_floats(raw)
        try:
            power = power[-1]
        except:
            pass
        if power > 3e38:
            power = -100  # noise floor, arbitrarily set
        return power

    def __exit__(self, exception_type, exception_value, traceback):
        if super()._is_offline():
            return
        self.instr.control_ren(0)  # go to local
        self.instr.close()         # close visa connection

# if __name__ == '__main__':
#     with AgilentPM(address='GPIB::20::INSTR') as pm:
#         pm.setup(wl_nm=1523)
#         p = pm.get_power()
