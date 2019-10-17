import errno
import os
import pickle

from azureml.studio.package_info import __version__ as alghost_version
from azureml.studio.package_info import __package_name__ as alghost_package_name
from azureml.studio.core.logger import common_logger


_ALGHOST_VERSION_ATTR = '__alghost_version__'


def read_with_pickle_from_stream(stream, check_version=True):
    obj = pickle.load(stream)
    if check_version:
        version_in_pickle_file = getattr(obj, _ALGHOST_VERSION_ATTR, None)
        if version_in_pickle_file != alghost_version:
            common_logger.warning(f"Version mismatch. "
                                  f"Pickle file was dumped by {alghost_package_name} {version_in_pickle_file} "
                                  f"but currently is {alghost_version}.")
    return obj


def read_with_pickle_from_file(file_name, check_version=True):
    if not os.path.isfile(file_name):
        raise FileNotFoundError(
            errno.ENOENT,
            os.strerror(errno.ENOENT),
            file_name)

    with open(file_name, 'rb') as f:
        return read_with_pickle_from_stream(f, check_version)


def write_with_pickle(obj, file_name):
    with open(file_name, 'wb') as f:
        setattr(obj, _ALGHOST_VERSION_ATTR, alghost_version)
        pickle.dump(obj, f, protocol=4)
