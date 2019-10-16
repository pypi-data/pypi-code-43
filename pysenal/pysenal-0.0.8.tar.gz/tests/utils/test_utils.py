# -*- coding: UTF-8 -*-
import shutil
import tempfile
from types import GeneratorType
from decimal import Decimal
import pytest
from pysenal.utils.utils import *


def test_get_chunk():
    r1 = range(100)
    chunk_r1 = get_chunk(r1, 12)
    assert type(chunk_r1) == GeneratorType
    assert next(chunk_r1) == range(12)

    l1 = [1, 3, 5, 7, 9]
    chunk_l1 = get_chunk(l1, 5)
    assert next(chunk_l1) == l1
    with pytest.raises(StopIteration):
        next(chunk_l1)

    chunk_l1 = get_chunk(l1, 10)
    assert next(chunk_l1) == l1

    g1 = (i for i in [1, 10, 100, 3, 4, 'a'])
    chunk_g1 = get_chunk(g1, 2)
    assert type(chunk_g1) == GeneratorType
    assert next(chunk_g1) == [1, 10]
    assert next(chunk_g1) == [100, 3]

    g2 = (i for i in [20, 100, 40, 123])
    chunk_g2 = get_chunk(g2, 3)
    assert next(chunk_g2) == [20, 100, 40]
    assert next(chunk_g2) == [123]

    g3 = (i for i in [10, 100, 200])
    chunk_g3 = get_chunk(g3, 5)
    assert next(chunk_g3, [10, 100, 200])
    with pytest.raises(StopIteration):
        next(chunk_g3)


def test_list2dict():
    l1 = [{'pid': '1', 'title': 'haha'}, {'pid': '2', 'title': 'lalala'}]
    expected_l1 = {'1': {'pid': '1', 'title': 'haha'}, '2': {'pid': '2', 'title': 'lalala'}}
    ret_l1 = list2dict(l1, 'pid')
    l1[0]['pid'] = '11'
    l1[1]['pid'] = '22'

    assert ret_l1 == expected_l1
    with pytest.raises(KeyError):
        list2dict(l1, 'patent_id')
    l1.append(1)
    with pytest.raises(TypeError):
        list2dict(l1, 'pid')

    l2 = [{'name': 'a', 'count': 11}, {'name': 'b', 'count': 2}]
    expected_l2 = {'a': {'count': 11}, 'b': {'count': 2}}
    assert list2dict(l2, 'name', pop_key=True) == expected_l2
    with pytest.raises(TypeError):
        list2dict(1, 'pid')


@pytest.fixture()
def get_filename_dirname():
    base_dirname = tempfile.gettempdir() + '/'
    dirname = base_dirname + 'pysenal_test_utils_get_filename/'
    return dirname


@pytest.fixture()
def get_filename_dir_setup(get_filename_dirname):
    dirname = get_filename_dirname
    if os.path.exists(dirname):
        shutil.rmtree(dirname)
    os.mkdir(dirname)
    os.mkdir(dirname + 'dir1')
    os.mkdir(dirname + 'dir2')
    open(dirname + 'file1', 'a').close()
    open(dirname + 'file2.bak', 'a').close()
    open(dirname + 'file2.bak', 'a').close()
    open(dirname + '.file3', 'a').close()
    open(dirname + '.file4.txt', 'a').close()


def test_get_filename_in_dir(get_filename_dir_setup, get_filename_dirname):
    dirname = get_filename_dirname
    expected_ret1 = [dirname + 'file1', dirname + 'file2.bak']
    assert get_filenames_in_dir(dirname) == expected_ret1

    expected_ret2 = [dirname + 'file1', dirname + 'file2']
    assert get_filenames_in_dir(dirname, rm_extname=True) == expected_ret2

    assert get_filenames_in_dir(dirname, rm_extname=True, rm_dirname=True) == ['file1', 'file2']

    ret3 = get_filenames_in_dir(dirname, rm_extname=True, skip_hidden_file=False)
    expected_ret3 = [dirname + '.file3', dirname + '.file4', dirname + 'file1', dirname + 'file2']
    assert ret3 == expected_ret3


def test_index():
    values = [1, 2, 3, 4, 5]
    assert index(values, 2) == 1
    assert index(values, 6) == -1
    assert index(values, 6, default=100) == 100
    with pytest.raises(TypeError):
        index(10, 10)

    assert index('This is an example', 'example') == 11
    assert index(('a', 'b', 'c'), 'b') == 1


def test_json_serialize():
    assert json_serialize(Decimal('3.1415926')) == '3.1415926'
    assert json_serialize(Decimal('11.0')) == '11.0'
    assert json_serialize(b'123') == "b'123'"
    assert json_serialize(11) == '11'
