# -*- coding: utf-8 -*-
"""
Created 2017/04/27
Last update 2019/09/11

@author: Markus Eisenbach, Ronny Stricker

Description:
Automatic download of GAPs dataset if not available on PC.
"""

from __future__ import print_function, absolute_import
import numpy as np
from .ftp_utils import download_dataset, _read_pkl
from .ftp_info import INFO_FILE_TEMPLATE, CHUNK_TEMPLATE
try:
    from pathlib import Path
except ImportError:
    from pathlib2 import Path  # python 2 backport


def download(
        login,
        output_dir,
        version=1,
        patchsize=64,
        issue='NORMvsDISTRESS',
        subsets=None,
        debug_outputs=False):
    """
    Downloads the GAPs dataset with the specified patch size and issue.
    Please provide a valid login.

    Parameters
    ----------
    login : str
        Please enter the login you have received by mail.
        Note that you required different logins for the different versions of the dataset.
    output_dir : str
        Specify the directory where the dataset should be stored.
        The download script will create different subdirs for the different versions and issues.
    version : int
        The requested version of the dataset. Possible values are [1, 2].
    patchsize : int
        The requested patch size.
    issue : str
        The requested issue of the dataset. The issues differ in terms of the number of classes.
    subsets : list of str
        Specify the desired subsets of the dataset.
        All available subsets will be downloaded if None is passed as argument.
    debug_outputs : bool
        Specifies if debug outputs are desired.

    """
    download_dataset(login, output_dir, version, patchsize, issue, subsets, debug_outputs)


def get_dataset_info(version=1,
                     patchsize=64,
                     issue='NORMvsDISTRESS',
                     subset='train',
                     datadir='/local/datasets/gaps'):
    """
    Get information dictionary for a single subset of the dataset.
    Please note that the specified dataset has to be downloaded first.

    Parameters
    ----------
    version : int
        The requested version of the dataset. Possible values are [1, 2].
    patchsize : int
        The requested patch size.
    issue : str
        The requested issue of the dataset. The issues differ in terms of the number of classes.
    subset : list of str
        Specify the desired subsets of the dataset.
        All available subsets will be downloaded if None is passed as argument.
    datadir : str
        Specify the directory where the dataset is located (provide the same dir used in the download function call).

    Returns
    -------
    dict
        Dictionary with dataset info.

    """

    # obtain dataset info
    dataset_path = Path(datadir) / 'v{}'.format(version) / '{}_{}'.format(issue, patchsize) / subset
    dataset_info_file = dataset_path / INFO_FILE_TEMPLATE.format(patchsize=str(patchsize),
                                                                 issue=issue,
                                                                 subset=subset)
    if not dataset_info_file.exists():
        msg = 'cannot find dataset info file!'
        msg2 = 'Please download the dataset first.'
        msg3 = 'See http://www.tu-ilmenau.de/neurob/data-sets-code/gaps/'
        raise IOError('[ERROR] {}\n       HINT: {}\n       HINT: {}'.format(msg, msg2, msg3))

    return _read_pkl(dataset_info_file)


def load_chunk(chunk_id,
               version=1,
               patchsize=64,
               issue='NORMvsDISTRESS',
               subset='train',
               datadir='/local/datasets/gaps'):
    """
    Get information dictionary for a single subset of the dataset.
    Please note that the specified dataset has to be downloaded first.

    Parameters
    ----------
    chunk_id : int
        The id of the desired chunk. E.g. 0, 1, 2, ...
    version : int
        The requested version of the dataset. Possible values are [1, 2].
    patchsize : int
        The requested patch size.
    issue : str
        The requested issue of the dataset. The issues differ in terms of the number of classes.
    subset : list of str
        Specify the desired subsets of the dataset.
        All available subsets will be downloaded if None is passed as argument.
    datadir : str
        Specify the directory where the dataset is located (provide the same dir used in the download function call).

    Returns
    -------
    (ndarray, ndarray)
        The first mat has four dimensions (sample, channel, y, x) and contains the patches.
        The second mat has one dimension and contains the target values for every single sample.

    """

    # obtain dataset info
    ds_info = get_dataset_info(version,
                               patchsize,
                               issue,
                               subset,
                               datadir)

    if chunk_id < 0 or chunk_id >= ds_info['n_chunks']:
        raise ValueError("Chunk with id {} not available. The total number of chunks is {}.".format(
            chunk_id,
            ds_info['n_chunks']))

    # continue extracting the chunk
    dataset_path = Path(datadir) / 'v{}'.format(version) / '{}_{}'.format(issue, patchsize) / subset
    x_file, y_file = (dataset_path / CHUNK_TEMPLATE.format(
        patchsize=str(patchsize),
        issue=issue,
        subset=subset,
        part_nr=str(chunk_id).zfill(ds_info['chunk_descriptor_digits']),
        data=data) for data in ['x', 'y'])
    try:
        return np.load(x_file), np.load(y_file)
    except IOError:
        print('[ERROR] Failed to load chunk {}'.format(chunk_id))
        raise
