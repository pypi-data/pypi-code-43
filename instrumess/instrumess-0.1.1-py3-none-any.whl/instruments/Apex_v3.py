"""Driver for Old Apex"""
import visa
from instrument_v2 import Instrument
from time import sleep
import utilities as ut


rm = visa.ResourceManager()


class Apex(Instrument):
    """Apex driver class"""

    def __init__(self, model='old', ip_addr=None, online=True, name=None):
        """Intialize Apex instance"""
        if ip_addr is None:
            if model in ['2641B', 'new']:
                ip_addr = 'TCPIP::192.168.1.8::5900::SOCKET'
            elif model in ['2041A', 'old']:
                ip_addr = 'TCPIP::192.168.1.14::6500::SOCKET'   # OLA2 new
                # ip_addr = 'TCPIP::192.168.1.10::6500::SOCKET'   # OLA1 router
                # ip_addr = 'TCPIP::192.168.1.102::6500::SOCKET'  #OLA2 router
        super().__init__(address=ip_addr, name=name, online=online)

    def __enter__(self):
        if super()._is_offline():
            return
        self.instr = rm.open_resource(self._address)
        self.reset()
        return self

    def setup(self, wl_from=None, wl_to=None,
              wl_cent=None, span=None,  # in nm
              res='100MHz',     # '100MHz' or '20MHz'
              points=None,  # 'auto' or 2 to 20 000
              noise_mask=None,
              ):
        """Setup Apex parameters"""
        resolution = {'100MHz':0,
                      '20MHz':1}
        if super()._is_offline():
            return
        if wl_from is not None and wl_to is not None:
            wl_cent = (wl_from + wl_to)/2
            span = abs(wl_from-wl_to)
#         this doesn't work, Apex drags the other end when one is changed
#            self.instr.query('SPSTRTWL%.3f'%wl_from)
#            sleep(0.1)
#            self.instr.query('SPSTOPWL%.3f'%wl_to)
        if wl_cent is not None and span is not None:
            self.instr.query('SPSPANWL%.3f'%span)
            sleep(0.1)
            self.instr.query('SPCTRWL%.3f'%wl_cent)
        if res is not None:
            sleep(0.1)
            self.instr.query('SPSWPRES%1d'%resolution[res])
        if points is not None:
            points = str(points)
            if points.lower() == 'auto':
                answer = self.instr.query('SPAUTONBPT1')
                if answer != 'SP_POINT_NUMBER_AUTO':
                    raise ValueError('Something went wrong with setting the'
                                     ' auto point number')
            else:
                answer = self.instr.query('SPAUTONBPT0')
                if answer != 'SP_POINT_NUMBER_MANUAL':
                    raise ValueError('Something went wrong with setting the'
                                     ' auto point number')
                self.instr.query('SPNBPTSWP'+points)
        if noise_mask is not None:
            self.instr.query('SPSWPMSK{}'.format(noise_mask))

    def sweep(self, sweep_type='single'):
        if super()._is_offline():
            return
        try:
            sweep_type = ['auto',
                          'single',
                          'repeat',
                          'stop'].index(sweep_type)  # assign a number
        except:
            print('Warning: "%s" is not a valid sweep type')
            print("Choose from 'auto', 'single', 'repeat', 'stop'.")
            return
        return self.instr.query('SPSWP%d'%sweep_type)

    def get_sweep(self, trace=1 ,sweep_first=False, save_to=None):
        """doesn't work, old Apex does not respond to queries"""
        if super()._is_offline():
            return
        if sweep_first:
            self.sweep()
        p_dBm = self.instr.query('SPDATAL%d'%trace)
        wl = self.instr.query('SPDATAWL{:d}'.format(trace))
        if save_to is not None:
            pass
        return p_dBm, wl

    def save_locally(self, rel_filepath,
                     move_to=None,
                     apex_root='R:/',
                     pc_shared_folder='D:/Apex spectra'):
        """Save spectrum.txt in the shared folder on PC
        
        Parameters
        ----------
        rel_filepath : str or pathlib Path
            Relative file path with filename on Apex to store the spectrum in
        move_to : str of pathlib Path
            Folder on PC to move the spectrum to
        apex_root : str
            Drive letter on Apex that will be prepended to rel_filepath, ex. R:/
        pc_shared : str
            Folder path on PC where the spectra are stored
        
        Returns
        -------
        pathlib Path
            Path on PC where the spectrum is stored
        """
        if super()._is_offline():
            return
        # make rel_filepath relative if it already isn't
        if not ut.Path(rel_filepath).anchor=='':
            filepath = ut.Path(rel_filepath.parts[1:])
        filepath = ut.Path(apex_root)/rel_filepath
        pc_path = ut.Path(pc_shared_folder)/(str(rel_filepath)+'_spectrum.txt')
        pc_path.parent.mkdir(mode=0o777, parents=True, exist_ok=True)
        answer = self.instr.query('SPSAVEB0_{}'.format(filepath))  # trace 0 !!!
        if answer!='SP_SAVE_SPECTRUM_TXT':
            raise ValueError('Save went south')
        if move_to is not None:
            move_from = pc_path.parent
            filename = pc_path.name
            ut.move_files(move_from, move_to, pattern=filename, mode='move')
            return ut.Path(move_to)/filename
        return pc_path

    def reset(self):
        """Configure communication and bring instrument into a knows state"""
        self.instr.write_termination = '\n'
        self.instr.read_termination = '\n'
        self.instr.timeout = 60000       # set the timeout to one minute
        self.instr.write('SPAVERAGE0')   # disable average mode
        sleep(0.1)
        self.instr.query('SPXUNT1')      # set x-unit to wavelength
        self.instr.query('SPLINSC1')     # set y-scale unit to dBm
        self.instr.query('SPSWPMSK-80')  # set noise mask to -100 dBm
        self.instr.query('SPAUTONBPT1')  # auto-choose number of points
        self.instr.query('SPSWPRES0')    # set resolution to 100MHz
        self.instr.write('SPINPUT0')     # physical SM optical input
        sleep(0.1)
        self.instr.query('SPPOLAR0')    # sum both polarizations

    def __exit__(self, exception_type, exception_value, traceback):
        if super()._is_offline():
            return
        self.instr.close()


# def setup():
#     """Set Apex default settings"""
#     with Apex(model='old'):
#         pass


# def sweep():
#     """Sweep Apex once"""
#     with Apex(model='old') as apex:
#         apex.sweep(sweep_type='single')
