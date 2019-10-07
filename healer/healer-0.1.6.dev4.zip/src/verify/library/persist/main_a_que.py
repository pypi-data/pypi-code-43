import apsw
import pickle
from datetime import datetime
from typing import Any


class StoredQueue():

    store_path:str
    conn:apsw.Connection

    def __init__(self, store_path):
        self.store_path = store_path

    def encode(self, entry_object:Any) -> memoryview:
        return memoryview(pickle.dumps(entry_object))

    def decode(self, entry_buffer:memoryview) -> Any:
        return pickle.loads(bytes(entry_buffer))

    def open(self):
        conn = apsw.Connection(self.store_path)
        self.conn = conn
        cursor = self.cursor()
        cursor.execute('PRAGMA journal_mode=DELETE')
        cursor.execute('PRAGMA synchronous=OFF')
        sql_table = f"create table if not exists queue (clock integer primary key, entry blob)"
        cursor.execute(sql_table)

#         cursor.execute('begin')
#         cursor.execute('commit')

    def close(self):
        self.conn.close(True)
        self.conn = None

    def cursor(self):
        return self.conn.cursor()

    def get(self) -> Any:
        with self.conn:
            sql_select = f"select * from queue order by rowid asc limit 1"
            cursor = self.cursor()
            record_list = cursor.execute(sql_select)
            for record in record_list:
                clock = record[0]
                entry = record[1]
                sql_delete = f"delete from queue where clock={clock}"
                cursor.execute(sql_delete)
                return self.decode(entry)
            return None

    def persist(self, entry:Any) -> None:
        with self.conn:
            sql_insert = f'insert into queue (entry) values (?)'
            self.conn.cursor().execute(sql_insert, [self.encode(entry)])


queue = StoredQueue("data.queue")

queue.open()

queue.persist(f"hello-kitty @ {datetime.now()}")

entry = queue.get()
print(entry)

queue.close()
