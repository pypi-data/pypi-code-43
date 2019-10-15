import sqlite3
from datetime import datetime
import os

from pydq import _queue, TIME_FORMAT


class SQLite(_queue):
    FILE_NAME = 'pydq.db'

    def __init__(self, name, db_file=os.path.join(os.getcwd(), FILE_NAME)):
        super().__init__(name)
        self.db_file = db_file
        if not os.path.exists(os.path.dirname(db_file)):
            os.makedirs(os.path.dirname(db_file), exist_ok=True)
        with sqlite3.connect(self.db_file) as conn:
            conn.cursor().execute('CREATE TABLE IF NOT EXISTS "%s" (qid TEXT NOT NULL, ts TEXT NOT NULL, val BLOB, PRIMARY KEY(qid, ts))' % name)
            conn.commit()

    def __exit__(self, exc_type, exc_val, exc_tb):
        conn = sqlite3.connect(self.db_file)
        c = conn.cursor()
        for txn in self.get_log():
            action, qitem = txn
            if action == self.CREATE:
                c.execute('REPLACE INTO "%s" (qid, ts, val) VALUES (?, ?, ?)' % self.name, (qitem['qid'], qitem['ts'], qitem['val']))
            elif action == self.DELETE:
                c.execute('DELETE FROM "%s" WHERE qid = ? AND ts = ?' % self.name, (qitem['qid'], qitem['ts']))
        conn.commit()
        conn.close()

    def __call__(self, qid=None, start_time=None, end_time=None, limit=0):
        start_time = datetime(1, 1, 1) if start_time is None else start_time
        end_time = datetime.utcnow() if end_time is None else end_time
        stmt = ['SELECT qid, ts, val from "%s" WHERE ts >= "%s" AND ts <= "%s"' %
                (self.name, start_time.strftime(TIME_FORMAT), end_time.strftime(TIME_FORMAT))]
        conn = sqlite3.connect(self.db_file)
        c = conn.cursor()
        if qid is not None:
            stmt.append(' AND qid = "%s"' % qid)
        stmt.append(' ORDER BY ts desc')
        if limit > 0:
            stmt.append(' LIMIT %i' % limit)
        c.execute(''.join(stmt))
        results = [{'qid': i[0], 'ts': i[1], 'val': i[2]} for i in c.fetchall()]  # TODO: Page this
        conn.close()
        with self.mutex:
            self.queue.extend(results)
        return self

    @staticmethod
    def list_all(db_file=os.path.join(os.getcwd(), FILE_NAME)):
        if not os.path.exists(os.path.dirname(db_file)):
            os.makedirs(os.path.dirname(db_file), exist_ok=True)
        with sqlite3.connect(db_file) as conn:
            c = conn.cursor()
            c.execute('select name from sqlite_master where type="table"')
            return [i[0] for i in c.fetchall()]
