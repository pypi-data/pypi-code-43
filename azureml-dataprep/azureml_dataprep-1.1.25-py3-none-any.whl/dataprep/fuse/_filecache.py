from ._stat import update_stat
from azureml.dataprep import ExecutionError
from azureml.dataprep.api._loggerfactory import _LoggerFactory
from azureml.dataprep.native import StreamInfo
from collections import OrderedDict
from errno import EFBIG, ENOENT
from fuse import FuseOSError
import io
import os
import shutil
import sys
import threading
from typing import Callable, BinaryIO, Union
import uuid


log = _LoggerFactory.get_logger('dprep.fuse.filecache')


class _FileOps:
    def __init__(self,
                 makedirs: Callable[[str], None],
                 rmtree: Callable[[str], None],
                 rm: Callable[[str], None],
                 stat: Callable[[str], os.stat_result],
                 open_file: Callable[[str], BinaryIO],
                 get_free_space: Callable[[str], int]):
        self.makedirs = makedirs
        self.rmtree = rmtree
        self.rm = rm
        self.stat = stat
        self.open = open_file
        self.get_free_space = get_free_space


def _get_free_space(path: str) -> int:
    statvfs = os.statvfs(path)
    return statvfs.f_frsize * statvfs.f_bavail


_standard_file_ops = _FileOps(os.makedirs,
                              lambda p: shutil.rmtree(p, ignore_errors=True),
                              os.remove,
                              os.stat,
                              lambda p: io.open(p, mode='rb'),
                              _get_free_space)


class _CacheEntry:
    def __init__(self,
                 path: str,
                 download_path: str,
                 attributes: os.stat_result):
        self.path = path
        self.download_path = download_path
        self.attributes = attributes


class FileCache:
    def __init__(self,
                 data_dir: str,
                 allowed_size: int,
                 required_free_space: int,
                 download_path: Callable[[StreamInfo, str], int],
                 get_handle: Callable[[], int],
                 file_ops: _FileOps = _standard_file_ops):
        self._next_handle = 0
        self._entries = OrderedDict()
        self._open_paths = {}
        self._streams = {}
        self._downloads_in_progress = {}
        self._total_size = 0

        cache_id = str(uuid.uuid4())
        self.data_dir = os.path.join(data_dir, cache_id)

        self._allowed_size = allowed_size
        self._required_free_space = required_free_space
        self._download_path = download_path
        self._get_handle = get_handle

        self._file_ops = file_ops
        self._file_ops.makedirs(self.data_dir)

    def clear(self):
        self._file_ops.rmtree(self.data_dir)

    def get_attributes(self, path: str) -> os.stat_result:
        entry = self._entries[path]
        log.debug('Returning attributes from cache: %s', entry.attributes)
        return entry.attributes

    def _remove_entry(self, entry: _CacheEntry):
        log.debug('Removing entry from cache: %s', entry.path)
        self._file_ops.rm(entry.download_path)
        self._total_size -= entry.attributes.st_size
        self._entries.pop(entry.path)

    def _ensure_enough_space(self, size: int, free_space: int) -> int:
        log.debug('Ensuring file fits in cache.')
        if size > self._allowed_size:
            log.info('Attempting to cache file larger than max allowed size.')
            raise FuseOSError(EFBIG)

        if free_space + self._total_size - size < self._required_free_space:
            log.debug('Attempting to cache file that does not fit in the specified volume.')
            raise FuseOSError(EFBIG)

        while free_space - size < self._required_free_space or size + self._total_size > self._allowed_size:
            if len(self._entries) == 0:
                log.debug('Unable to clear sufficient space from the cache to fit file.')
                raise FuseOSError(EFBIG)

            entry_path, entry_to_remove = \
                next((item for item in self._entries.items() if item[1].path not in self._open_paths), (None, None))
            if entry_to_remove is None:
                log.debug('Unable to clear sufficient space from the cache to fit file.')
                raise FuseOSError(EFBIG)

            self._remove_entry(entry_to_remove)
            free_space += entry_to_remove.attributes.st_size

        log.debug('Sufficient space to cache file.')
        return free_space

    def push(self, path: str, stream_info: StreamInfo, attributes: os.stat_result):
        log.debug('Request to add stream to cache: %s. Stat: %s', stream_info, attributes)
        size = attributes.st_size
        free_space = self._file_ops.get_free_space(self.data_dir)
        if size is not None:
            free_space = self._ensure_enough_space(size, free_space)

        download_lock = self._downloads_in_progress.get(path)
        if download_lock is not None:
            log.debug('Stream is already being downloaded: %s', stream_info)
            download_lock.acquire()
            log.debug('Pending stream download completed: %s', stream_info)
            if path in self:
                log.debug('Stream already in cache: %s', stream_info)
                return

        log.debug('Adding stream to cache: %s', stream_info)
        download_lock = threading.Lock()
        download_lock.acquire()
        self._downloads_in_progress[path] = download_lock
        try:
            target_relative_path = path[1:] if path[0] == '/' else path
            target_path = os.path.join(self.data_dir, target_relative_path)
            log.info('Downloading file into cache.')
            size = self._download_path(stream_info, target_path)
            log.debug('File downloaded. Size: %s', size)
            try:
                self._ensure_enough_space(size, free_space)
            except FuseOSError:
                log.info('File does not fit in cache. Deleting downloaded data.')
                self._file_ops.rm(target_path)
                raise

            self._total_size += size
            actual_attributes = update_stat(attributes, new_size=size)
            cache_entry = _CacheEntry(path, target_path, actual_attributes)
            self._entries[path] = cache_entry
        except ExecutionError as e:
            if e.error_code == 'NotEnoughSpace':
                raise FuseOSError(EFBIG)
            else:
                log.error('Execution error while downloading stream.', exc_info=sys.exc_info())
                raise FuseOSError(ENOENT)
        finally:
            download_lock.release()
            self._downloads_in_progress.pop(path)

    def open(self, path: str) -> int:
        cache_entry = self._entries.pop(path)
        self._entries[path] = cache_entry
        handle = self._get_handle()
        self._streams[handle] = (self._file_ops.open(cache_entry.download_path), path, threading.Lock())
        self._open_paths[path] = self._open_paths.get(path, 0) + 1
        return handle

    def read(self, handle: int, size: int, offset: int):
        open_file, _, read_lock = self._streams[handle]
        read_lock.acquire()
        try:
            open_file.seek(offset)
            return open_file.read(size)
        finally:
            read_lock.release()

    def release(self, handle: int):
        stream, path, _ = self._streams.pop(handle)
        open_count = self._open_paths[path] - 1
        if open_count == 0:
            self._open_paths.pop(path)
        else:
            self._open_paths[path] = open_count
        stream.close()

    def remove_from_cache(self, path):
        if path in self._open_paths:
            raise ValueError('Path currently opened and cannot be removed from cache.')

        self._remove_entry(self._entries[path])

    def get_open_handle_count(self, path):
        return self._open_paths.get(path) or 0

    def __contains__(self, item: Union[str, int]):
        return item in self._entries
