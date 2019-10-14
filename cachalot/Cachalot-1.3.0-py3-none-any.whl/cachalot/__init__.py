"""Cachalot is a minimal persistent memoization cache, that uses TinyDB."""

VERSION = (1, 1, 0)

__title__ = 'cachalot'
__description__ = 'Minimal persistent memoization cache'
__url__ = 'http://gitlab.com/radek-sprta/cachalot'
__download_url__ = 'https://gitlab.com/radek-sprta/cachalot/repository/archive.tar.gz?ref=master'
__version__ = '.'.join(map(str, VERSION))
__author__ = 'Radek Sprta'
__author_email__ = 'mail@radeksprta.eu'
__license__ = 'MIT License'
__copyright__ = "Copyright 2018 Radek Sprta"

import functools
import hashlib
import inspect
import os
import time
from typing import Any, Callable

import jsonpickle
import tinydb  # pylint: disable=wrong-import-order
import tinydb_smartcache


class Cache:
    """Offline cache for search results.

    Attributes:
        path: Defaults to .cache.json. Path to the database file.
        timeout: Defaults to infinite. Period after which results should expire.
        size: Defaults to infinite. Maximum number of cached results.
        filesize: Defaults to infinite. Maximum size of databytes in bytes.
        storage: Defaults to JSONStorage. Storage type for TinyDB.
    """

    def __init__(self,
                 *,
                 path: str = '.cache.json',
                 timeout: int = 0,
                 size: int = 0,
                 filesize: int = 0,
                 storage: tinydb.storages.Storage = tinydb.storages.JSONStorage,
                 retry: bool = False,
                 renew_on_read: bool = True) -> None:
        self.path = os.path.abspath(os.path.expanduser(path))
        os.makedirs(os.path.dirname(self.path), exist_ok=True)
        self.timeout = timeout
        self.size = size
        self.filesize = filesize
        self.retry = retry
        self.renew_on_read = renew_on_read
        self.db = tinydb.TinyDB(self.path, storage)
        self.db.table_class = tinydb_smartcache.SmartCacheTable

    def clear(self) -> None:
        """Clear the cache."""
        self.db.purge()

    def expiry(self) -> float:
        """Return expiration time for cached results."""
        return time.time() + self.timeout

    def get(self, key: str) -> Any:
        """Get torrent from database.

        Args:
            key: Key hash.

        Returns:
            Cached object.
        """
        self._remove_expired()
        entry = tinydb.Query()
        value = self.db.get(entry.key == key)
        if value:
            if self.renew_on_read:
                self.db.update({'time': self.expiry()}, entry.key == key)
            return jsonpickle.decode(value['value'])
        return None

    def insert(self, key: str, entry: Any) -> None:
        """Insert entry into cache.

        Args:
            key: Key hash of the entry to store.
            entry: Object to cache.
        """
        value = jsonpickle.encode(entry)
        self.db.insert({'key': key, 'time': self.expiry(), 'value': value})
        if self.size > 0 and len(self.db) > self.size:
            self._remove_oldest()
        if self.filesize > 0:
            while os.stat(self.path).st_size > self.filesize and len(self.db) > 0:
                self._remove_oldest()


    @staticmethod
    def _is_method(function: Callable[..., Any]) -> bool:
        """Check if function is actually a method.

        Args:
            function: Function to check the state of.

        Returns:
            True if function is method, false otherwise.
        """
        try:
            if '.' in function.__qualname__ and inspect.getfullargspec(function).args[0] == 'self':
                return True
            return False
        except IndexError:
            # For functions with no arguments
            return False

    def remove(self, key: str) -> None:
        """Delete key from cache.

        Args:
            key: Hash key to delete from the cache.
        """
        entry = tinydb.Query()
        self.db.remove(entry.key == key)

    def _remove_expired(self) -> None:
        """Remove old entries."""
        if self.timeout < 1:
            return

        entry = tinydb.Query()
        now = time.time()
        self.db.remove(entry.time < now)

    def _remove_oldest(self) -> None:
        """Remove oldest entry."""
        oldest = self.db.all()[0]['key']
        self.remove(oldest)

    def __call__(self, function: Callable[..., Any]):
        """Decorator for caching function results.

        Args:
            function: Function to decorate.

        Returns:
            Cached function.
        """
        @functools.wraps(function)
        def wrapped(*args, **kwargs):
            """Cache function."""
            result = ''
            seed_args = args[1:] if self._is_method(function) else args
            seed = function.__name__ + \
                jsonpickle.encode(seed_args) + jsonpickle.encode(kwargs)
            key = hashlib.md5(seed.encode('utf8')).hexdigest()
            result = self.get(key)
            if not result:
                if self.retry or result is None:
                    result = function(*args, **kwargs)
                    self.insert(key, result)
            return result
        return wrapped
