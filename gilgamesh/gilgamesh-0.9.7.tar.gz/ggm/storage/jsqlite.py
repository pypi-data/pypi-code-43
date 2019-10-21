"""
    Copyright (c) 2019 Contributors as noted in the AUTHORS file
    This file is part of ggm, the GILGAMESH core engine in Python.
    ggm is free software; you can redistribute it and/or modify it under
    the terms of the GNU Lesser General Public License (GPL) as published
    by the Free Software Foundation; either version 3 of the License, or
    (at your option) any later version.
    As a special exception, the Contributors give you permission to link
    this library with independent modules to produce an executable,
    regardless of the license terms of these independent modules, and to
    copy and distribute the resulting executable under terms of your choice,
    provided that you also meet, for each linked independent module, the
    terms and conditions of the license of that module. An independent
    module is a module which is not derived from or based on this library.
    If you modify this library, you must extend this exception to your
    version of the library.
    ggm is distributed in the hope that it will be useful, but WITHOUT
    ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
    FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public
    License for more details.
    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""
import sys, os
import zmq
import asyncio
import sqlite3
import pickle
import json
from datetime import datetime as dt

from ..lib.kernel import GK
from ..lib.kontext import Kontext

import time
from pprint import pprint

class GJSqlite(GK):
    def __init__(self, *args, **kwargs):
        GK.__init__(self, *args, **kwargs)

        self.DB = "ipc:///tmp/json_out"
        self.data_path = kwargs['data_path']
        try:
            os.makedirs(self.data_path)
        except OSError as e:
            pass

        self.conn = sqlite3.connect(f'{self.data_path}/jsqlite.db', detect_types=sqlite3.PARSE_DECLTYPES)

        self.loop.create_task(self.query_task())

    async def query_task(self):
        """
        task for answering queries
        """
        dbq = self.context.socket(zmq.REP)
        dbq.connect(self.DB)
        cur = self.conn.cursor()
        while True:
            raw = await dbq.precv()
            try:
                sig = raw.pop(0)
                table = raw.pop(0)

                reply = {}

                #print(sig)
                #print(raw)
                if sig == 'measurements':
                    colls = []
                    query = f'SELECT _id FROM "{table}" UNIQE'
                    cur.execute(query)
                    _ids = [i[0] for i in cur.fetchall()]
                    await dbq.psnd(_ids)
                    continue

                elif sig == 'get':
                    _id = raw.pop(0)
                    tmp = raw.pop(0)

                    query = f'SELECT * FROM "{table}" WHERE _id = "{_id}" '

                    if tmp == 'head':
                        query = query+'ORDER BY time DESC LIMIT 1'
                        cur.execute(query)
                        records = cur.fetchone()
                        #await dbq.psnd(pickle.loads(records[-1]))
                        await dbq.psnd(json.loads(records[-1]))
                        continue

                    if tmp == 'tail':
                        query = query+'ORDER BY time ASC LIMIT 1'
                        cur.execute(query)
                        records = cur.fetchone()
                        #await dbq.psnd(pickle.loads(records[-1]))
                        await dbq.psnd(json.loads(records[-1]))
                        continue

                    if tmp == 'all':
                        query = query+'ORDER BY time DESC LIMIT 1000'
                        cur.execute(query)
                        records = cur.fetchall()
                        #await dbq.psnd([pickle.loads(record[-1]) for record in records])
                        await dbq.psnd([json.loads(record[-1]) for record in records])
                        continue

                    # this should never be reached
                    await dbq.psnd({'Error': True, 'Reason': 'Did not get get!' })

                elif sig == 'insert':
                    _id = raw.pop(0)
                    data = raw.pop(0)

                    ret = self.alter_insert(cur, table, _id, data)
                    self.conn.commit()
                    await dbq.psnd(ret)

                elif sig == 'nupsert':
                    _id = raw.pop(0)
                    data = raw.pop(0)

                    cur.execute(f'CREATE TABLE IF NOT EXISTS "{table}" (time TIMESTAMP, _id VARCHAR(128), json BLOB)')
                    query = f'SELECT * FROM "{table}" WHERE _id = "{_id}" ORDER BY time DESC LIMIT 1'
                    cur.execute(query)
                    doc = cur.fetchone()
                    if doc:
                        # rowid? see sqlite docs!
                        query = f'UPDATE "{table}" SET json = ? WHERE rowid IN (SELECT rowid FROM "{table}" WHERE _id = "{_id}" ORDER BY time DESC LIMIT 1)'
                        #doc = pickle.loads(doc[-1])
                        doc = json.loads(doc[-1])
                        #doc.update(data)
                        doc = self.update(doc, data)
                        #cur.execute(query, (pickle.dumps(doc),))
                        cur.execute(query, (json.dumps(doc),))
                    else:
                        resp = self.alter_insert(cur, table, _id, data)

                    self.conn.commit()
                    await dbq.psnd({"Error": False, 'Reason': "NUpsert Success."})

                elif sig == 'delete':
                    _id = raw.pop(0)
                    del_keys = raw

                    try:
                        query = f'SELECT * FROM "{table}" WHERE _id = "{_id}" ORDER BY time DESC LIMIT 1'
                        cur.execute(query)
                        doc = cur.fetchone()
                        doc = json.loads(doc[-1])
                    except Exception as e:
                        await dbq.psend_err(f'fail: this resource does not exist!')
                        continue

                    if not del_keys:
                        query = f'DELETE FROM "{table}" WHERE _id = "{_id}"'
                        cur.execute(query)
                    else:
                        self.delete(doc, del_keys)
                        query = f'UPDATE "{table}" SET json = ? WHERE rowid IN (SELECT rowid FROM "{table}" WHERE _id = "{_id}" ORDER BY time DESC LIMIT 1)'
                        cur.execute(query, (json.dumps(doc),))

                    self.conn.commit()
                    resp = { 'Error': False, 'Reason': f'Delete Success.' }
                    await dbq.psnd(resp)

                else:
                    await dbq.psnd({'Error': True, 'Reason': 'JSQLite Driver does not understand.'})

            except Exception as e:
                self.glog.error(f'Malformed query? -- {e}')
                await dbq.psnd({'Error': True, 'Reason': str(e)})

    def delete(self, d, u):
        k = u.pop(0)
        if not u:
            try:
                del d[k]
            except Exception as e:
                return d
        if isinstance(u, list):
            try:
                self.delete(d[k], u)
            except Exception as e:
                return d
        #return d

    def update(self, d, u):
        for k, v in u.items():
            dv = d.get(k, {})
            if not isinstance(dv, dict):
                d[k] = v
            elif isinstance(v, dict):
                d[k] = self.update(dv, v)
            else:
                d[k] = v
        return d

    def alter_insert(self, cur, table , _id, data, upsert=False):
        """
        """
        try:
            cur.execute(f'CREATE TABLE IF NOT EXISTS "{table}" (time TIMESTAMP, _id VARCHAR(128), json BLOB)')
        except Exception as e:
            self.glog.error(f"could not create table: {e}")
            return { 'Error': True, 'Reason': f'could not create table: {e}' }

        # fkn query
        q = f'INSERT INTO "{table}" (time, _id, json) VALUES (?, ?, ?) '
        try:
            #cur.execute(q, [dt.utcnow().isoformat(sep=' '), _id, pickle.dumps(data)])
            cur.execute(q, [dt.utcnow().isoformat(sep=' '), _id, json.dumps(data)])
            return  { 'Error': False, 'Reason': f'Insert Success.' }
        except Exception as e:
            self.glog.error(f'Could not save data to DB! --- {e}')
            return { 'Error': True, 'Reason': f'psql error: {e}' }

def jsqlite_process(kcfg):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    kcfg['context'] = Kontext()
    kcfg['loop'] = loop
    
    ssqlite = GJSqlite(**kcfg)
    ssqlite.start()
