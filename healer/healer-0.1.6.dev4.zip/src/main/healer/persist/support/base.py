"""
Base types for disk based maps, lists, etc.
"""

from __future__ import annotations

import abc
import os
import pickle
import sqlite3
from typing import Any
from typing import List

from healer.support.typing import override


class StoredCodec(abc.ABC):
    "persistence serilalizer"

    @abc.abstractmethod
    def encode(self, entry_object:Any) -> bytes:
        "serialize object into buffer"

    @abc.abstractmethod
    def decode(self, entry_buffer:bytes) -> Any:
        "deserialize buffer into object"

    def encode_key(self, entry_object:Any) -> bytes:
        return self.encode(entry_object)

    def decode_key(self, entry_buffer:bytes) -> Any:
        return self.decode(entry_buffer)

    def encode_value(self, entry_object:Any) -> bytes:
        return self.encode(entry_object)

    def decode_value(self, entry_buffer:bytes) -> Any:
        return self.decode(entry_buffer)


class StoredCodecPickle(StoredCodec):
    "persistence serilalizer via python pickle"

    @override
    def encode(self, entry_object:Any) -> bytes:
        return pickle.dumps(entry_object)

    @override
    def decode(self, entry_buffer:bytes) -> Any:
        return pickle.loads(entry_buffer)


class StoredCodecString(StoredCodec):
    "persistence serilalizer via string buffers"

    @override
    def encode(self, entry_object:str) -> bytes:
        assert isinstance(entry_object, str), f"need string: {entry_object}"
        return entry_object.encode()

    @override
    def decode(self, entry_buffer:bytes) -> str:
        return entry_buffer.decode()


class CursorFace(abc.ABC):
    """
    """

    @abc.abstractmethod
    def execute(self, sql:str, var:List[Any]=None):
        pass


class ConnectionFace(abc.ABC):
    """
    """

    @abc.abstractmethod
    def cursor(self) -> CursorFace:
        pass


class DatabaseFace(abc.ABC):
    """
    """

    @abc.abstractmethod
    def connectionection(self) -> ConnectionFace:
        pass


class StoredSupport:
    ""
    default_pragma_dict = dict(
        page_size=1024 * 4,
        cache_size=1024 * 4,
        journal_mode='wal',
    )


class StoredDatabase(abc.ABC):
    """
    Base type for disk based mapping, qeueue, etc
    """

    store_path:str
    pragma_dict:dict
    connection:sqlite3.Connection

    def __str__(self):
        return f"{self.__class__.__name__}(store_path='{self.store_path}')"

    def __repr__(self):
        return self.__str__()

    def __init__(self,
            store_path:str,
            pragma_dict:dict=StoredSupport.default_pragma_dict,
        ):
        parent_path = os.path.dirname(store_path)
        assert os.path.exists(parent_path), f"need parent path: {store_path}"
        self.store_path = store_path
        self.pragma_dict = pragma_dict
        self.connection = None

    def touch(self) -> None:
        "ensure disk file"
        self.open()
        self.close()

    def open(self) -> None:
        if self.connection:
            return
        else:
            self.connection = sqlite3.connect(
                database=self.store_path,
                # disable python transactions
                # enable libsqlite3 autocommit
                isolation_level=None,
            )
            for key, value in self.pragma_dict.items():
                self.cursor().execute(f"pragma {key}={value}")

    def close(self) -> None:
        if self.connection:
            self.connection.commit()
            self.connection.close()
            self.connection = None

    def commit(self) -> None:
        self.connection.commit()

    def cursor(self) -> Any:
        return self.connection.cursor()

    def vacuum(self):
        return self.cursor().execute('vacuum')
