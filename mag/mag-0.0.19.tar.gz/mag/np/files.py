import numpy as np
from mag.py.files import linesplit
def from_delim(file:str, delim:str=',', dtype=None, newline='\n') -> list:
    '''Parses deliminated file into numpy array.

    Args:
    '''
    with open(file, 'r') as f:
        data = np.array([linesplit(line, delim, newline) for line in f])

    if dtype is not None:
        data = data.astype(dtype)
    return data

def from_npz(
    filename:str,
    n_records:int=None
    allow_pickle:bool=True,
    **kwargs
)->list:
    '''
    Notes:
        - NPZ loads data lazily, so it is efficient when just inspecting certain
            records, but less so when you want to map over all data.
    Arguments:
        filename (str): .npz file to load.
        n_records (int): Number of records to load. By default `None` which
            results in all data being loaded.
        allow_pickle (bool): whether or not to depickle saved objects.
        **kwargs: passed to `np.load`.
    Returns:
        results (list): list of all values from `filename`
    '''
    from sil import Sil
    print('NumPy lazy-loading index of saved data.')
    npz = np.load(file, allow_pickle=allow_pickle, **kwargs)
    print('Loading data from NPZ file into memory. This may take a while.')
    files = npz.files if n_records is None else npz.files[:n_records]
    results = []
    status = Sil(len(files), every=100, estimate_time=True)
    for file in files:
        results.append(npz[file])
        status.tick()
    npz.close() # <-- prevent data leak
    return np.array(results)
