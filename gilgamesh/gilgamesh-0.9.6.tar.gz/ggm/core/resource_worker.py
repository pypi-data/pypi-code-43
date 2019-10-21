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
import os
import zmq
import asyncio

from ..lib.kernel import GK
from ..lib.kontext import Kontext

class KResourceWorker(GK):
    """
    provides a basic REST-like API to resources

    """
    def __init__(self, *args, **kwargs):
        GK.__init__(self, *args, **kwargs)

        self.storage_cfg = kwargs['resource_types']

        self.BAC = 'ipc:///tmp/backend'
        self.bac = self.context.socket(zmq.DEALER)
        self.bac.connect(self.BAC)

        for res_type in self.storage_cfg:
            if res_type == 'json':
                self.json_DB = f'ipc:///tmp/json_in'
                self.json_db = self.context.socket(zmq.REQ)
                self.json_db.connect(self.json_DB)
            elif res_type == 'series':
                self.series_DB = f'ipc:///tmp/series_in'
                self.series_db = self.context.socket(zmq.REQ)
                self.series_db.connect(self.series_DB)
            else:
                self.glog.error('No known storage adapter configured!')


        # tricky!! (context/socket wise)
        #count = kwargs['count']
        #for i in range(count):
        #    self.loop.create_task(self.work(i))
        self.loop.create_task(self.work())

    async def get_all(self, resource_sock, dbs, colls, cmd):
        reply = {}
        for i, db in enumerate(dbs):
            reply[db] = {}
            for coll in colls[i]:
                query = ['get', db, coll, cmd]
                await resource_sock.psnd(query)
                reply[db][coll] = await resource_sock.precv()
        return reply

    async def work(self, i=0):
        """
        this is the glue between
        application logic and backend logic
        it aims to provide peaceful coexistence of multiple protocols

        TODO
        *zero copy* for payload (last frame in multipart) only would be nice
        """
        me = i
        while True:
            # 'filter' flags
            http_get = False
            http_post = False

            z_route, raw = await self.bac.drecv()
            #print(f'RW: {z_route} {raw}')
            #self.glog.info(f'RW: {z_route} {raw}')
            try:
                # unwrap present
                sig = raw.pop(0)
                sig_typ = sig
            except Exception as e:
                self.glog.error(f'RW({me}) received strange signal -- {0}'.format(e))
                await self.bac.dsend_err('fuck you too!', z_route)
                continue

            #print(sig)
            """
            FIXME: This should be protocol code! (e.g. flatbuffers?)
            FIXME: Should this be protocol code? or zmq router/dealer identity?
            """
            #
            ## sieve http requests
            #
            if sig == 'http-get':
                try:
                    sig = raw.pop(0)
                    sig_typ = sig
                except:
                    await self.bac.dsend_err('', z_route)
                    continue
                if sig not in ['json', 'series']:
                    await self.bac.dsend_err('http-get signal error.', z_route)
                    continue
                http_get = True
            elif sig == "http-post":
                try:
                    sig = raw.pop(0)
                    sig_typ = sig
                except:
                    await self.bac.dsend_err('', z_route)
                    continue
                if sig not in ['json', 'series']:
                    await self.bac.dsend_err('http-post signal error.', z_route)
                    continue
                http_post = True
            else:
                pass

            #
            ## sieve/validate
            #
            if sig == "greetings":
                await self.bac.dsend(['earthlings'], z_route)
                continue
            elif sig == "info":
                await self.bac.dsend({'dev_id': self.dev_id, 'version': self.version}, z_route)
                continue
            #elif sig == "cache":
            #    try:
            #        sig = raw[0]
            #    except:
            #        await self.bac.dsend_err('', z_route)
            #        continue
            #    if sig not in ['get', 'insert']:
            #        await self.bac.dsend_err('cache signal error.', z_route)
            #        continue
            #    resource_sock = self.cache
            elif sig == "series":
                try:
                    sig = raw[0]
                except:
                    await self.bac.dsend_err('', z_route)
                    continue
                if http_get:
                    if sig not in ['get']:
                        await self.bac.dsend_err('http-get signal error.', z_route)
                        continue
                if http_post:
                    if sig not in ['insert']:
                        await self.bac.dsend_err('http-post signal error.', z_route)
                        continue
                if sig not in ['measurements', 'count', 'get', 'upload', 'insert', 'delete', 'chunk', 'inventory']:
                    await self.bac.dsend_err('series signal error.', z_route)
                    continue
                resource_sock = self.series_db
            elif sig == "json":
                try:
                    sig = raw[0]
                except:
                    await self.bac.dsend_err('', z_route)
                    continue
                if http_get:
                    if sig not in ['get']:
                        await self.bac.dsend_err('http-get signal error.', z_route)
                        continue
                if http_post:
                    if sig not in ['insert', 'nupsert']:
                        await self.bac.dsend_err('http-post signal error.', z_route)
                        continue
                if sig not in ['get', 'insert', 'nupsert', 'delete']:
                    await self.bac.dsend_err('json signal error.', z_route)
                    continue
                resource_sock = self.json_db
            else:
                await self.bac.dsend_err('signal error.', z_route)
                continue


            # redirect directly if nostorage is being used
            # FIXME loop over resource types -> if storage_cfg[resource_type] == 'nostorage'
            if ((self.storage_cfg["series"] == 'nostorage' and sig_typ == 'series')
                or (self.storage_cfg["json"] == 'nostorage' and sig_typ == 'json')):
                raw.insert(0, sig_typ)
                await resource_sock.psnd(raw)
                reply = await resource_sock.precv()
                await self.bac.dsend(reply, z_route)
                continue
            #
            ## operations
            #
            #print(raw)
            if sig == "get":
                try:
                    cmd = raw.pop(0)
                    tmp = raw.pop(0)
                except Exception as e:
                    self.glog.error(f'Error while parsing get: {e}')
                    await self.bac.dsend_err('No database specified.', z_route)
                    continue

                if tmp == 'all':
                    dbs = [self.dev_id]
                else:
                    dbs = [tmp]

                try:
                    tmp = raw.pop(0)
                except Exception as e:
                    self.glog.error(f'Error while parsing get: {e}')
                    await self.bac.dsend_err('No collection specified.', z_route)
                    continue

                if tmp == 'all':
                    colls = []
                    for db in dbs:
                        query = ['measurements', db]
                        await resource_sock.psnd(query)
                        colls.append(await resource_sock.precv())
                else:
                    colls = [[tmp]]

                try:
                    cmds = raw.pop(0)
                except Exception as e:
                    self.glog.error(f"Error while parsing get: {e}")
                    await self.bac.dsend_err('No action specified.', z_route)
                    continue

                reply = {}
                reply = await self.get_all(resource_sock, dbs, colls, cmds)

                await self.bac.dsend(reply, z_route)
                continue

            elif sig == 'insert':
                """
                insert document in collection
                """
                try:
                    cmd = raw.pop(0)
                    db = raw.pop(0)
                    coll = raw.pop(0)
                    doc = raw.pop(0)
                except Exception as e:
                    self.glog.error(f"Error while parsing insert: {e}")
                    await self.bac.dsend_err('Error parsing insert query.', z_route)
                    continue

                query = [cmd, db, coll, doc]

                if sig_typ == 'series':
                    query.pop(0)
                    await self.send_batch(query)
                    await self.bac.dsend({'Error': False, 'Reason': 'all is good'}, z_route)
                    continue
                else:
                    await resource_sock.psnd(query)
                    reply = await resource_sock.precv()
                    await self.bac.dsend(reply, z_route)
                    continue

            elif sig == 'nupsert':
                """
                update newest document in collection or create one and insert
                """
                try:
                    cmd = raw.pop(0)
                    db = raw.pop(0)
                    coll = raw.pop(0)
                    doc = raw.pop(0)
                except Exception as e:
                    self.glog.error(f"Error while parsing nupsert: {e}")
                    await self.bac.dsend_err('Error parsing nupsert query.', z_route)
                    continue

                query = [cmd, db, coll, doc]

                await resource_sock.psnd(query)
                reply = await resource_sock.precv()

                await self.bac.dsend(reply, z_route)
                continue

            elif sig == 'delete':
                """
                delete
                only tables are deleteable (no databases)
                tables need a column called deleteable with a value within the last 5min
                """
                try:
                    cmd = raw.pop(0)
                    db = raw.pop(0)
                    coll = raw.pop(0)
                    query = [cmd, db, coll]
                    # jsqlite demands more 'levels'
                    if isinstance(raw, list) and len(raw) > 0:
                        query.extend(raw)
                except Exception as e:
                    self.glog.error(f"Error while parsing delete: {e}")
                    await self.bac.dsend_err('Error parsing delete query.', z_route)
                    continue

                await resource_sock.psnd(query)
                reply = await resource_sock.precv()

                await self.bac.dsend(reply, z_route)
                continue

            elif sig == "upload":
                raw.pop(0)
                if len(raw) > 0: 
                    await self.send_batch(raw)
                    await self.bac.dsend(['OK'], z_route)
                    continue
                else:
                    await self.bac.dsend_err("data empty!", z_route)
                    continue

            elif sig == "chunk":
                try:
                    cmd = raw.pop(0)
                    db = raw.pop(0)
                    coll = raw.pop(0)
                    params = raw.pop(0)
                except Exception as e:
                    self.glog.error(f"Error while parsing Download: {e}")
                    await self.bac.dsend_err('Error parsing Download query.', z_route)
                    continue

                query = [cmd, db, coll, params]

                await resource_sock.psnd(query)
                records = await resource_sock.precv()

                await self.bac.dsend(records, z_route)
                continue

            elif sig == 'measurements':
                try:
                    cmd = raw.pop(0)
                    db = raw.pop(0)
                except Exception as e:
                    self.glog.error(f"Error parsing measurement query: {e}")
                    await self.bac.dsend_err('Error parsing measurement query', z_route)
                    continue
                await resource_sock.psnd(['measurements', db]) # here you can create loops by asking for it
                colls = await resource_sock.precv()
                await self.bac.dsend(colls, z_route)

            elif sig == 'count':
                try:
                    cmd = raw.pop(0)
                    db = raw.pop(0)
                    measurement = raw.pop(0)
                    query = [cmd, db, measurement]
                    if len(raw) == 1:
                        query.extend(raw)
                except Exception as e:
                    self.glog.error(f"Error parsing count query: {e}")
                    await self.bac.dsend_err('Error parsing count query', z_route)
                    continue
                await resource_sock.psnd(query)
                colls = await resource_sock.precv()
                await self.bac.dsend(colls, z_route)

            elif sig == "inventory":
                try:
                    cmd = raw.pop(0)
                    db = raw.pop(0)
                    tmp = raw.pop(0)
                    state = {}
                    state['inventory'] = {}
                    # TODO
                    state['store'] = {}
                except Exception as e:
                    self.glog.error(f"Error while parsing inventory: {e}")
                    await self.bac.dsend_err('Error parsing inventory query', z_route)
                    continue

                if tmp == 'all':
                    query = ['measurements', db]
                    await resource_sock.psnd(query)
                    colls = await resource_sock.precv()
                else:
                    colls = [tmp]

                for coll in colls:
                    state['inventory'][coll] = {}
                    try:
                        head_query = ['get', db, coll, 'head']
                        await resource_sock.psnd(head_query)
                        points = await resource_sock.precv()
                        state['inventory'][coll]['head'] = points.pop(0)

                        tail_query = ['get', db, coll, 'tail']
                        await resource_sock.psnd(tail_query)
                        points = await resource_sock.precv()
                        state['inventory'][coll]['tail'] = points.pop(0)
                    except Exception as e:
                        self.glog.error(f'Inventory update failed for {coll}: {e}')

                #print(state)
                await self.bac.dsend(state, z_route)
                continue

            else:
                await self.bac.dsend_err('Not so nice of you!', z_route)

def resource_worker_process(kcfg):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    kcfg['context'] = Kontext()
    kcfg['loop'] = loop

    data = KResourceWorker(**kcfg)
    data.start()
