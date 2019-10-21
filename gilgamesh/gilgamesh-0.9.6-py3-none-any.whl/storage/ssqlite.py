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

from ..lib.kernel import GK
from ..lib.kontext import Kontext

import time
from pprint import pprint

class SSqlite(GK):
    def __init__(self, *args, **kwargs):
        GK.__init__(self, *args, **kwargs)

        self.DB = "ipc:///tmp/series_out"
        self.data_path = kwargs['data_path']
        try:
            os.makedirs(self.data_path)
        except OSError as e:
            pass

        # one db per device!
        #self.conn = sqlite3.connect('./ssqlite.db', detect_types=sqlite3.PARSE_DECLTYPES)

        self.DOUT = "ipc:///tmp/data_out"
        self.receiver = self.context.socket(zmq.PULL)
        self.receiver.connect(self.DOUT)
        self.loop.create_task(self.write_data())

        self.loop.create_task(self.query_task())

    async def query_task(self):
        """
        task for answering queries
        """
        dbq = self.context.socket(zmq.REP)
        dbq.connect(self.DB)
        while True:
            raw = await dbq.precv()
            try:
                sig = raw.pop(0)
                dev_id = raw.pop(0)

                #db = sqlite3.connect(f'./{dev_id}.db', detect_types=sqlite3.PARSE_DECLTYPES)
                if sig != 'insert':
                    db = sqlite3.connect(f'file:{self.data_path}/{dev_id}.db?mode=ro', uri=True)
                else:
                    db = sqlite3.connect(f'{self.data_path}/{dev_id}.db')
                cur = db.cursor()
                reply = {}

                #print(sig)
                #print(raw)
                if sig == 'measurements':
                    colls = []
                    query = f'SELECT name FROM sqlite_master WHERE type="table"'
                    cur.execute(query)
                    measurements = [i[0] for i in cur.fetchall()]
                    await dbq.psnd(measurements)
                    cur.close()
                    db.close()
                    continue

                elif sig == 'count':
                    measurement = raw.pop(0)
                    query = f'SELECT count(*) FROM {measurement} '
                    try:
                        tmp = raw.pop(0)
                        if 'start' in tmp.keys():
                            query = query+f"WHERE time >= '{tmp['start']}' "
                            if 'stop' in tmp.keys():
                                query = query+f"AND time < '{tmp['stop']}' "
                    except:
                        pass
                    cur.execute(query)
                    count = [i[0] for i in cur.fetchall()]
                    await dbq.psnd(count)
                    cur.close()
                    db.close()
                    continue

                elif sig == 'get':
                    measurement = raw.pop(0)
                    tmp = raw.pop(0)

                    # get table column names and types for conversion
                    query = f'PRAGMA table_info({measurement})'
                    cur.execute(query)
                    records = cur.fetchall()
                    clist = [i[1] for i in records]
                    tlist = [i[2] for i in records]

                    query = f'SELECT * FROM "{measurement}" '

                    if tmp == 'head':
                        query = query+'ORDER BY time DESC LIMIT 1'

                    elif tmp == 'tail':
                        query = query+'ORDER BY time ASC LIMIT 1'

                    elif tmp == 'all':
                        query = query+'ORDER BY time DESC LIMIT 1000'

                    elif isinstance(tmp, dict):
                        if 'start' in tmp.keys():
                            query = query+f"WHERE time >= '{tmp['start']}' "
                            if 'stop' in tmp.keys():
                                query = query+f"AND time < '{tmp['stop']}' "
                        query = query+ f'ORDER BY time DESC LIMIT 1000'

                    else:
                        await dbq.psnd({'Error': True, 'Reason': 'Did not get get!' })
                        continue

                    records = []
                    cur.execute(query)
                    records = cur.fetchall()
                    records = self.from_db_format(records, clist, tlist)
                    await dbq.psnd(records)
                    cur.close()
                    db.close()
                    continue

                elif sig == 'insert':
                    measurement = raw.pop(0)
                    data = raw.pop(0)

                    if not isinstance(data, list):
                        data = [data]

                    #self.glog.debug(f'inserting {data}')
                    ret = self.alter_insert(cur, measurement, data)
                    db.commit()
                    await dbq.psnd(ret)
                    cur.close()
                    db.close()
                    continue

                elif sig == 'delete':
                    measurement = raw.pop(0)

                    thresh = self.iso_5min_ago()
                    query = f'SELECT deleteable FROM "{measurement}" where time >= "{thresh}" AND deleteable IS NOT NULL ORDER BY time DESC'
                    cur.execute(query)
                    records = cur.fetchall()
                    if records:
                        query = f'DROP TABLE "{measurement}"'
                        cur.execute(query)
                        db.commit()
                        await dbq.psnd({'Error': False, 'Reason': f'Deletion of {measurement} successful.'})
                    else:
                        await dbq.psnd({'Error': True, 'Reason': f'{measurement} is not deleteable.'})

                    cur.close()
                    db.close()
                    continue

                elif sig == 'chunk':
                    tic = time.time()
                    measurement = raw.pop(0)
                    tmp = raw.pop(0)

                    try:
                        offset = tmp['offset']
                        limit = tmp['limit']
                    except Exception as e:
                        await dbq.psnd({'Error': True, 'Reason': str(e)})

                    # get table column names and types for conversion
                    query = f'PRAGMA table_info({measurement})'
                    cur.execute(query)
                    records = cur.fetchall()
                    clist = [i[1] for i in records]
                    tlist = [i[2] for i in records]

                    cols = []
                    if 'cols' in tmp:
                        clist = ['time']
                        tlist = ['TIMESTAMP']
                        for i in records:
                            if i[1] in tmp['cols']:
                                clist.append(i[1])
                                tlist.append(i[2])
                        # FIXME sql-injection-city
                        cols_str = [f'"{col}"' for col in clist[1:]]
                        query = f'SELECT time, {", ".join(cols_str)} FROM "{measurement}" '
                    else:
                        query = f'SELECT * FROM "{measurement}" '

                    if 'start' in tmp.keys():
                        query = query+f"WHERE time > '{tmp['start']}' "
                        if 'stop' in tmp.keys():
                            query = query+f"AND time <= '{tmp['stop']}' "

                    query = query+ f"ORDER BY time DESC LIMIT {limit} OFFSET {offset}"

                    records = []
                    cur.execute(query)
                    records = cur.fetchall()
                    records = self.from_db_format(records, clist, tlist)

                    # get last metadata if necessary
                    zipped = zip(clist, tlist)
                    meta_list = []
                    meta_data = []
                    for i in zipped:
                        if i[1] not in ['TIMESTAMP', 'FLOAT']:
                            meta_list.append(i[0])
                    if records:
                        if not any(list(records[-1]['tags'].values())):
                            query = f'SELECT {", ".join(meta_list)} FROM "{measurement}" '
                            query = query+f'WHERE time < "{records[-1]["time"]}" AND COALESCE({", ".join(meta_list)}) IS NOT NULL ORDER BY time DESC LIMIT 1'
                            cur.execute(query)
                            meta_data = cur.fetchone()
                            records[-1]['tags'] = {k: v for (k, v) in zip(meta_list, meta_data)}

                    # log slow querys
                    toc = time.time()
                    if toc-tic > 2.00:
                        self.glog.info(f'Slow chunk query ({dev_id} {measurement}): {round((toc-tic), 3)} s')

                    await dbq.psnd(records)
                    cur.close()
                    db.close()
                    continue

                else:
                    await dbq.psnd({'Error': True, 'Reason': 'SSQLite Driver does not understand.'})

            except Exception as e:
                self.glog.error(f'Malformed query? --- {e}')
                #self.glog.error(f'Malformed query? --- {e} --- {sig} {dev_id} {measurement}')
                await dbq.psnd({'Error': True, 'Reason': str(e)})

    async def write_data(self):
        while True:
            raw = await self.receiver.precv()

            try:
                dev_id = raw.pop(0)
                measurement = raw.pop(0)
                data = raw.pop(0)
            except Exception as e:
                self.glog.error(f"Error while parsing incoming Data: {e}")
                continue

            if len(data) == 0:
                self.glog.debug(f"incoming data empty")
                continue
            #db = sqlite3.connect(f'./{dev_id}.db', detect_types=sqlite3.PARSE_DECLTYPES)
            db = sqlite3.connect(f'{self.data_path}/{dev_id}.db', timeout=10)
            cur = db.cursor()
            #self.glog.debug(f'Data of len {len(data)} received.')
            self.alter_insert(cur, measurement, data)
            db.commit()
            cur.close()
            db.close()

    def alter_insert(self, cur, measurement, data):
        """
        """
        try:
            cur.execute(f'CREATE TABLE IF NOT EXISTS "{measurement}" (time TIMESTAMP)')
        except Exception as e:
            self.glog.error(f"ssql error: {e}")
            return { 'Error': True, 'Reason': f'ssql error: {e}' }

        #pprint(data)
        clist = ['time']
        clist_str = ['time']
        try:
            cur.execute(f'SELECT * FROM "{measurement}"')
            col_exists = list(map(lambda x: x[0], cur.description))
        except Exception as e:
            self.glog.error(f"ssql error: {e}")
            return { 'Error': True, 'Reason': f'ssql error: {e}' }

        try:
            for col in data[0]['fields']:
                clist.append(col)
                clist_str.append(f'"{col}"')
                if col not in col_exists:
                    cur.execute(f'ALTER TABLE "{measurement}" ADD COLUMN "{col}" FLOAT')
        except Exception as e:
            self.glog.error(f"ssql error: {e}")
            return { 'Error': True, 'Reason': f'ssql error: {e}' }

        try:
            for col in data[0]['tags']:
                clist.append(col)
                clist_str.append(f'"{col}"')
                if col not in col_exists:
                    cur.execute(f'ALTER TABLE "{measurement}" ADD COLUMN "{col}" VARCHAR(128)')
        except Exception as e:
            self.glog.error(f'Could not save data to DB! --- {e} --- {dev_id} {measurement} length: {len(data)}')
            return { 'Error': True, 'Reason': f'ssql error: {e}' }

        # fkn query
        q = f'INSERT INTO "{measurement}" ' + f"({', '.join(clist_str)}) VALUES ({', '.join(['?']*len(clist_str))})"
        data = self.to_db_format(data, clist)
        try:
            cur.executemany(q, data)
            return  { 'Error': False, 'Reason': f'Insert Success.' }
        except Exception as e:
            print(clist)
            pprint(data)
            self.glog.error(f'Could not save data to DB! --- {e}')
            return { 'Error': True, 'Reason': f'ssql error: {e}' }

    def to_db_format(self, data, clist):
        """
        takes list of data dicts and a list with key names
        returns list of data tuples with values from data dict in order of key list
        TODO error checking?
        """
        for i, d in enumerate(data):
            tmp = []
            tmp.append(d['time'])
            for k in clist:
                if k in d['fields'].keys():
                    tmp.append(d['fields'][k])
                elif k in d['tags'].keys():
                    tmp.append(d['tags'][k])
            data[i] = tuple(tmp)
        return data

    def from_db_format(self, data, clist, tlist):
        """
        takes list of data tuples with values from data dict in order of key list
        returns list of data dicts with 'fields' key for float values and 'tags' key for strings
        TODO error checking?
        """
        for i, d in enumerate(data):
            tmp = {}
            tmp['fields'] = {}
            tmp['tags'] = {}
            for j, t in enumerate(tlist):
                if t == 'TIMESTAMP':
                    tmp[clist[j]] = d[j]
                elif t == 'FLOAT':
                    tmp['fields'].update({clist[j]: d[j]})
                else:
                    tmp['tags'].update({clist[j]: d[j]})
            data[i] = tmp
        return data

def ssqlite_process(kcfg):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    kcfg['context'] = Kontext()
    kcfg['loop'] = loop
    
    ssqlite = SSqlite(**kcfg)
    ssqlite.start()
