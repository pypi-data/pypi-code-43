import visa
from instrument import Instrument
from time import sleep

rm = visa.ResourceManager()

class Apex(Instrument):
    def __init__(self, model='2641B', ip_addr=None, online=True, name=None):
        if ip_addr is None:
            if model in ['2641B', 'new']:
                ip_addr = 'TCPIP::192.168.1.8::5900::SOCKET'
            elif model in ['2041A', 'old']:
#                ip_addr = 'TCPIP::192.168.1.10::6500::SOCKET'
                ip_addr = 'TCPIP::192.168.1.102::6500::SOCKET'
        super().__init__(address=ip_addr, name=name, online=online)


    def init(self):
        if super()._is_offline():
            return
        self.instr = rm.open_resource(self._address)
        self.reset()

    def setup(self, 
                    # wl_from=None, wl_to=None, # valid if wl_cent is none
                    wl_cent=None, span=None,  
                    res=None,  # 0 for 100MHz, 1 for 20MHz
                    ):
        if super()._is_offline():
            return
        # this doesn't work, Apex drags the other end when one is changed
#        if wl_from is not None and wl_to is not None:
#            self.instr.query('SPSTRTWL%.3f'%wl_from)
#            sleep(0.1)
#            self.instr.query('SPSTOPWL%.3f'%wl_to)
        if wl_cent is not None and span is not None:
            self.instr.query('SPSPANWL%.3f'%span)
            sleep(0.1)
            self.instr.query('SPCTRWL%.3f'%wl_cent)
        if res is not None:
            sleep(0.1)
            self.instr.query('SPSWPRES%1d'%res)
            

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
        if super()._is_offline():
            return
        if sweep_first:
            self.sweep()
        p_dBm = self.instr.query('SPDATAL%d'%trace)
        wl = self.instr.query('SPDATAWL{:d}'.format(trace))  
        if save_to is not None:
            pass
        return p_dBm, wl

    def save_locally(self, filepath):
        if super()._is_offline():
            return
        answer = self.instr.query('SPSAVEB0_{}'.format(filepath))  # save trace 0 !!!
        if answer!='SP_SAVE_SPECTRUM_TXT':
            raise ValueError('Save went south')
        return answer

    def analyze_sweep(self, smsr=True):
        pass

    def reset(self):
        # configure instument and communication
        self.instr.write_termination = '\n'
        self.instr.read_termination = '\n'
        self.instr.timeout = 60000          # set the timeout to one minute
        self.instr.write('SPAVERAGE0')    # disable average mode
        sleep(0.1)
        self.instr.query('SPXUNT1')       # set x-unit to wavelength
        self.instr.query('SPLINSC1')        # set y-scale unit to dBm
        self.instr.query('SPSWPMSK-80')  # set noise mask to -100 dBm
        self.instr.query('SPAUTONBPT1')   # auto-choose number of points
        self.instr.query('SPSWPRES0')     # set resolution to 100MHz
        self.instr.write('SPINPUT0')      # physical SM optical input
        sleep(0.1)        
        self.instr.query('SPPOLAR0')      # sum both polarizations

    def close(self):
        if super()._is_offline():
            return
        self.instr.close()
