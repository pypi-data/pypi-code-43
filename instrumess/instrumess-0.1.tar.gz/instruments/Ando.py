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


class Ando6315A(OSA):
    """Driver for the Ando 6315A OSA"""

    # the idea is that this code can be reused for any OSA
    # by simply changing the com, limits and setup_known_state

    # list of string commands to communicate with the instrument
    com = ut.Dotdict({  # Dotdict makes dictionary keys easier to access
        'resolution'      : 'RESOLN{:.2f}',
        'sensitivity'     : 'S{:s}',
        'start_wl'        : 'STAWL{:07.2f}',
        'stop_wl'         : 'STPWL{:07.2f}',
        'averaging'       : 'AVG{:d}',
        'monochromator'   : 'MONO{:d}',
        'chopper'         : 'CHOP{:d}',
        'num_samples'     : 'SMPL{:04d}',
        'ref_level'       : 'REFL{:02.1f}',
        'y_div'           : 'LSCL{:02.1f}',
        'get_p'           : 'LDATA',
        'get_wl'          : 'WDATA',
        'get_sweep_status': 'SWEEP?',
        'set_cw_mode'     : 'CLMES',
        'set_str_delim'   : 'SD0',  # sets , as the string delimiter
        'set_block_delim' : 'BD1',  # sets \n as the block delimiter
    })

    # ----- Limits, accepted values --------------------------------------------
    limits = ut.Dotdict({
        'resolution'   : [0.05, 0.1, 0.2, 0.5, 1, 2, 5, 10],  # nm
        'sensitivity'  : {'normal-hold': 'NHD',
                          'normal-auto': 'NAT',
                          'hi1'        : 'HI1',
                          'hi2'        : 'HI2',
                          'hi3'        : 'HI3',},
        'wl'           : (350, 1750),  # nm
        'averaging'    : (1, 1000),
        'monochromator': {'single': 0,
                          'double': 1},
        'chopper'      : {'internal': 0,
                          'external': 1},
        'num_samples'  : (11, 1001),
        'sweep'        : {'single':'SGL',
                          'repeat':'RPT',
                          'auto'  :'AUTO',
                          'stop'  :'STP'},
        'ref_level'    : (-90, 20),
        'y_div'        : (0.1, 10),
    })
    # ----- Properties ---------------------------------------------------------
    # properties are a convienince that performs limits check
    prop = OSA.prop
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
    monochromator = prop(com.monochromator, docs="Set monochromator",
                         in_set=limits.monochromator, name='monochromator')
    chopper = prop(com.chopper, docs="Set chopper",
                   in_set=limits.chopper, name='chopper')
    num_samples = prop(com.num_samples, docs='Number of sample points in sweep',
                       in_range=limits.num_samples, name='num_samples')
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
        self.instr.write(self.com.set_str_delim)
        self.instr.write(self.com.set_block_delim)
        self.instr.timeout = 10000
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
              monochromator=None,
              chopper=None):
        """Setup the functions of OSA that influence the measurement"""
        if wl_range_nm is not None:
            self.start_wl = min(wl_range_nm)
            self.stop_wl = max(wl_range_nm)
        if sensitivity is not None:
            self.sensitivity = sensitivity
        if resolution is not None:
            self.resolution = resolution
        if num_samples is not None:
            self.num_samples = num_samples
        if averaging is not None:
            self.averaging = averaging
        if monochromator is not None:
            self.monochromator = monochromator
        if chopper is not None:
            self.chopper = chopper

    def setup_known_state(self):
        """Set important parameters to a known state"""
        self.averaging = 1
        self.monochromator = 'single'
        self.chopper = 'internal'
        self.write(self.com.set_cw_mode)  # set CW instead of pulsed

    def wait_sweep_finish(self, wait_s=0.05):
        """Wait for the sweep to finish"""
        while True:
            ans_raw = self.query(self.com.get_sweep_status)
            answer = ut.parse_floats(ans_raw)
            if answer==0:
                break
            elif answer==2:
                print('Sweep is on REPEAT')
                break
            ut.wait_s(wait_s)

    def sweep(self, sweep_type='single'):
        """Send the command to sweep 'single' 'repeat', 'stop', 'auto'"""
        validate.in_set(sweep_type, self.limits.sweep, name='sweep')
        self.write(self.limits.sweep[sweep_type])

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
        p, wl = [ut.parse_floats(el)[1:] for el in [p_raw, wl_raw]]
        return wl, p

    def get_spectrum(self, sweep_first=True,
                     show=False, save_plot=False, unique_plot_name=False,
                     save_to_folder=None, header=None, unique_name='Spectrum'):
        """Get sweep data: wl, p; optionaly plot and save"""
        if sweep_first:
            self.sweep(sweep_type='single')
        self.wait_sweep_finish()
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
