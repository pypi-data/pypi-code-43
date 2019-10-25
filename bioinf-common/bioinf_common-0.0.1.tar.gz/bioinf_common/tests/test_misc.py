import os

import numpy as np
import pandas as pd
import nbformat as nbf
import dask.dataframe as dd

import pytest
from pandas.util.testing import assert_frame_equal

from ..tools import execute_notebook, to_single_csv, chdir, multipletests_nan


@pytest.fixture
def notebook(tmpdir):
    # create notebook
    nb = nbf.v4.new_notebook()

    code = f"""\
        !echo foo > {tmpdir}/fubar.txt
    """
    nb['cells'] = [nbf.v4.new_code_cell(code)]

    # save notebook
    fname = os.path.join(tmpdir, 'test_notebook.ipynb')
    with open(fname, 'w') as f:
        nbf.write(nb, f)

    return fname

def test_notebook_execution(notebook):
    execute_notebook(notebook)

    fname = os.path.join(os.path.dirname(notebook), 'fubar.txt')
    assert os.path.isfile(fname)

    with open(fname) as fd:
        assert fd.read() == 'foo\n'

def test_notebook_execution_inplace(notebook):
    with open(notebook) as fd:
        nb_pre = nbf.read(fd, as_version=4)

    execute_notebook(notebook, inplace=True)

    with open(notebook) as fd:
        nb_post = nbf.read(fd, as_version=4)

    # assert that no cells were added
    assert len(nb_pre['cells']) == len(nb_post['cells'])

def test_to_single_csv(tmpdir):
    fname = os.path.join(tmpdir, 'result.csv')

    ddf = dd.from_pandas(pd.DataFrame({
        'A': np.random.normal(size=1000),
        'B': np.random.choice(['a', 'b', 'c'], size=1000)
    }), npartitions=10)

    to_single_csv(ddf, fname, index=False)
    assert_frame_equal(ddf.compute(), pd.read_csv(fname))

def test_chdir(tmpdir):
    newdir = os.path.join(tmpdir, 'another')
    os.mkdir(newdir)

    beforedir = os.getcwd()
    with chdir(newdir):
        duringdir = os.getcwd()
    afterdir = os.getcwd()

    assert beforedir == afterdir
    assert duringdir == newdir

def test_multipletests_nan():
    mt = lambda x: multipletests_nan(x).tolist()

    np.testing.assert_array_equal(mt([np.nan, np.nan, np.nan]), [np.nan, np.nan, np.nan])

    np.testing.assert_array_equal(mt([.1, np.nan, np.nan]), [.1, np.nan, np.nan])
    np.testing.assert_array_equal(mt([np.nan, .1, np.nan]), [np.nan, .1, np.nan])
    np.testing.assert_array_equal(mt([np.nan, np.nan, .1]), [np.nan, np.nan, .1])

    np.testing.assert_allclose(mt([.8, np.nan, .5, np.nan, .1]), [0.8, np.nan, 0.75, np.nan, 0.3])
