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
import sys
import zmq
import asyncio

import psycopg2
import psycopg2.extras
from psycopg2 import sql

from ..lib.kernel import GK
from ..lib.kontext import Kontext

import time
import json
from pprint import pprint
from datetime import datetime as dt

class KTimescale(GK):
    def __init__(self, *args, **kwargs):
        GK.__init__(self, *args, **kwargs)

        self.DB = "ipc:///tmp/series_out"

        # FIXME hard coded? better for secrets?
        with open(f'/etc/gilgamesh/timescaledb.secret', 'r') as raw:
            dbcfg = json.load(raw)
            dbname = dbcfg['dbname']
            dbuser = dbcfg['dbuser']
            dbpw = dbcfg['dbpw']
            dbhost = dbcfg['dbhost']
            del dbcfg

        self.dsn = f'dbname={dbname} user={dbuser} password={dbpw} host={dbhost}'
        #self.conn = psycopg2.connect(dsn)
        #self.conn.set_isolation_level(0) # autocommit
        #tmst_as_string = psycopg2.extensions.new_type(psycopg2.extensions.TIME.values, 'TIME', psycopg2.STRING)
        #psycopg2.extensions.register_type(tmst_as_string)

        # we are a time series adapter!
        self.DOUT = "ipc:///tmp/data_out"
        self.receiver = self.context.socket(zmq.PULL)
        self.receiver.connect(self.DOUT)
        self.loop.create_task(self.write_data())

        self.loop.create_task(self.query_task())

    async def query_task(self):
        """
        task for answering timescaledb queries
        """
        dbq = self.context.socket(zmq.REP)
        dbq.connect(self.DB)
        conn = psycopg2.connect(self.dsn)
        conn.set_session(autocommit=True, readonly=True)
        cur = conn.cursor()
        while True:
            raw = await dbq.precv()
            try:
                sig = raw.pop(0)
                dev_id = raw.pop(0)

                reply = {}

                #print(sig)
                #pprint(raw)
                if sig == 'measurements':
                    colls = []
                    query = sql.SQL("SELECT table_name FROM information_schema.tables WHERE table_schema = {0}").format(sql.Literal(dev_id))
                    cur.execute(query)
                    measurements = [i[0] for i in cur.fetchall()]
                    await dbq.psnd(measurements)
                    continue

                elif sig == 'count':
                    measurement = raw.pop(0)
                    query = sql.SQL("SELECT COUNT(*) FROM {0}.{1} ").format(*tuple(map(sql.Identifier, [dev_id, measurement])))

                    try:
                        tmp = raw.pop(0)
                        if 'start' in tmp.keys():
                            query = query + sql.SQL(f"WHERE time >= '{tmp['start']}' ")
                            if 'stop' in tmp.keys():
                                query = query + sql.SQL(f"AND time < '{tmp['stop']}' ")
                    except:
                        pass

                    cur.execute(query)
                    count = [i[0] for i in cur.fetchall()]
                    await dbq.psnd(count)
                    continue

                elif sig == 'get':
                    measurement = raw.pop(0)
                    tmp = raw.pop(0)

                    query = sql.SQL("SELECT * FROM {0}.{1} ").format(*tuple(map(sql.Identifier, [dev_id, measurement])))

                    if tmp == 'head':
                        query = query + sql.SQL('ORDER BY time DESC LIMIT 1')
                        cur.execute(query)
                        records = cur.fetchall()
                        clist = [i[0] for i in cur.description]
                        records = self.from_db_format(records, clist)
                        await dbq.psnd(records)
                        continue

                    if tmp == 'tail':
                        query = query + sql.SQL('ORDER BY time ASC LIMIT 1')
                        cur.execute(query)
                        records = cur.fetchall()
                        clist = [i[0] for i in cur.description]
                        records = self.from_db_format(records, clist)
                        await dbq.psnd(records)
                        continue

                    if tmp == 'all':
                        query = query + sql.SQL('ORDER BY time DESC LIMIT 1000')
                        cur.execute(query)
                        records = cur.fetchall()
                        clist = [i[0] for i in cur.description]
                        records = self.from_db_format(records, clist)
                        await dbq.psnd(records)
                        continue

                    if isinstance(tmp, dict):
                        if 'start' in tmp.keys():
                            query = query + sql.SQL(f"WHERE time >= '{tmp['start']}' ")
                            if 'stop' in tmp.keys():
                                query = query + sql.SQL(f"AND time < '{tmp['stop']}' ")

                        query = sql.Composed(query, 'ORDER BY time DESC LIMIT 1000')
                        records = []

                        cur.execute(query)
                        records = cur.fetchall()
                        clist = [i[0] for i in cur.description]
                        records = self.from_db_format(records, clist)
                        await dbq.psnd(records)
                        continue
                    # this should never be reached
                    await dbq.psnd({'Error': True, 'Reason': 'Did not get get!' })

                elif sig == 'insert':
                    measurement = raw.pop(0)
                    data = raw.pop(0)

                    # should not be needed !!
                    # remove when sure!
                    if not isinstance(data, list):
                        data = [data]

                    ret = self.alter_insert(cur, dev_id, measurement, data)
                    await dbq.psnd(ret)
                    continue

                elif sig == 'delete':
                    measurement = raw.pop(0)

                    thresh = self.iso_5min_ago().isoformat(sep=' ')
                    query = sql.SQL("SELECT EXISTS(SELECT deleteable FROM {0}.{1} where time >= {2} AND deleteable IS NOT NULL ORDER BY time DESC)").format(
                            sql.Identifier(dev_id), sql.Identifier(measurement), sql.Literal(thresh))
                    cur.execute(query)
                    records = cur.fetchall()
                    if records[0][0]:
                        query = sql.SQL("DROP TABLE {0}.{1} CASCADE").format(
                                sql.Identifier(dev_id), sql.Identifier(measurement))
                        cur.execute(query)
                        await dbq.psnd({'Error': False, 'Reason': f'Deletion of {measurement} successful.'})
                    else:
                        await dbq.psnd({'Error': True, 'Reason': f'{measurement} is not deleteable.'})

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

                    query = sql.SQL("SELECT column_name, data_type FROM information_schema.columns WHERE table_schema = {0} AND table_name = {1}").format(sql.Literal(dev_id),sql.Literal(measurement))
                    cur.execute(query)
                    records = cur.fetchall()
                    meta_list = [x[0] for x in filter(lambda x: x[1] == 'character varying', records)]

                    clist = []
                    if 'cols' in tmp:
                        for i in records:
                            if i[0] == 'time':
                                clist.append(i[0])
                            elif i[0] in tmp['cols']:
                                clist.append(i[0])
                        # FIXME sql-injection-city
                        query = sql.SQL("SELECT {2} FROM {0}.{1} ").format(
                                *tuple(map(sql.Identifier, [dev_id, measurement])),
                                sql.SQL(', ').join(map(sql.Identifier, clist)))
                    else:
                        clist = [n[0] for n in records]
                        query = sql.SQL("SELECT * FROM {0}.{1} ").format(
                                sql.Identifier(dev_id), sql.Identifier(measurement))

                    # FIXME sql-injection-city
                    if 'start' in tmp.keys():
                        query = query + sql.SQL(f"WHERE time > '{tmp['start']}' ")
                        if 'stop' in tmp.keys():
                            query = query + sql.SQL(f"AND time <= '{tmp['stop']}' ")

                    query = query + sql.SQL(f"ORDER BY time DESC LIMIT {limit} OFFSET {offset}")

                    records = []
                    cur.execute(query)
                    records = cur.fetchall()
                    records = self.from_db_format(records, clist)

                    # get last metadata if necessary
                    if records:
                        if not any(list(records[-1]['tags'].values())):
                            query = sql.SQL("SELECT {0} FROM {1}.{2} WHERE time < {3} AND COALESCE({0}) IS NOT NULL ORDER BY time DESC LIMIT 1").format(
                                    sql.SQL(', ').join(map(sql.Identifier, meta_list)),
                                    *tuple(map(sql.Identifier, [dev_id, measurement])),
                                    sql.Literal(records[-1]['time']))
                            cur.execute(query)
                            meta_data = cur.fetchone()
                            records[-1]['tags'] = {k: v for (k, v) in zip(meta_list, meta_data)}

                    # log slow querys
                    toc = time.time()
                    if toc-tic > 2.00:
                        self.glog.info(f'Slow chunk query ({dev_id} {measurement}): {round((toc-tic), 3)} s')

                    await dbq.psnd(records)
                    continue

                else:
                    await dbq.psnd({'Error': True, 'Reason': 'TimescaleDB Driver does not understand.'})

            except Exception as e:
                self.glog.error(f'Malformed query? -- {e}')
                await dbq.psnd({'Error': True, 'Reason': str(e)})

    async def write_data(self):
        conn = psycopg2.connect(self.dsn)
        conn.set_session(autocommit=True) # autocommit
        conn.set_isolation_level(0) # autocommit
        cur = conn.cursor()
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
            #self.glog.debug(f'Data of len {len(data)} received.')
            self.alter_insert(cur, dev_id, measurement, data)

    def alter_insert(self, cur, dev_id, measurement, data):
        """
        """
        try:
            cur.execute(sql.SQL("CREATE SCHEMA IF NOT EXISTS {0}").format(sql.Identifier(dev_id)))
            cur.execute(sql.SQL("CREATE TABLE IF NOT EXISTS {0}.{1} (time TIMESTAMP)").format(
                *tuple(map(sql.Identifier, [dev_id, measurement]))))
            cur.execute(sql.SQL("SELECT create_hypertable('{0}.{1}', 'time', chunk_time_interval => INTERVAL '1 day', if_not_exists => TRUE)").format(
                *tuple(map(sql.Identifier, [dev_id, measurement]))))
        except Exception as e:
            self.glog.error(f"psql error: {e}")
            return { 'Error': True, 'Reason': f'psql error: {e}' }

        clist = ['time']
        try:
            keys = ['fields', 'tags']
            for key in keys:
                if key not in data[0]:
                    data[0][key] = {}
            for col in data[0]['fields']:
                clist.append(col)
                cur.execute(sql.SQL('ALTER TABLE {0}.{1} ADD COLUMN IF NOT EXISTS {2} FLOAT DEFAULT NULL').format(
                    *tuple(map(sql.Identifier, [dev_id, measurement, col]))))
            for col in data[0]['tags']:
                clist.append(col)
                cur.execute(sql.SQL('ALTER TABLE {0}.{1} ADD COLUMN IF NOT EXISTS {2} VARCHAR(128) DEFAULT NULL').format(
                    *tuple(map(sql.Identifier, [dev_id, measurement, col]))))
        except Exception as e:
            self.glog.error(f'Could not save data to DB! --- {e} --- {dev_id} {measurement} length: {len(data)}')
            return { 'Error': True, 'Reason': f'psql error: {e}' }

        # fkn query
        #q = sql.SQL("INSERT INTO {0}.{1} ({2}) VALUES ({3})").format(
        #        *tuple(map(sql.Identifier, [dev_id, measurement])),
        #        sql.SQL(', ').join(map(sql.Identifier, clist)),
        #        sql.SQL(', ').join(sql.Placeholder() * len(clist)))
        q = sql.SQL("INSERT INTO {0}.{1} ({2}) VALUES %s").format(
                *tuple(map(sql.Identifier, [dev_id, measurement])),
                sql.SQL(', ').join(map(sql.Identifier, clist)))
        data = self.to_db_format(data, clist)
        try:
            #psycopg2.extras.execute_batch(cur, q, data)
            psycopg2.extras.execute_values(cur, q, data)
            return  { 'Error': False, 'Reason': f'Insert Success.' }
        except Exception as e:
            self.glog.error(f'Could not save data to DB! --- {e} --- {dev_id} {measurement} length: {len(data)}')
            return { 'Error': True, 'Reason': f'psql error: {e}' }

    def to_db_format(self, data, clist):
        """
        takes list of data dicts and a list with key names
        returns list of data tuples with values from data dict in order of key list
        TODO error checking?
        """
        keys = ['fields', 'tags']
        for i, d in enumerate(data):
            tmp = []
            tmp.append(d['time'])
            for key in keys:
                if key not in d:
                    d[key] = {}
            for k in clist:
                if k in d['fields'].keys():
                    tmp.append(d['fields'][k])
                elif k in d['tags'].keys():
                    tmp.append(d['tags'][k])
            data[i] = tuple(tmp)
        return data

    def from_db_format(self, data, clist):
        """
        takes list of data tuples with values from data dict in order of key list
        returns list of data dicts with 'fields' key for float values and 'tags' key for strings
        TODO error checking?
        """
        for i, d in enumerate(data):
            tmp = {}
            tmp['fields'] = {}
            tmp['tags'] = {}
            for j, k in enumerate(clist):
                if k == 'time':
                    tmp[k] = d[j].isoformat(sep=' ')
                elif type(d[j]) in [int, float]:
                    tmp['fields'].update({k: d[j]})
                elif type(d[j]) is str:
                    tmp['tags'].update({k: d[j]})
            data[i] = tmp
        return data

def timescale_process(kcfg):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    kcfg['context'] = Kontext()
    kcfg['loop'] = loop
    
    timescale = KTimescale(**kcfg)
    timescale.start()
