"""
Disk based queue on top of Sqlite
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


class StoredQueueSupport:

    @staticmethod
    def default_reactor(entry:Any) -> None:
        pass


class StoredQueue(StoredDatabase):
    """
    Disk based queue
    """

    table_name:str
    stored_codec:StoredCodec

    def __init__(self,
            store_path:str,
            table_name:str='queue',
            pragma_dict:dict=StoredSupport.default_pragma_dict,
            codec_class:Type[StoredCodec]=StoredCodecPickle,
        ):
        super().__init__(store_path, pragma_dict)
        self.table_name = table_name
        self.stored_codec = codec_class()
        #
        self.sql_ensure_table = f'create table if not exists "{self.table_name}" (uid integer primary key, entry blob)'
        self.sql_select_size = f'select count(*) from "{self.table_name}"'
        self.sql_select_head = f'select uid, entry from "{self.table_name}" order by uid asc limit 1'
        self.sql_insert_tail = f'insert or replace into "{self.table_name}" (entry) values (?)'
        self.sql_delete_item = f'delete from "{self.table_name}" where uid=(?)'
        self.sql_select_entries = f'select entry from "{self.table_name}" order by uid asc'

    def encode(self, entry_object:Any) -> memoryview:
        return self.stored_codec.encode(entry_object)

    def decode(self, entry_buffer:memoryview) -> Any:
        return self.stored_codec.decode(entry_buffer)

    def open(self):
        super().open()
        self.cursor().execute(self.sql_ensure_table)

    def close(self):
        super().close()

    def size(self):
        record = next(self.cursor().execute(self.sql_select_size), None)
        count = record[0]
        return count

    def read_head(self) -> Tuple[int, Any]:
        "extract first element of the queue"
        return next(self.cursor().execute(self.sql_select_head), None)

    def write_tail(self, entry:Any) -> None:
        "append last element to the queue"
        self.cursor().execute(self.sql_insert_tail, [self.encode(entry)])

    def remove_entry(self, uid:int) -> None:
        "delete queue element by uid"
        self.cursor().execute(self.sql_delete_item, [uid])

    def persist(self, entry:Any) -> None:
        # TODO
        with self.connection:
            self.write_tail(entry)

    def retrieve(self, reactor:Callable=StoredQueueSupport.default_reactor) -> bool:
        # TODO
        with self.connection:
            record = self.read_head()
            if record:
                uid = record[0]
                entry = self.decode(record[1])
                reactor(entry)
                self.remove_entry(uid)
                return True
            else:
                return False

    def iterate(self, reactor:Callable=StoredQueueSupport.default_reactor) -> None:
        "apply reactor to queue elements"
        for entry in self:
            reactor(entry)

    def __iter__(self) -> Generator:
        "produce yielding iteration generator"
        record_list = self.cursor().execute(self.sql_select_entries)
        for record in record_list:
            entry = self.decode(record[0])
            yield entry
