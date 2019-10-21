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
import socket
import asyncio
from zmq.utils.strtypes import asbytes
from datetime import datetime as dt
import time
 
import random

from ..lib.kernel import GK
from ..lib.kontext import Kontext
from ..lib.auth import GAuthClient

from pprint import pprint

class KUplink(GAuthClient, GK):
    def __init__(self, *args, **kwargs):
        GK.__init__(self, *args, **kwargs)
        # FIXME maybe do this nice or not at all
        self.auth_cfg = {
            'keys_path': kwargs['keys_path'],
            'client_key': kwargs['client_key'],
            'server_key': kwargs['server_key'],
            'hostname': kwargs['hostname'],
            'port': kwargs['port']
        }

        self.FRO = "ipc:///tmp/frontend"
        self.fro = self.context.socket(zmq.DEALER)
        #self.fro.setsockopt(zmq.IDENTITY, asbytes(self.name))
        #self.fro.setsockopt(zmq.LINGER, 0)
        self.fro.connect(self.FRO)

        self.loop.create_task(self.heartbeat())
        self.loop.create_task(self.upload_data())

    async def upload_data(self):
        upl = GAuthClient(**self.auth_cfg)
        while True:
            rand_sleep = round(random.uniform(2.5,4.5), 2)
            await asyncio.sleep(60*rand_sleep)
            #await asyncio.sleep(5)
            # greetings!
            earthling = True
            await upl.client.dsend(['greetings'])
            route, earthling = await upl.client.drecv()
            #self.glog.debug(f'UPLINK got greeting ({earthling}) from {uplink}')

            start_time = time.time()

            # info
            remote_info = {}
            await upl.client.dsend(['info'])
            route, remote_info = await upl.client.drecv()
            #print(route, remote_info)

            # get remote store
            store_remote = {}
            store_query = ['json', 'get', 'device_state_db', remote_info['dev_id'], 'head']
            await upl.client.dsend(store_query)
            route, store_remote = await upl.client.drecv()
            try:
                store_remote = store_remote['device_state_db'][remote_info['dev_id']].pop('store')
                #print(route, store_remote)
            except Exception as e:
                self.glog.error(f'trouble getting remote store on {self.auth_cfg["hostname"]}')
                continue

            # get local state 
            state = {}
            inv_query = ['json', 'get', 'device_state_db', self.dev_id, 'head']
            await self.fro.dsend(inv_query)
            route, state = await self.fro.drecv()
            state = state['device_state_db']

            # update remote state
            upup = ['json', 'nupsert', 'device_state_db', self.dev_id, state[self.dev_id]]
            await upl.client.dsend(upup)
            route, response = await upl.client.drecv()

            #print(self.name)
            #pprint('Local Inventory: ', state)
            #pprint('Remote Store: ', store_remote)
            #self.glog.debug(f'Local Inventory ---- {state}')
            #self.glog.debug(f'Remote Store ---- {store_remote}')

            for col in state[self.dev_id]['inventory']:
                segment = {}
                ## full upload
                try:
                    segment['start'] = state[self.dev_id]['inventory'][col]['tail']['time']
                    segment['stop'] = state[self.dev_id]['inventory'][col]['head']['time']
                except:
                    # FIXME leftovers?
                    continue
                if self.dev_id in store_remote:
                    if col in store_remote[self.dev_id]:
                        ## upload increment
                        if 'head' in store_remote[self.dev_id][col]:
                            segment['start'] = store_remote[self.dev_id][col]['head']['time']
                            segment['stop'] = state[self.dev_id]['inventory'][col]['head']['time']
                            #print('increment')
                #print(segment)
                if segment['start'] == segment['stop']:
                    continue
                cmd = ['series', 'chunk', self.dev_id, col]
                self.glog.info(f'Uploading ({self.name}): collection {col} segment {segment}')
                await upl.client.upstream(cmd, segment, source=self.fro, compression=False)

            self.glog.info(f'Uploaded state snapshot to: {self.auth_cfg["hostname"]}')
            stop_time = time.time()
            self.glog.info(f'Upload took: {round((stop_time-start_time), 3)} s')

    async def heartbeat(self):
        upl = GAuthClient(**self.auth_cfg)
        self.glog.info(f'Starting uplink {self.name}.')
        while True:
            await asyncio.sleep(10)
            # greetings!
            await upl.client.dsend(['greetings'])
            route, earthling = await upl.client.drecv()

            start_time = time.time()
            tmst = dt.utcnow()

            # update remote db
            up_request = ['json', 'nupsert', 'device_state_db', self.dev_id, {'seen': tmst.isoformat(sep=' '), 'dev_id': self.dev_id}]
            await upl.client.dsend(up_request)
            route, raw = await upl.client.drecv()
            dev_db = ['json', 'nupsert', 'device_db', self.dev_id , {'dev_id': self.dev_id, 'version': self.version}]
            await upl.client.dsend(dev_db)
            route, raw = await upl.client.drecv()

            now = dt.utcnow()
            if (now-tmst).seconds > 10: ## 10sec is considered timeout
                self.glog.info("Heart lost at: {0} --- Connection reestablished at {1}".format(dt.fromtimestamp(tmst), dt.fromtimestamp(now)))
            stop_time = time.time()
            self.glog.debug(f'({self.name}: {self.auth_cfg["hostname"]}) Heartbeat round trip: {round((stop_time-start_time)*1000, 1)} ms')

def uplink_process(kcfg):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    kcfg['context'] = Kontext()
    kcfg['loop'] = loop

    upl = KUplink(**kcfg)
    upl.start()
