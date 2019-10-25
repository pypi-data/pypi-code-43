import os
import glob
import uuid
import shutil
import tempfile
import contextlib

from typing import Any, Optional, List

import numpy as np
import pandas as pd
from dask.dataframe.core import DataFrame

from statsmodels.sandbox.stats.multicomp import multipletests

import nbformat
from nbconvert.preprocessors import ExecutePreprocessor


def execute_notebook(
    nb_path: str,
    timeout: int = -1, version: int = 4,
    cwd: Optional[str] = None,
    allow_errors: bool = False, inplace: bool = False
) -> None:
    # read notebook
    with open(nb_path) as fd:
        nb = nbformat.read(fd, as_version=version)

    # set module import path
    nb['cells'].insert(0, nbformat.v4.new_code_cell(
        f'import sys; sys.path.insert(0, "{os.path.dirname(nb_path)}")'))

    # execute notebook
    ep = ExecutePreprocessor(timeout=timeout, allow_errors=allow_errors)

    try:
        ep.preprocess(nb, {'metadata': {'path': cwd}})
    except BaseException:
        raise
    finally:
        # save if needed
        if inplace:
            nb['cells'].pop(0)  # remove artificial cell

            with open(nb_path, 'w') as fd:
                nbformat.write(nb, fd)


def to_single_csv(
    ddf: DataFrame, fname: str,
    **kwargs: Any
) -> None:
    """Save dask dataframe to single CSV file."""
    tempdir = os.path.join(tempfile.gettempdir(), f'csv_merge.{uuid.uuid4()}')
    os.makedirs(tempdir)

    # save dask dataframe in multiple chunks
    target_files = os.path.join(tempdir, 'tmp.*.csv')
    ddf.to_csv(target_files, header_first_partition_only=True, **kwargs)

    # merge chunks into single file
    filenames = sorted(glob.glob(target_files))
    with open(fname, 'w') as fd_out:
        for fn in filenames:
            with open(fn) as fd_in:
                fd_out.write(fd_in.read())

    shutil.rmtree(tempdir)


def disable_truncate_view() -> None:
    """Enable printing of whole pandas dataframes."""
    # pd.describe_option('display')
    pd.set_option('display.max_columns', None)
    pd.set_option('display.max_rows', None)
    pd.set_option('display.max_colwidth', -1)


@contextlib.contextmanager
def chdir(dir_: str):
    """Temporarily switch directories."""
    curdir = os.getcwd()
    os.chdir(dir_)
    try:
        yield
    finally:
        os.chdir(curdir)


def multipletests_nan(pval_list: List, method: str = 'fdr_bh') -> List:
    """Multiple testing correction on lists with NaNs."""
    pval_list = np.asarray(pval_list)

    nan_idx, = np.where(np.isnan(pval_list))
    pval_list_nonan = pval_list[~np.isnan(pval_list)]

    if len(pval_list_nonan) == 0:
        assert np.isnan(pval_list).all()  # contains only np.nan
        pval_corr = pval_list
    else:
        _, pval_corr, _, _ = multipletests(pval_list_nonan, method=method)
        for i in nan_idx:
            pval_corr = np.insert(pval_corr, i, np.nan)

    return pval_corr
