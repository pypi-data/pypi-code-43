# -*- coding: utf-8 -*-
"""
Created on Tuesday 24-July-2018 at 17:20

@author: Rastko Pajković
"""

from datetime import datetime
import re
import numpy as np
from pathlib import Path
import pandas as pd
import time
import shutil
# from findpeaks import detect_peaks
from scipy import fftpack
import visa
import random
from itertools import takewhile
from scipy.constants import c

meas = Path('D:/Dropbox/PhD - ITL for SS-OCT/Measurements')
weekly = Path('D:/Dropbox/PhD - ITL for SS-OCT/Presentations/Weekly meetings')


class Dotdict(dict):
    """dot.notation access to dictionary attributes

    from derec73 on stackoverflow
    https://stackoverflow.com/questions/2352181/
    how-to-use-a-dot-to-access-members-of-dictionary
    """

    __getattr__ = dict.get
    __setattr__ = dict.__setitem__
    __delattr__ = dict.__delitem__


def df_init(columns, numel=0, units=None):
    """Initialize an empty DataFrame"""
    df = pd.DataFrame(index=range(numel), columns=columns)
    if units is not None:
        units = pd.DataFrame(data={c:units[i] for i,c in enumerate(columns)},
                             index=['#units'])
        df = pd.concat((units, df))
    return df


# ----- TIME -------------------------------------------------------------------
def ts2dt(ts, t0=None):
    """Convert timestamps to Δt in seconds, if t0 is None t0=ts[0]"""
    # define t0 if not given
    if t0 is None:
        t0 = ts[0]
    # convert to datetime if the format is string
    if isinstance(t0, str):
        ts = [datetime.strptime(t, '%Y-%m-%d %H:%M:%S.%f') for t in ts]
        t0 = ts[0]
    return [(t-t0).total_seconds() for t in ts]


def str2dt(string, form='%Y-%m-%d %H:%M:%S.%f'):
    """Convert a datetime string into a datetime object"""
    return datetime.strptime(string, form)


def get_time(form='dt'):
    """Generate a timestamp, form='str' for string
    
    Parameters
    ----------
    form : str
        'str' - return string date yyyy-mm-dd hh:mm:ss.microseconds,
        'dt' - return datetime object
    """
    form = form.lower()
    if form=='str':
        return datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')
    elif form=='dt':
        return datetime.now()


def get_date(form='str'):
    """Generate a date-stamp
    
    Parameters
    ----------
    form : str
        'str'  - return string 'YYYY-MM-DD ',
        'str2' - return string 'Day DD-MM-YYYY',
        'dt'   - return datetime object
    """
    form = form.lower()
    if form=='str':
        return datetime.today().strftime('%Y-%m-%d ')  # 1992-02-22
    elif form=='str2':
        return datetime.today().strftime('%A %d.%m.%Y')
    elif form=='dt':
        return datetime.today().date()


def elapsed_since(t0):
    """Calculate the elapsed time in seconds down to microseconds"""
    return (get_time('dt')-t0).total_seconds()


def now():
    """Return current DateTime with microsecond precision"""
    return datetime.now()


def wait_s(sec):
    """Wait sec seconds"""
    time.sleep(sec)
# ------------------------------------------------------------------------------


def to_iterable(anything):
    """Convert anything to an iterable"""
    if isinstance(anything, str):
        return [anything]
    elif hasattr(anything, "__iter__"):
        return anything
    else:
        try:
            return list(anything)
        except TypeError:
            return [anything]


def list_connected_gpibs(id=False, query='GPIB?*::INSTR'):
    """Print which GPIB addresses are currently connected"""
    rm = visa.ResourceManager()
    gpibs = rm.list_resources(query=query)
    if id:
        for gpib in gpibs:
            inst = rm.open_resource(gpib)
            print(gpib + ' - {}'.format(inst.query("*IDN?")))
            inst.close()
        return
    return gpibs


def parse_floats(string, iterable=False):
    """Turn a string of floats into a numpy array, a scalar or None"""
    re_float = r"[-+]?(?:\d+(?:\.\d*)?|\.\d+)(?:[eE][-+]?\d+)?"
    float_string = re.findall(re_float, string)
    if iterable:
        return [float(el) for el in float_string]
    if len(float_string) == 1:
        return float(float_string[0])
    elif len(float_string) == 0:
        return None
    return np.array([float(str) for str in float_string])


def find_num_in_string(string, before=None, after=None):
    """Find a float in the string imediately after of before a substring"""
    if before is not None:
        parts = string.split(before)
        if len(parts)!=2:
            raise ValueError('String {} apears 0 or >1 times in {}.'.format(before, string))
        floats = parse_floats(parts[0], iterable=True)
        return floats[-1]
    if after is not None:
        parts = string.split(after)
        if len(parts)!=2:
            raise ValueError('String {} apears 0 or >1 times in {}.'.format(after, string))
        floats = parse_floats(parts[1], iterable=True)
        return floats[0]


def make_fold(name,
              date=True,
              root='measurements'):
    """Make the folder root/name and return the Path"""
    if date:
        name = get_date(form='str') + str(name)
    if root=='measurements':
        root=Path('D:/Dropbox/PhD - ITL for SS-OCT/Measurements')
    elif root=='apex-shared':
        root = Path('D:/Apex spectra')
    else:
        root = Path(root)
    dest = root/name
    dest.mkdir(mode=0o777, parents=True, exist_ok=True)
    return dest


def get_fold(date=None,
             name=None,
             root='D:/Dropbox/PhD - ITL for SS-OCT/Measurements',
             verbose=False):
    """Get full paths to the first folder that matches the date and name"""
    root = Path(root)
    if date is None:
        date = get_date()
    if name is None:
        name = ''
    else:
        name = '*' + name
    pattern = '{}{}*'.format(date, name)
    if verbose:
        print(pattern, list(root.glob(pattern)))
    return list(root.glob(pattern))[0]


def df_read(filepath, column_names=None, index_col=0, skip_rows=0, **kwargs):
    """Read a DataFrame from a file, skip lines that start with #"""
    if column_names is not None:
        skip_rows += 1
    res = pd.read_csv(filepath,
                      sep='\t',
                      names=column_names,
                      skiprows=skip_rows,
                      index_col=index_col,
                      comment='#',
                      **kwargs)
    # try:
    #     res = res.drop('units')
    # except ValueError:
    #     pass  # there was no units index
    try:
        res['ts'] = pd.to_datetime(res['ts'])
    except:
        pass
    return res


def df_read_hd(filepath, hd_item=None, item_type='num'):
    """Read the header (sarts with '# ') of a text file and return as dict
    
    Parameters
    ----------
    filepath : string or Path
        Full filepath to the csv dataframe
    hd_item : str
        Name of the item from header to fetch, if None return all
    item_type : str
        Type of item: 'num',' str', 'datetime'
    """
    with open(filepath, 'r', encoding='utf-8') as fobj:
        # takewhile returns an iterator over all the lines
        # that start with the comment string
        headiter = takewhile(lambda s: s.startswith('# '), fobj)
        # you may want to process the headers differently,
        # but here we just convert it to a list
        lines = [l[2:-1].split(': ') for l in headiter]
        header_dict = dict(lines)
        if hd_item is not None:
            item_str = header_dict[hd_item]
            if item_type=='str':
                return item_str
            elif item_type=='num':
                return parse_floats(item_str, iterable=False)
            elif item_type=='datetime':
                return datetime.strptime(item_str,'%Y-%m-%d %H:%M:%S.%f')
        return Dotdict(header_dict)


def df_write(df, filepath, overwrite=False,
             header={
                 'Measured_by':'',
                 'Chip':'',
                 'Temperature':'',
                 'Equipment':'',
                 'ParameterX':''
             },
             **kwargs):
    """Write a dataframe to a tab delimited .txt file"""
    # check if the file already exists and ask what to do
    filepath = Path(filepath)
    if filepath.is_file() and not overwrite:
        answer = input('File {} already exists, overwrite? [y/(n)]:\n'.format(filepath.name))
        if answer.lower() != 'y':
            return
    try:
        h = ''
        l_key_max = max([len(k) for k in header.keys()])
        for k, v in header.items():
            h+=('# {:<'+str(l_key_max+1)+'} {}\n').format(k+':', v)
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(h)
            df.to_csv(f, sep='\t', encoding='utf-8', **kwargs)
    except:
        df.to_csv(filepath, sep='\t', **kwargs)


def make_dated_pyfile(name, dest=None):
    """Make an empty 'YYYY-MM-DD name.py' file in the destination

    Parameters
    -----------
    dest : str
        takes ['plot', 'man'] of fullfolderpath
    name : str
        name that follows tha date
    """
    if (dest is None) or dest=='man':
        dest = Path('D:/Dropbox/PhD - ITL for SS-OCT/Python/'
                    'Measurement analysis')
    elif dest=='plot':
        dest = Path('D:/Dropbox/PhD - ITL for SS-OCT/Python/Plots')
    else:
        dest = Path(dest)
    filename = dest/'{}{}.py'.format(get_date(),name)
    with open(filename, 'w'):
        pass
    return filename


def move_files(from_folder, to_folder, pattern='*.txt', mode='move'):
    """Move files from on folder to another if they match pattern
    
    Parameters
    ----------
    from_folder : str or pathlib Path
        Source folder containing files to be moved
    to_folder : str or pathlib Path
        Destination folder, will be created if doesn't exist
    pattern : str
        Only files that match the pattern in the source folder will be moved
    mode : str
        Mode of moving the files: ['move', 'copy']
    """
    from_folder = Path(from_folder)
    to_folder = Path(to_folder)
    to_folder.mkdir(mode=0o777, parents=True, exist_ok=True)

    if not (from_folder.is_dir() & to_folder.is_dir()):
        raise ValueError('from_folder and to_folder need to be directory paths')
    files = list(from_folder.glob(pattern))
    if mode=='move':
        for f in files:
            shutil.move(str(f), to_folder)
    elif mode=='copy':
        for f in files:
            shutil.copy2(str(f), to_folder)
    else:
        allowed_modes = ['move', 'copy']
        raise ValueError('Allowed modes are {}'.format(allowed_modes))


def fft(y, dt):
    """Perform fast Fourier transform and return freq, y"""
    y = fftpack.fft(y)
    f = fftpack.fftfreq(len(y), d=dt)
    # shift to plot nicely
    y = fftpack.fftshift(y, axes=None)
    f = fftpack.fftshift(f, axes=None)
    return f, y


def bracket(step_numel, center=None, max_val=None, min_val=None,
            start_at_center=False):
    """Generate an array around center with steps of different sizes
    
    Parameters
    ----------
    step_numel : list of lists
        [[step1, number_of_steps1], [step2, number_of_steps2], ...]
    center : float
        Central value around which to bracket, if None return offset
    max_val : float
        Minimal acceptable return value, values lower than this are removed
    min_val : float
        Maximal acceptable return value, values higher than this are removed
    start_at_center : bool
        If True return [center, positive_offset, center, negative_offset]
    Example:
    ---------
    bracket(10, [[0.5, 2], [1, 4]], min_val=8) gives
        [8, 9, 9.5, 10, 10.5, 11, 12, 13, 14, 15]
    
    Returns
    -------
    numpy.array
        Resulting array
    """
    if center is None:
        center = 0
    offset = []
    for step, numel in step_numel:
        start = step if not offset else offset[-1]+step
        offset += [start+i*step for i in range(numel)]
    if start_at_center:
        offset = [0] + offset + [0] + [-el for el in offset]
    else:
        offset = [-el for el in offset[::-1]] + [0] + offset
    offset = np.array(offset)
    res = center + offset
    if min_val is not None:
        res = res[res>=min_val]
    if max_val is not None:
        res = res[res<=max_val]
    return res


def rand(low, high, numel=1):
    """Generate numel random floats between low and high"""
    if numel == 1:
        return random.uniform(low,high)
    else:
        return [random.uniform(low, high) for _ in range(numel)]

# ----- ARRAYS -----------------------------------------------------------------


def array(start=0, step=1, stop=10, numel=None):
    """Generate an equidistand vector of values
    
    Parameters
    ----------
    start : float
        Starting value, included in output
    step : float
        Step, if numel is defined it overrides step
    stop : float
        Last value, included in output
    numel : int
        Number of elements, overrides step
    """
    if start>stop:
        step = -np.abs(step)
    else:
        step = np.abs(step)
    if numel is None:
        return np.arange(start, stop+step*0.1, step)
    else:
        return np.linspace(start, stop, num=numel, endpoint=True)


def df_find_closest_ind(pd_series, target):
    """Return the first index of an array element closest to target"""
    pd_series = pd.Series(pd_series)
    return (pd_series-target).abs().argsort().iloc[0]


def find_closest_ind(array, target):
    """Return the first index of an array element closest to target"""
    pd_series = pd.Series(array)
    return (pd_series-target).abs().argsort().iloc[0]


def fing_max_ind(array):
    """Return the index of the maximum"""
    return find_closest_ind(array, max(array))


def find_closest(array, target):
    """Return the array element closest to target"""
    pd_series = pd.Series(array)
    return array[(pd_series-target).abs().argsort().iloc[0]]

# ----- CONVERSION -------------------------------------------------------------


def dbm2mw(dbm):
    """Convert dBm power to mW"""
    if isinstance(dbm, (float,int)):
        return 10**(dbm/10)
    if len(dbm)>1:
        dbm = np.array(dbm)
    return 10**(dbm/10)



def mw2dbm(mw):
    """Convert mW power to dBm"""
    if isinstance(mw, (float,int)):
        return 10*np.log10(mw)
    if len(mw)>1:
        mw = np.array(mw)
    return 10*np.log10(mw)


def idens2i(idens_kA_cm2, l_um, w_um=2):
    """Convert current density in kA/cm2 to current in mA"""
    return idens_kA_cm2*l_um*w_um/1e2


def i2idens(i, l_um, w_um=2):
    """Convert current in mA to current density in kA/cm2"""
    return i/l_um/w_um*1e2


def dl2df(dl_um, wl_nm=1530, ng=3.67, answer='nm'):
    """Convert a linear cavity length into answer units, 'nm' or 'GHz'"""
    df = c/(2*dl_um*ng)/1e3
    if answer=='nm':
        return df*wl_nm**2/c
    elif answer=='ghz':
        return df


def df2dlambda(df_ghz, wl_nm=1530):
    """Convert FSR in GHz to FSR in nm"""
    f_ghz = c/wl_nm
    return c*df_ghz/f_ghz**2


def dlambda2df(dlambda_nm, wl_nm=1530):
    """Convert FSR in nm to FSR in GHz"""
    return c*dlambda_nm/wl_nm**2


def g2G(g,l):
    """Convert gain [cm-1] to gain in dB, l in μm"""
    l = l/1e4  # convert μm to cm
    return mw2dbm(np.exp(g*l))


def G2g(G,l):
    """Convert gain in dB to gain in cm-1, l in μm"""
    l = l/1e4  # convert μm to cm
    return np.log(dbm2mw(G))/l
