import os
import pytest

from azureml.studio.common.error import InvalidZipFileError
from azureml.studio.core.utils.fileutils import ensure_folder
from azureml.studio.common.zip_wrapper import ZipFileWrapper
from azureml.studio.core.utils.strutils import generate_random_string


@pytest.fixture
def zip_file_path():
    return os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        'input',
        'data.zip'
    )


@pytest.fixture
def extract_to_path():
    target_dir = os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        'gen',
    )
    ensure_folder(target_dir)
    return target_dir


@pytest.fixture
def not_zip_file_path():
    return os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        'input',
        'data.pickle'
    )


"""
Test class ZipFileWrapper
"""


def test_init(zip_file_path):
    assert ZipFileWrapper(file_path=zip_file_path)


def test_init_file_not_exist_error(zip_file_path):
    wrong_path = zip_file_path.replace('data.zip', 'data_not_exist.zip')
    with pytest.raises(FileNotFoundError, match=r"File: .* does not exist."):
        ZipFileWrapper(wrong_path)


def test_extractall(zip_file_path, extract_to_path):
    zip_file_wrapper = ZipFileWrapper(zip_file_path)
    zip_file_wrapper.extractall(extract_to_path)


def test_extractall_dir_not_exist_error(zip_file_path, extract_to_path):
    zip_file_wrapper = ZipFileWrapper(zip_file_path)
    wrong_path = zip_file_path.replace('gen', 'dir_not_exist')
    with pytest.raises(NotADirectoryError, match=r"Directory: .* does not exist."):
        zip_file_wrapper.extractall(wrong_path)


def test_extractall_invalid_zip_file_error(not_zip_file_path, extract_to_path):
    zip_file_wrapper = ZipFileWrapper(not_zip_file_path)
    with pytest.raises(InvalidZipFileError, match="Given ZIP file is not in the correct format."):
        zip_file_wrapper.extractall(extract_to_path)


def test_invalid_zip_file_error(tmpdir):
    file_name = generate_random_string()
    full_path = os.path.join(tmpdir, file_name)
    with open(full_path, 'w') as f:
        f.write("illegal zip file")

    with pytest.raises(InvalidZipFileError, match='Given ZIP file is not in the correct format'):
        zip_file_wrapper = ZipFileWrapper(full_path)
        zip_file_wrapper.extractall(target_dir=tmpdir)
