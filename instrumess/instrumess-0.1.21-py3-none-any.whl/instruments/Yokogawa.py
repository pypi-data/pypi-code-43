# -*- coding: utf-8 -*-
"""
Created on Tuesday 09-April-2019 at 16:49

@author: Rastko Pajković
"""

import utilities as ut
from OSA import OSA
import visa
import validate
import plot_aux


class YokogawaAQ6375(OSA):
    """Driver for theYokogawa AQ6375 OSA"""

    # the idea is that this code can be reused for any OSA
    # by simply changing the com, limits and setup_known_state

    # list of string commands to communicate with the instrument
    com = ut.Dotdict({  # Dotdict makes dictionary keys easier to access
        'resolution'        : ':SENSe:BANDwidth:RESolution {:.2f}NM',
        'sensitivity'       : ':SENSe:SENSe {:s}',
        'start_wl'          : ':SENSe:WAVelength:STARt {:07.2f}NM',
        'stop_wl'           : ':SENSe:WAVelength:STOP {:07.2f}NM',
        'averaging'         : ':SENSe:AVERage:COUNt {:d}',
        'num_samples'       : ':SENSe:SWEep:POINts {:04d}',
        'num_samples_auto'  : ':SENSe:SWEep:POINts:AUTO {}',
        'ref_level'         : ':DISPlay:TRACe:Y1:RLEVel {:02.1f}DBM',
        'y_div'             : ':DISPlay:TRACe:Y1:PDIVision {:02.1f}DB',
        'get_p'             : ':TRACe:Y? TRA',  # TRA stands for trace A
        'get_wl'            : ':TRACe:X? TRA',  # TRA stands for trace A
        'sweep'             : ':INITiate:SMODe {:s};:INITiate',
        'sweep_stop'        : ':ABORt',
        'active_trace'      : ':TRACe:ACTive TRA',  # TRA stands for trace A
        'set_command_format': 'CFORM1',  # sets the command format to AQ6375
    })

    # ----- Limits, accepted values --------------------------------------------
    limits = ut.Dotdict({
        'resolution'   : [0.05, 0.1, 0.2, 0.5, 1, 2, 5, 10],  # nm
        'sensitivity'  : {'normal-hold': 'NHLD',
                          'normal-auto': 'NAUT',
                          'normal'     : 'NORMal',
                          'middle'     : 'MID',
                          'hi1'        : 'HIGH1',
                          'hi2'        : 'HIGH2',
                          'hi3'        : 'HIGH3',},
        'wl'           : (1200, 2400),  # nm
        'averaging'    : (1, 1000),
        'num_samples'  : (101, 16001),
        'num_samples_auto': ['on', 'off'],
        'sweep'        : {'single':'SINGle',
                          'repeat':'REPeat',
                          'auto'  :'AUTO',
                          'stop'  :'STP'},
        'ref_level'    : (-90, 20),
        'y_div'        : (0.1, 10),
    })
    # ----- Properties ---------------------------------------------------------
    # properties are a convienince that performs limits check
    prop = OSA.prop
    # sweep = prop(com.sweep, docs="Sweep type",
    #              in_range=limits.sweep, name='sweep')
    resolution = prop(com.resolution, docs="Set resolution in nm",
                      in_set=limits.resolution, name='resolution')
    sensitivity = prop(com.sensitivity, docs="Set sensitivity",
                       in_set=limits.sensitivity, name='sensitivity')
    start_wl = prop(com.start_wl, docs="Set start_wl in nm",
                    in_range=limits.wl, name='start_wl')
    stop_wl = prop(com.stop_wl, docs="Set stop_wl in nm",
                   in_range=limits.wl, name='stop_wl')
    averaging = prop(com.averaging, docs="Set spectra averaging",
                     in_range=limits.averaging, name='averaging')
    num_samples = prop(com.num_samples, docs='Number of sample points in sweep',
                       in_range=limits.num_samples, name='num_samples')
    num_samples_auto = prop(com.num_samples_auto, docs='Number of sample points in sweep',
                            in_range=limits.num_samples_auto, name='num_samples')

    ref_level = prop(com.ref_level, docs='Display reference level in dB',
                     in_range=limits.ref_level, name='ref_level')
    y_div = prop(com.y_div, docs='Display div in dB',
                 in_range=limits.y_div, name='y_div')

    # ----- Functions ----------------------------------------------------------

    def __enter__(self):
        self._rm = visa.ResourceManager()
        self.instr = self._rm.open_resource(self._address)
        self.reset()
        self.instr.read_termination = '\n'
        self.instr.write_termination = '\n'
        self.instr.timeout = 60000
        self.write(self.com.set_command_format)  # in case of AQ6317 format
        self.write(self.com.active_trace)
        return self
    
    def reset(self):
        """Reset the instrument to a known state"""
        pass

    def setup(self,
              wl_range_nm=None,
              sensitivity=None,
              resolution=None,
              num_samples=None,
              averaging=None,
              ):
        """Setup the functions of OSA that influence the measurement"""
        if wl_range_nm is not None:
            self.start_wl = min(wl_range_nm)
            self.stop_wl = max(wl_range_nm)
        if sensitivity is not None:
            self.sensitivity = sensitivity
        if resolution is not None:
            self.resolution = resolution
        if num_samples is not None:
            if num_samples=='auto':
                self.num_samples_auto = 'on'
            else:
                self.num_samples = num_samples
        if averaging is not None:
            self.averaging = averaging

    def sweep(self, sweep_type='single'):
        """Send the command to sweep 'single' 'repeat', 'auto'"""
        validate.in_set(sweep_type, self.limits.sweep, name='sweep')
        self.write(self.com.sweep.format(self.limits.sweep[sweep_type]))
        # self.sweep = sweep_type

    def sweep_stop(self):
        """Send the command to stop a sweep"""
        self.write(self.com.sweep_stop)

    def set_yscale(self, ref_level=None, y_div=None):
        """Set display properties of Y axis"""
        if ref_level is not None:
            self.ref_level = ref_level
        if y_div is not None:
            self.y_div = y_div

    def get_data(self):
        """Get sweep data: wl, p"""
        p_raw = self.query(self.com.get_p)
        wl_raw = self.query(self.com.get_wl)
        p, wl = [ut.parse_floats(el) for el in [p_raw, wl_raw]]
        return wl*1e9, p

    def get_spectrum(self, sweep_first=True,
                     show=False, save_plot=False, unique_plot_name=False,
                     save_to_folder=None, header=None, unique_name='Spectrum'):
        """Get sweep data: wl, p; optionaly plot and save"""
        if sweep_first:
            self.sweep(sweep_type='single')
        wl, p = self.get_data()
        if show:
            plot_name = unique_name if unique_plot_name else 'Spectrum'
            fig, ax = plot_aux.spectrum(wl, p, name=plot_name)
            plot_aux.plt.pause(0.05)  # give ploter time to update figure
        if save_to_folder is not None:
            save_to_folder = ut.Path(save_to_folder)
            df = ut.df_init(['wl', 'p'], numel=len(p), units=['nm', 'dBm'])
            df.p[1:], df.wl[1:] = p, wl
            ut.df_write(df, save_to_folder/(unique_name+'.txt'),
                        overwrite=False, header=header)
            if save_plot:
                plot_aux.save_last_fig(name=unique_name, dest=save_to_folder,
                                       filetype='png', dpi=150)
        return wl, p
