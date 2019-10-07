"""
Disk based dictionary on top of Sqlite
"""

from __future__ import annotations

from typing import Any
from typing import Callable
from typing import Generator
from typing import Tuple
from typing import Type

from healer.support.typing import override

from .base import StoredCodec
from .base import StoredCodecPickle
from .base import StoredDatabase
from .base import StoredSupport


class StoredMappingSupport:

    @staticmethod
    def default_reactor(entry:Any) -> None:
        pass


class StoredMapping(StoredDatabase):
    """
    Disk based dictionary
    """

    table_name:str
    stored_codec:StoredCodec

    def __init__(self,
            store_path:str,
            table_name:str='mapping',
            pragma_dict:dict=StoredSupport.default_pragma_dict,
            codec_class:Type[StoredCodec]=StoredCodecPickle,
        ):
        super().__init__(
            store_path=store_path, pragma_dict=pragma_dict,
        )
        self.table_name = table_name
        self.stored_codec = codec_class()
        #
        self.sql_ensure_table = f'create table if not exists "{self.table_name}" (key blob primary key, value blob)'
        self.sql_delete_data = f'delete from "{self.table_name}"'
        self.sql_select_size = f'select count(*) from "{self.table_name}"'
        self.sql_select_max = f'select max(rowid) from "{self.table_name}"'
        self.sql_select_keys = f'select key from "{self.table_name}" order by rowid'
        self.sql_select_values = f'select value from "{self.table_name}" order by rowid'
        self.sql_select_entries = f'select key, value from "{self.table_name}" order by rowid'
        self.sql_select_contains = f'select 1 from "{self.table_name}" where key=?'
        self.sql_select_getitem = f'select value from "{self.table_name}" where key=?'
        self.sql_insert_setitem = f'insert or replace into "{self.table_name}" (key, value) values (?,?)'
        self.sql_delete_delitem = f'delete from "{self.table_name}" where key=?'

    def encode_key(self, entry_object:Any) -> memoryview:
        return self.stored_codec.encode_key(entry_object)

    def decode_key(self, entry_buffer:memoryview) -> Any:
        return self.stored_codec.decode_key(entry_buffer)

    def encode_value(self, entry_object:Any) -> memoryview:
        return self.stored_codec.encode_value(entry_object)

    def decode_value(self, entry_buffer:memoryview) -> Any:
        return self.stored_codec.decode_value(entry_buffer)

    @override
    def open(self) -> None:
        super().open()
        self.cursor().execute(self.sql_ensure_table)

    @override
    def close(self) -> None:
        super().close()

    def clear(self) -> None:
        self.cursor().execute(self.sql_delete_data)

    def size(self) -> int:
        record = next(self.cursor().execute(self.sql_select_size), None)
        count = record[0]
        return count

    def is_empty(self) -> bool:
        record = next(self.cursor().execute(self.sql_select_max), None)
        return record[0] is None

    def keys(self) -> Generator:
        "produce key generator"
        record_list = self.cursor().execute(self.sql_select_keys)
        for record in record_list:
            key = self.decode_key(record[0])
            yield key

    def values(self) -> Generator:
        "produce value generator"
        record_list = self.cursor().execute(self.sql_select_values)
        for record in record_list:
            value = self.decode_value(record[0])
            yield value

    def items(self) -> Generator:
        "produce (key,value) generator"
        record_list = self.cursor().execute(self.sql_select_entries)
        for record in record_list:
            key = self.decode_key(record[0])
            value = self.decode_value(record[1])
            yield (key, value)

    def get(self, key:Any, default:Any=None) -> Any:
        try:
            return self.__getitem__(key)
        except Exception:
            return default

    def __len__(self):
        return self.size()

    def __bool__(self) -> bool:
        "truth check: non empty"
        return not self.is_empty()

    def __iter__(self) -> Generator:
        "default iterator: by keys"
        return self.keys()

    def __contains__(self, key:Any) -> bool:
        record = next(self.cursor().execute(self.sql_select_contains, [self.encode_key(key)]), None)
        return record is not None

    def __getitem__(self, key:Any) -> Any:
        record = next(self.cursor().execute(self.sql_select_getitem, [self.encode_key(key)]) , None)
        if record:
            return self.decode_value(record[0])
        else:
            raise KeyError(key)

    def __setitem__(self, key:Any, value:Any):
        self.cursor().execute(self.sql_insert_setitem, [self.encode_key(key), self.encode_value(value)])

    def __delitem__(self, key:Any) -> None:
        if key in self:
            self.cursor().execute(self.sql_delete_delitem, [self.encode_key(key)])
        else:
            raise KeyError(key)
