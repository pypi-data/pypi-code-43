# -*- coding: utf-8 -*-
"""
Created on Sat Aug 12 01:23:20 2017

@author: Rastko
"""

import numpy as np
import pandas as pd
import glob
from os.path import join
from pathlib import Path
import utilities as ut

# def measurements(folder):
#    measurements = pd.read_csv(join(folder, 'Measurements.txt'), delimiter='\t',
#                   skip_blank_lines=True, # to awoid reading
#                   header=5)               # the wrong header
#    # rename columns
#    measurements.columns = ['vcav', 'vcl', 'vcs', 'vml', 'vms', 'vfs', 'vfl','wmc',
#                            'wmm', 'wmf', 'ptot', 'wl', 'wl_side', 'pp', 'smsr']
#    return measurements

# def spectrum(filepath):
#    data = pd.read_csv(filepath, delimiter='\t',
#                   skip_blank_lines=False, # to awoid reading
#                   header=5)               # the wrong header
#    return data


def lecroy(file_path):
    """Load a recording from LeCroy oscilloscope into a Dataframe with v, t"""
    df = pd.read_csv(file_path, sep='\t',header=None, names=['v', 't'])
    return df


def folder(folder, filetype='df'):
    """Load a folder of text files
    
    Parameters
    ----------
    folder : string of pathlib Path
        full folder path that contains .txt files
    filetype : str
        ['df',]
    
    Returns
    -------
    Dict
        DataFrames, element coresponds to one file, with filename as key
    """
    folder = Path(folder)
    if filetype=='df':
        files = folder.glob('*.txt')
        return {f.stem: ut.df_read(f) for f in files}
    elif filetype=='ando':
        files = folder.glob('*.txt')
        return {f.stem: pd.read_csv(f, skiprows=6, names=['wl', 'p'], sep='\t')
                for f in files}
    elif filetype=='apex':
        files = folder.glob('*_Spectrum.txt')
        return{f.stem: pd.read_csv(f, skiprows=3, names=['wl','p'], sep='\t',
                                   index_col=False)
               for f in files}
    elif filetype=='lecroy':
        files = folder.glob('*.txt')
        return {f.stem: pd.read_csv(f, skiprows=5, names=['Time', 'Ampl'], sep='\t')
                for f in files}
    else:
        raise ValueError('Filetype property only takes certain values, '
                         'see documentation')
    

def spectrum(folder, index):
    """You should really write better documentation"""
    data = np.loadtxt(
        open(join(folder, 'Spectra\\Spectrum_%04d.txt' % index), "rb"),
        delimiter="\t",
        skiprows=6)
    return data[:,1], data[:,0]  # power, wavelength

mcol = pd.Series(data=np.arange(17), index=['vcav', 'vcl', 'vcs', 'vml',
                                            'vms', 'vfs', 'vfl','wmc',
                                            'wmm', 'wmf', 'ptot', 'wl',
                                            'wl_side', 'pp', 'smsr', 'i', 'gap'])


def measurements(folders):
    """You should really write better documentation"""
    if not isinstance(folders, list) :
        folders = [folders]
    res = []
    for folder in folders:
        meas = np.loadtxt(open(join(folder, 'Measurements.txt'), "rb"),
                          delimiter="\t", skiprows=10)
        if len(res) == 0:
            res = meas
        else:
            res = np.vstack([res, meas])
    # add index column
    res = np.c_[res, np.arange(0, res.shape[0])]
    return res


def file(filepath, filetype='ando-lv'):
    """Load measurement files: ando-lv, apex, lvv..."""
    switch = filetype.lower()
    if switch=='ando-lv':
        return pd.read_csv(filepath, skiprows=6, names=['wl', 'p'], sep='\t')
    elif switch=='apex':
        return pd.read_csv(filepath, skiprows=3, names=['wl','p'], sep='\t',
                           index_col=False)
    elif switch=='lecroy':
        return pd.read_csv(filepath, skiprows=5, names=['Time', 'Ampl'], sep='\t')
    elif switch=='lvv':
        return ut.df_read(filepath, column_names=['vset', 'vmeas', 'p'],
                          index_col=None, skip_rows=0)


def filepaths(folder, ends_in='*.txt', starts_with=None, contains=None):
    """Return full filepaths in folder that satisfy all specified conditions"""
    folder = Path(folder)
    if ends_in is None:
        ends_in = '*'
    filenames = [f.name for f in folder.glob(ends_in)]
    if starts_with is not None:
        filenames = [f for f in filenames if f.startswith(starts_with)]
    if contains is not None:
        filenames = [f for f in filenames if contains in f]
    return [folder/f for f in filenames]
