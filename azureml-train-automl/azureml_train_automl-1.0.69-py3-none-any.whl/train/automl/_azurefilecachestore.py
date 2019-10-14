# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Cache store implementation that utilizes Azure files for backend storage."""
import logging
import os
import pickle
import time
from enum import Enum
from io import BytesIO
from typing import BinaryIO, Any, Dict, Tuple

import numpy as np
from azureml._vendor.azure_storage.file import FileService, models, ContentSettings
from scipy import sparse

from automl.client.core.common.activity_logger import DummyActivityLogger
from automl.client.core.runtime.cache_store import CacheStore, CacheException, _create_temp_dir, \
    DEFAULT_TASK_TIMEOUT_SECONDS, _try_remove_dir
from automl.client.core.runtime.pickler import DefaultPickler, DEFAULT_PICKLE_PROTOCOL_VERSION
from azureml import _async


class _SavedAsProtocol(Enum):
    PICKLE = 1
    NUMPY = 2
    SCIPY = 3


class AzureFileCacheStore(CacheStore):
    """Cache store based on azure file system."""

    NUMPY_FILE_EXTENSION = '.npy'
    SCIPY_SPARSE_FILE_EXTENSION = '.npz'

    def __init__(self,
                 path,
                 account_name=None,
                 account_key=None,
                 pickler=None,
                 task_timeout=DEFAULT_TASK_TIMEOUT_SECONDS,
                 module_logger=logging.getLogger(__name__),
                 temp_location=None,
                 file_service=None):
        """
        Cache based on azure file system.

        :param path: path of the store
        :param account_name: account name
        :param account_key: account key
        :param pickler: pickler, default is cPickler
        :param task_timeout: task timeout
        :param module_logger: logger
        :param temp_location: temporary location to store the files
        :param file_service: file service instance if provided
        """
        super(AzureFileCacheStore, self).__init__(module_logger=module_logger)

        if pickler is None:
            pickler = DefaultPickler()

        self.task_timeout = task_timeout
        self.pickler = pickler
        self.account_name = account_name
        self.account_key = account_key
        self.cache_items = dict()  # type: Dict[str, str]
        self._num_workers = os.cpu_count()
        self.module_logger = module_logger if module_logger is not None else logging.getLogger()
        self.temp_location = _create_temp_dir(temp_location)
        self.activity_prefix = "_AzureFileCacheStore"
        self.file_service = file_service if file_service is not None else \
            FileService(account_name=account_name, account_key=account_key)
        self.path = path.lower().replace('_', '-')
        self.file_service.create_share(self.path)
        self.saved_as = dict()  # type: Dict[str, _SavedAsProtocol]

    def __getstate__(self):
        return {'task_timeout': self.task_timeout,
                'pickler': self.pickler,
                'account_name': self.account_name,
                'account_key': self.account_key,
                'cache_items': self.cache_items,
                'num_workers': self._num_workers,
                'module_logger': None,
                'temp_location': self.temp_location,
                'activity_prefix': self.activity_prefix,
                'path': self.path,
                'max_retries': self.max_retries,
                'saved_as': self.saved_as}

    def __setstate__(self, state):
        self.path = state['path']
        self.pickler = state['pickler']
        self.account_name = state['account_name']
        self.account_key = state['account_key']
        self.cache_items = state['cache_items']
        self._num_workers = state['num_workers']
        self.module_logger = logging.getLogger()
        self.temp_location = _create_temp_dir()
        self.activity_prefix = state['activity_prefix']
        self.task_timeout = state['task_timeout']
        self.max_retries = state['max_retries']
        self.saved_as = state['saved_as']
        self.activity_logger = DummyActivityLogger()
        self.file_service = FileService(account_name=self.account_name, account_key=self.account_key)

    def add(self, keys, values):
        """Add to azure file store.

        :param keys: keys
        :param values: values
        """
        self.module_logger.info('Adding {} to Azure file store cache'.format(keys))
        with self.log_activity():
            try:
                for k, v in zip(keys, values):
                    self._function_with_retry(self._serialize_and_upload,
                                              self.max_retries, self.module_logger, k, v)
            except Exception as e:
                raise CacheException("Cache failure {}".format(e))

    def add_or_get(self, key, value):
        """
        Adds the key to the Azure File store. If it already exists, return the value.

        :param key:
        :param value:
        :return: deserialized object
        """
        val = self.cache_items.get(key, None)
        if val is None:
            self.add([key], [value])
            return {key: value}

        return self.get([key], None)

    def get(self, keys, default=None):
        """
        Get the deserialized object from azure file store

        :param default: default value
        :param keys: store key
        :return: deserialized object
        """
        self.module_logger.info('Getting {} from Azure file store cache'.format(keys))
        with self.log_activity():
            ret = dict()
            self.module_logger.debug("saved_as object: " + str(self.saved_as.keys()))
            self.module_logger.info("Currently available items in cache: " + str(self.cache_items.keys()))
            for key in keys:
                try:
                    ret[key] = self._function_with_retry(self._download_and_deserialize, self.max_retries,
                                                         self.module_logger, key)[key]
                except Exception as e:
                    self.module_logger.warning('Failed to retrieve key "{}" from cache: {}'.format(key, e))
                    ret[key] = default

        return ret

    def set(self, key, value):
        """
        Set values to store.

        :param key: key
        :param value: value
        """
        self.add([key], [value])

    def remove(self, key):
        """
        Remove from store.

        :param key: store key
        """
        with self.log_activity():
            self._remove(self.path, [key])

    def remove_all(self):
        """Remove all the file from cache."""
        with self.log_activity():
            self._remove(self.path, self.cache_items.keys())

    def load(self):
        """Load from azure file store."""
        with self.log_activity():
            self._function_with_retry(self._get_azure_file_lists,
                                      self.max_retries, self.module_logger, self.path)

    def unload(self):
        """Unload the cache."""
        try:
            self.file_service.delete_share(share_name=self.path)
        except Exception as e:
            self.module_logger.warning('Failed to delete share "{}", {}'.format(self.path, e))

        self.cache_items.clear()
        _try_remove_dir(self.temp_location)

    def _remove(self, path, files):
        worker_pool = _async.WorkerPool(max_workers=self._num_workers)
        tasks = []

        with _async.TaskQueue(worker_pool=worker_pool, _ident=__name__,
                              flush_timeout_seconds=self.task_timeout,
                              _parent_logger=self.module_logger) as tq:
            for file in files:
                tasks.append(tq.add(self._function_with_retry,
                                    self._remove_from_azure_file_store,
                                    self.max_retries,
                                    self.module_logger,
                                    path,
                                    file))

        for task in tasks:
            task.wait()
        worker_pool.shutdown()

    def _remove_from_azure_file_store(self, path, key):
        self.file_service.delete_file(path, directory_name=None, file_name=key)
        self.cache_items.pop(key)

    def _get_azure_file_lists(self, path):
        """
        Get list of files available from azure file store. similar to dir.

        :param path: path
        """
        self.module_logger.debug('Getting list of files in "{}" in Azure file store'.format(path))
        for dir_or_file in self.file_service.list_directories_and_files(share_name=path):
            if isinstance(dir_or_file, models.File):
                if dir_or_file.name != 'saved_as':
                    self.cache_items[dir_or_file.name] = dir_or_file.name
                else:
                    self._load_saved_as_object_from_file()

    def _try_remove_temp_file(self, path):
        self.module_logger.debug('Removing temp file "{}"'.format(path))
        try:
            os.remove(path)
        except OSError as e:
            self.module_logger.warning("failed to remove temp file {}".format(e))

    def _load_saved_as_object_from_file(self):
        self.module_logger.info("Loading the saved_as object")
        with BytesIO() as bio:
            self.file_service.get_file_to_stream(share_name=self.path,
                                                 directory_name=None,
                                                 file_name='saved_as',
                                                 stream=bio)
            bio.seek(0)
            self.saved_as = pickle.load(bio)
        self.module_logger.info("The saved_as object is: " + str(self.saved_as))

    def _persist_saved_as_file(self) -> None:
        self.module_logger.info("Saving the saved_as object: " + str(self.saved_as))
        bio = BytesIO()
        pickle.dump(self.saved_as, bio, protocol=DEFAULT_PICKLE_PROTOCOL_VERSION)
        size_in_bytes = bio.tell()
        bio.seek(0)
        self.file_service.create_file_from_stream(share_name=self.path,
                                                  file_name="saved_as",
                                                  directory_name=None,
                                                  content_settings=ContentSettings('application/x-binary'),
                                                  stream=bio,
                                                  count=size_in_bytes)
        self.module_logger.info("The saved_as object is: " + str(self.saved_as))

    def _generate_unique_file_names(self, key: str, extension: str = '') -> str:
        ts = time.time()
        process_id = os.getpid()
        filename = str(ts) + str(key) + str(process_id)
        if not extension:
            return filename
        return '.'.join([filename, str(extension)])

    def _get_binary_readable_file(self, filename: str) -> Tuple[BinaryIO, int]:
        size_in_bytes = os.path.getsize(filename)
        file_obj = open(filename, "rb")
        file_obj.seek(0)
        return file_obj, size_in_bytes

    def _serialize_numpy_ndarray(self, file_name: str, obj: np.ndarray) -> Tuple[BinaryIO, int]:
        assert isinstance(obj, np.ndarray)
        self.module_logger.debug('Numpy saving and uploading "{}" to cache'.format(file_name))
        upload_file_name = self._generate_unique_file_names(file_name, 'npy')
        np.save(upload_file_name, obj, allow_pickle=False)
        self.saved_as[file_name] = _SavedAsProtocol.NUMPY
        return self._get_binary_readable_file(upload_file_name)

    def _serialize_scipy_sparse_matrix(self, file_name: str, obj: Any) -> Tuple[BinaryIO, int]:
        assert sparse.issparse(obj)
        self.module_logger.debug('Scipy saving and uploading "{}" to cache'.format(file_name))
        upload_file_name = self._generate_unique_file_names(file_name, 'npz')
        sparse.save_npz(upload_file_name, obj)
        self.saved_as[file_name] = _SavedAsProtocol.SCIPY
        return self._get_binary_readable_file(upload_file_name)

    def _serialize_object_as_pickle(self, file_name: str, obj: Any) -> Tuple[BytesIO, int]:
        self.module_logger.debug('Pickling and uploading "{}" to cache'.format(file_name))
        self.saved_as[file_name] = _SavedAsProtocol.PICKLE
        bio = BytesIO()
        pickle.dump(obj, bio, protocol=DEFAULT_PICKLE_PROTOCOL_VERSION)
        size_in_bytes = bio.tell()
        bio.seek(0)
        return bio, size_in_bytes

    def _serialize_and_upload(self, file_name: str, obj: Any) -> None:
        with self.log_activity():
            file_or_bio_obj = None
            size_in_bytes = None
            if isinstance(obj, np.ndarray) and obj.dtype != np.object:
                file_or_bio_obj, size_in_bytes = self._serialize_numpy_ndarray(file_name, obj)
            elif sparse.issparse(obj):
                file_or_bio_obj, size_in_bytes = self._serialize_scipy_sparse_matrix(file_name, obj)
            else:
                file_or_bio_obj, size_in_bytes = self._serialize_object_as_pickle(file_name, obj)

            self.file_service.create_file_from_stream(share_name=self.path,
                                                      file_name=file_name,
                                                      directory_name=None,
                                                      content_settings=ContentSettings('application/x-binary'),
                                                      stream=file_or_bio_obj,
                                                      count=size_in_bytes)
            try:
                file_or_bio_obj.close()
                if isinstance(file_or_bio_obj, BinaryIO):
                    os.remove(file_or_bio_obj.name)
            except Exception as e:
                self.module_logger.warning("Failed to close the stream after serializing and uploading to AzureCache:"
                                           " {}".format(e))

            self.cache_items[file_name] = file_name
            self._persist_saved_as_file()

    def _deserialize_numpy_ndarray(self, file_name: str) -> Dict[str, np.ndarray]:
        self.module_logger.debug('Downloading and numpy unpacking "{}" from cache'.format(file_name))
        downloadable_file_name = self._generate_unique_file_names(file_name, self.NUMPY_FILE_EXTENSION)
        file_obj = open(downloadable_file_name, 'wb')
        self.file_service.get_file_to_stream(share_name=self.path,
                                             directory_name=None,
                                             file_name=file_name,
                                             stream=file_obj)
        file_obj.seek(0)
        return_dict = {file_name: np.load(downloadable_file_name, allow_pickle=False)}
        file_obj.close()
        os.remove(downloadable_file_name)
        return return_dict

    def _deserialize_scipy_sparse_matrix(self, file_name: str) -> Dict[str, Any]:
        self.module_logger.debug('Downloading and scipy unpacking "{}" from cache'.format(file_name))
        downloadable_file_name = self._generate_unique_file_names(file_name, self.SCIPY_SPARSE_FILE_EXTENSION)
        file_obj = open(downloadable_file_name, 'wb')
        self.file_service.get_file_to_stream(share_name=self.path,
                                             directory_name=None,
                                             file_name=file_name,
                                             stream=file_obj)
        file_obj.seek(0)
        return_dict = {file_name: sparse.load_npz(downloadable_file_name)}
        file_obj.close()
        os.remove(downloadable_file_name)
        return return_dict

    def _deserialize_object_as_pickle(self, file_name: str) -> Dict[str, Any]:
        self.module_logger.debug('Downloading and unpickling "{}" from cache'.format(file_name))
        bio = BytesIO()
        self.file_service.get_file_to_stream(share_name=self.path,
                                             directory_name=None,
                                             file_name=file_name,
                                             stream=bio)
        bio.seek(0)
        return_dict = {file_name: pickle.load(bio)}
        bio.close()
        return return_dict

    def _download_and_deserialize(self, file_name: str) -> Dict[str, Any]:
        self.cache_items[file_name] = file_name
        saved_as = self.saved_as.get(file_name, None)
        if saved_as == _SavedAsProtocol.SCIPY:
            return self._deserialize_scipy_sparse_matrix(file_name)
        elif saved_as == _SavedAsProtocol.NUMPY:
            return self._deserialize_numpy_ndarray(file_name)
        else:
            return self._deserialize_object_as_pickle(file_name)
