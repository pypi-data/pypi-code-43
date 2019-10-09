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

    com = ut.Dotdict({
        'output'       : 'sour{}:pow:stat {}; *OPC?',
        'output_check' : 'sour{}:pow:stat?',
        'p_dBm'        : 'sour{}:pow {}dbm; *OPC?',
        'wl_nm'        : 'sour{}:wav {}nm; *OPC?',
        'lock'         : 'lock {},1234',
        'reset'        : '*RST',
        'sweep_state'  : 'sour{}:wav:swe {}',
        'sweep_mode'   : 'sour{}:wav:swe:mode {}',
        'sweep_start'  : 'sour{}:wav:swe:star {:.4f}nm',
        'sweep_stop'   : 'sour{}:wav:swe:stop {:.4f}nm',
        'sweep_step'   : 'sour{}:wav:swe:step {:.4f}nm',
        'sweep_cycle'  : 'sour{}:wav:swe:cycl {}',
        'sweep_speed'  : 'sour{}:wav:swe:spe {:.4f}nm/s',
        'sweep_wl_log' : 'sour{}:wav:swe:llog {}',
        'sweep_check'  : 'sour{}:wav:swe:checkparams?',
        'trigger'      : 'trig{}:chan:outp {}',
        'trigger_rearm': 'trig{}:chan:OUTPut:REARm {}',
        'trigger_count': 'sour{}:wav:swe:exp?',
    })
    
    def __init__(self, address='GPIB::11::INSTR', slot=1,
                 online=True, name=None):
        """Generate instance of class NiDaq_ao"""
        super().__init__(address=address, online=online, name=name)
        self._slot = slot

    # ----- Instrument limits and options --------------------------------------
    # model specific ranges
    models = {'':''}
    lim = ut.Dotdict({
            'output'       : {'ON':1, 'OFF':0},
            'p_dBm'        : (-10, 14),
            'wl_nm'        : (1440, 1595),
            'lock'         : {'lock'  :0, 'unlock':1,},
            'sweep_state'  : ['stop', 'start', 'pause', 'continue'],
            'sweep_mode'   : ['CONT', 'MAN', 'CONT'],
            'sweep_speed'  : (1, 100),  # nm/s, arbitrarily set, # TODO: Test
            'sweep_step'   : (0, 50),   # nm,   arbitrarily set, # TODO: Test
            'sweep_cycles' : (1, 100),  # ,     arbitrarily set, # TODO: Test
            'sweep_wl_log' : ['ON', 'OFF'],
            'trigger'      : ['disabled',
                              'avgover',
                              'measure',
                              'modulation',
                              'stfinished',  # when sweep step finishes
                              'swfinished',
                              'swstarted',],
            'trigger_rearm': ['ON', 'OFF'],
            
          })
    # ----- Instrument properties ----------------------------------------------
    on = Instrument.prop(com.output, "Set output 'ON' or 'OFF'",
                         in_set=lim.output, name='output')
    p_dBm = Instrument.prop(com.p_dBm, docs="Set output power in dBm",
                            in_range=lim.p_dBm, name='power')
    lock = Instrument.prop(com.lock, docs="Lock or unlock laser output",
                           in_set=lim.lock, name='lock')
    wl_nm = Instrument.prop(com.wl_nm, docs="Set output wavelength in m",
                            in_range=lim.wl_nm, name='wavelength')
    sweep_state = Instrument.prop(com.sweep_state, docs="Set sweep state",
                                  in_set=lim.sweep_state, name='sweep_state')
    sweep_mode = Instrument.prop(com.sweep_mode, docs="Set sweep mode",
                                 in_set=lim.sweep_mode, name='sweep_mode')
    sweep_start = Instrument.prop(com.sweep_start, docs="Set sweep start wl",
                                  in_set=lim.wl_nm, name='sweep_start_wl')
    sweep_stop = Instrument.prop(com.sweep_stop, docs="Set sweep stop wl",
                                 in_set=lim.wl_nm, name='sweep_stop_wl')
    sweep_step = Instrument.prop(com.sweep_step, docs="Set sweep step wl",
                                 in_set=lim.wl_nm, name='sweep_step_wl')
    sweep_cycles = Instrument.prop(com.sweep_cycles, docs="Set sweep cycles",
                                   in_set=lim.sweep_cycles, name='sweep_cycles')
    sweep_wl_log = Instrument.prop(com.sweep_wl_log, docs="Set sweep wl logging",
                                   in_set=lim.sweep_mode, name='sweep_wo_log')
    trigger = Instrument.prop(com.trigger, docs="Set when trigger is rearmed",
                              in_set=lim.trigger, name='trigger')
    trigger_rearm = Instrument.prop(com.trigger_rearm, docs="Rearm trigger",
                                    in_set=lim.trigger_rearm, name='trigger_rearm')
    # --------------------------------------------------------------------------

    def __enter__(self):
        if super()._is_offline():
            return
        self.instr = self._rm.open_resource(self._address)
        self._model = None  # TODO, implement model check
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
            self.on = self._slot, 1
        else:
            self.on = self._slot, 0

    def output_is_on(self):
        """Check if laser output is on, promptu user if not"""
        command = self.com.output_check.format(self._slot)
        # print(command)
        response = ut.parse_floats(self.query(command))
        if response==0:
            _ = input('TLS is off, turn it on manually and press ENTER\n')

    def unlock(self, lock='unlock'):
        """Turn the lock off"""
        self.lock = (lock,)

    def sweep_setup(self, p, start, stop, step=0.1, speed_nmps=5, cycles=1):
        """Setup wavelength sweep conditions, return trigger count"""
        self.sweep_mode    = self._slot, 'CONT'
        self.sweep_start   = self._slot, start
        self.sweep_stop    = self._slot, stop
        self.sweep_step    = self._slot, step
        self.sweep_cycles  = self._slot, cycles
        self.sweep_speed   = self._slot, speed_nmps
        self.sweep_wl_log  = self._slot, 'ON'
        self.trigger       = self._slot, 'STFinished'
        self.trigger_rearm = self._slot, 'ON'
        
        # check if sweep setup is ok, print error message
        sweep_ok_raw = self.query(self.com.sweep_check.format(self._slot))
        if 'OK' in sweep_ok_raw:
            pass
        else:
            error_code = ut.parse_floats(sweep_ok_raw, iterable=False)
            error_codes = {368: 'start wavelength must be smaller than stop wavelength',
                           369: 'the total time of the sweep is too small',
                           370: 'the total time of the sweep is too large',
                           371: 'the trigger frequency (calculated from sweep speed divided by sweep step) is too large',
                           372: 'step size too small',
                           373: 'the number of triggers exceeds the allowed limit',
                           374: 'The only allowed modulation source with the lambda logging function is coherence control',
                           375: 'lambda logging only works "Step Finished" output trigger configuration',
                           376: 'lambda logging can only be done in continuous sweep mode',
                           377: 'the step size must be a multiple of the smallest possible step size',
                           378: 'the number of triggers exceeds the allowed limit',
                           }
            try:
                error_msg = error_codes[error_code]
            except:
                error_msg = sweep_ok_raw
            raise ValueError(error_msg)
        # Set laser to starting wavelength, turn output on
        self.wl_nm = self._slot, start
        self.p_dBm = self._slot, p
        self.output = 'ON'
        self.output_is_on()

    def fast_scan(self, pm, p_pm_range, p_tls, start, stop, step=0.1, speed_nmps=5, cycles=1):
        """Intiate fast scan and return [p_mW, wl_nm]"""
        self.sweep_setup(p_tls, start, stop, step, speed_nmps, cycles)
        trigger_count_raw = self.query(self.com.trigger_count.format(self._slot))
        trigger_count = ut.parse_floats(trigger_count_raw, iterable=False)
        # set avg time to half of the time interval between 2 steps
        averaging_time = 0.5*(stop-start)/speed_nmps/((stop-start)//step+1)
        wl = (start+stop)/2
        pm.sweep_prepare(p_pm_range, wl, trigger_count, averaging_time)
        # start sweep
        self.st

    def __exit__(self, exception_type, exception_value, traceback):
        if super()._is_offline():
            return
        # self.output('off')
        ut.wait_s(0.2)
        self.instr.control_ren(0)  # go to local
        self.instr.close()         # close visa connection

