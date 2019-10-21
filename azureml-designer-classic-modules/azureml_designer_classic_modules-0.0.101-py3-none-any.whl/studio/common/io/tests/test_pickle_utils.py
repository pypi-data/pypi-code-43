import os
import pickle
from argparse import Namespace

import pandas as pd
import pytest

from azureml.studio.package_info import __version__ as alghost_version
from azureml.studio.common.datatable.data_table import DataTable
from azureml.studio.core.utils.strutils import generate_random_string
from azureml.studio.common.io.pickle_utils import write_with_pickle, read_with_pickle_from_file, _ALGHOST_VERSION_ATTR


@pytest.fixture
def input_data_table_1():
    return DataTable(
        pd.DataFrame(
            columns=["A", "B"],
            data=[
                [0, 1],
                [2, 3],
                [4, 5],
                [6, 7]
            ]))


@pytest.fixture
def obj():
    obj = Namespace()
    obj.foo = 'foo'
    obj.bar = 'bar'
    return obj


def test_pickle_read_and_write(tmpdir, input_data_table_1):
    temp_file = generate_random_string()
    output_file_name = tmpdir.join(f"{temp_file}.pickle")
    write_with_pickle(input_data_table_1, output_file_name)
    output_data_table = read_with_pickle_from_file(output_file_name)
    assert output_data_table.data_frame.equals(input_data_table_1.data_frame)


def test_pickle_read_exception_file_not_found():
    dummy_file = "dummy_file"
    with pytest.raises(FileNotFoundError,
                       match=f"No such file or directory: '{dummy_file}'"):
        read_with_pickle_from_file(dummy_file)


def test_pickle_should_dumped_with_version(obj, tmpdir):
    file_name = os.path.join(tmpdir, 'obj.pickle')
    write_with_pickle(obj, file_name)

    r = read_with_pickle_from_file(file_name)
    assert getattr(r, 'foo') == 'foo'
    assert getattr(r, 'bar') == 'bar'
    assert getattr(r, _ALGHOST_VERSION_ATTR) == alghost_version


def test_pickle_read_non_versioned_pickle_with_version_check(obj, tmpdir, caplog):
    file_name = os.path.join(tmpdir, 'obj.pickle')

    with open(file_name, 'wb') as f:
        pickle.dump(obj, f, protocol=4)

    r = read_with_pickle_from_file(file_name, check_version=True)
    assert getattr(r, 'foo') == 'foo'
    assert getattr(r, 'bar') == 'bar'
    assert not hasattr(r, _ALGHOST_VERSION_ATTR)

    log = caplog.record_tuples
    assert len(log) == 1
    assert log[0][2].startswith('Version mismatch.')


def test_pickle_read_non_versioned_pickle_without_version_check(obj, tmpdir, caplog):
    file_name = os.path.join(tmpdir, 'obj.pickle')

    with open(file_name, 'wb') as f:
        pickle.dump(obj, f, protocol=4)

    r = read_with_pickle_from_file(file_name, check_version=False)
    assert getattr(r, 'foo') == 'foo'
    assert getattr(r, 'bar') == 'bar'
    assert not hasattr(r, _ALGHOST_VERSION_ATTR)

    log = caplog.record_tuples
    assert len(log) == 0


def test_pickle_read_old_versioned_pickle_with_version_check(obj, tmpdir, caplog):
    file_name = os.path.join(tmpdir, 'obj.pickle')

    with open(file_name, 'wb') as f:
        setattr(obj, _ALGHOST_VERSION_ATTR, "0.0.0")
        pickle.dump(obj, f, protocol=4)

    r = read_with_pickle_from_file(file_name, check_version=True)
    assert getattr(r, 'foo') == 'foo'
    assert getattr(r, 'bar') == 'bar'
    assert getattr(r, _ALGHOST_VERSION_ATTR) == "0.0.0"

    log = caplog.record_tuples
    assert len(log) == 1
    assert log[0][2].startswith('Version mismatch.')


def test_pickle_read_old_versioned_pickle_without_version_check(obj, tmpdir, caplog):
    file_name = os.path.join(tmpdir, 'obj.pickle')

    with open(file_name, 'wb') as f:
        setattr(obj, _ALGHOST_VERSION_ATTR, "0.0.0")
        pickle.dump(obj, f, protocol=4)

    r = read_with_pickle_from_file(file_name, check_version=False)
    assert getattr(r, 'foo') == 'foo'
    assert getattr(r, 'bar') == 'bar'
    assert getattr(r, _ALGHOST_VERSION_ATTR) == "0.0.0"

    log = caplog.record_tuples
    assert len(log) == 0


def test_pickle_read_correct_versioned_pickle_with_version_check(obj, tmpdir, caplog):
    file_name = os.path.join(tmpdir, 'obj.pickle')
    write_with_pickle(obj, file_name)

    r = read_with_pickle_from_file(file_name, check_version=True)
    assert getattr(r, 'foo') == 'foo'
    assert getattr(r, 'bar') == 'bar'
    assert getattr(r, _ALGHOST_VERSION_ATTR) == alghost_version

    log = caplog.record_tuples
    assert len(log) == 0


def test_pickle_read_correct_versioned_pickle_without_version_check(obj, tmpdir, caplog):
    file_name = os.path.join(tmpdir, 'obj.pickle')
    write_with_pickle(obj, file_name)

    r = read_with_pickle_from_file(file_name, check_version=False)
    assert getattr(r, 'foo') == 'foo'
    assert getattr(r, 'bar') == 'bar'
    assert getattr(r, _ALGHOST_VERSION_ATTR) == alghost_version

    log = caplog.record_tuples
    assert len(log) == 0
