# -*- coding: utf-8 -*-
"""
Created on Tue May 15 12:32:48 2018

@author: Tobias Jachowski
"""
import h5py
import numpy as np
import os

from pyoti.data.datasource import DataSource


class HDF(DataSource):
    def __init__(self, filename, section=None, directory=None, datext='.bin',
                 parext='_para.dat', **kwargs):
        """
        parext : str, optional
            The extension of the parameter file ('_para.dat', default)
        """
        super().__init__(filename=filename, directory=directory, **kwargs)
        # TODO: Is it necessary to select a certain section?
        self.section = section

        self.samplingrate = get_samplingrate(self.absfile, section=section)

        self.name = ("HDF data originally loaded from \n"
                     "    %s with \n"
                     "    samplingrate %s Hz") % (self.absfile_orig,
                                                  self.samplingrate)

    def as_array(self):
        filename = self.absfile
        f = h5py.File(filename, "r")
        # TODO: for trace in ... do
            data = f[self.section]
        return data

    @property
    def parafile_orig(self):
        return self._parafile_orig

def get_samplingrate(filename, section=None):
    f = h5py.File(filename, "r")
    # TODO: howto get proper samplingrate
    samplingrate = f[section]["Sample rate (Hz)"]
    return samplingrate
