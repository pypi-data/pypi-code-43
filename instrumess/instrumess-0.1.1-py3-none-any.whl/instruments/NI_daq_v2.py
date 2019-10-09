# -*- coding: utf-8 -*-
"""
Created on Wednesday 15-August-2018 at 15:27

@author: Rastko Pajković
"""

import nidaqmx
from instrument_v3 import Instrument
import utilities as ut

system = nidaqmx.system.System.local()

VOLTAGES = {
    "phase_section":0,
    "coarse_long":1,
    "coarse_short":2,
    "medium_long":3,
    "medium_short":4,
    "fine_short":5,
    "fine_long":6,
}
VOLTAGES = ut.Dotdict(VOLTAGES)

class NiDaq_ao(Instrument):
    """Driver for NI cDAQ 16xAnalog output module"""

    DEST = ut.make_fold('Voltages_cDAQ', date=False,
                        root='D:/Dropbox/PhD - ITL for SS-OCT/Measurements')

    def __init__(self, address='cDAQ1Mod2', channels='0:6' ,online=True,
                 name=None):
        """Generate instance of class NiDaq_ao"""
        super().__init__(address=address, online=online, name=name)
        self.channels = channels
        self.voltages = None

    def __enter__(self):
        if super()._is_offline():
            return
        self._task = nidaqmx.Task('analog_output')
        self.set_channels(channels_string=self.channels)
        return self

    def set_channels(self, channels_string):
        """define output channels in e.g. '0, 2, 4:8' format """
        if super()._is_offline():
            return
        self._task.ao_channels.add_ao_voltage_chan(self._address+'/ao'+channels_string)
        self._task.start()
        self.channels = self._parse_channels(channels_string)

    def _parse_channels(self, channels_string):
        channels = []
        elems = channels_string.split(',')
        for elem in elems:
            if ':' in elem:
                first, *middle, last = map(int,elem.split(':'))
                channels += list(range(first, last+1))
            else:
                channels += int(elem)
        return channels

    def set_voltages(self, voltages, non_positive=True):
        """set voltages on the output channels"""
        if non_positive:
            voltages = [-abs(v) for v in voltages]
        self.voltages = voltages
        if super()._is_offline():
            return
        self._task.write(voltages)

    def reset(self):
        """Reset instrument to a known state and setup communication"""
        if super()._is_offline():
            return
        self._task.write([0]*len(self.channels))

    def get_saved_voltages(self, v_name=None, date='today', set_v=False):
        """Read saved voltages and return df or voltages if name is given"""
        if date=='today':
            filename = ut.get_date(form='str')[:-1]+'.txt'
        else:
            filename = date+'.txt'
        source = self.DEST/filename
        df = ut.df_read(source, column_names=None, index_col=0)
        if v_name is None:
            return df
        else:
            df = df[~df.index.duplicated(keep='first')]
            voltages = df.loc[str(v_name)].values[:7]
            if set_v:
                self.set_voltages(voltages)
            return voltages

    def save_voltages(self, v_name):
        """Save current voltages to a file"""
        filename = ut.get_date(form='str')[:-1]+'.txt'
        dest = self.DEST/filename
        df = ut.df_init(columns=['phase section',
                                 'coarse long',
                                 'coarse short',
                                 'medium long',
                                 'medium short',
                                 'fine short',
                                 'fine long',
                                 'ts'],
                        numel=0,
                        units=['V']*7+['microseconds'])
        df.loc[v_name] = self.voltages + [ut.get_time(form='dt')]
        if dest.is_file():
            df = df.drop('#units')
            add_header = False
            df_old = self.get_saved_voltages()
            if v_name in df_old.index.values:
                raise ValueError('Entry {} already exists'.format(v_name))
        else:
            add_header = True
        ut.wait_s(0.1)
        ut.df_write(df, dest, header=add_header, mode='a')

    def __exit__(self, exception_type, exception_value, traceback):
        if super()._is_offline():
            return
        # self.reset()  # prevent voltages going back to 0 after releasing inst
        self._task.close()
