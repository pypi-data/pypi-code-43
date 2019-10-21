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
from ..lib.auth import GAuthClient

import time

class KNoStorage(GAuthClient, GK):
    def __init__(self, *args, **kwargs):
        GK.__init__(self, *args, **kwargs)
        GAuthClient.__init__(self, *args, **kwargs)

        storage_type = kwargs['storage_type']
        self.DB = f'ipc:///tmp/{storage_type}_out'

        self.loop.create_task(self.query_task())

        # are we responsible for time series data?
        if storage_type == 'series':
            self.DOUT = "ipc:///tmp/data_out"
            self.receiver = self.context.socket(zmq.PULL)
            self.receiver.connect(self.DOUT)
            self.loop.create_task(self.upload_data())

    async def query_task(self):
        """
        relay query to uplink!
        """
        dbq = self.context.socket(zmq.REP)
        dbq.connect(self.DB)
        while True:
            raw = await dbq.precv()
            await self.client.dsend(raw)
            _, response = await self.client.drecv()
            await dbq.psnd(response)
            #self.glog.debug(f'route:{route} - earth: {earthling} - sent: {raw}')
           

    async def upload_data(self):
        while True:
            raw = await self.receiver.precv()
            up = ['series', 'upload']
            up.extend(raw)
            await self.client.dsend(up)
            route, earthling = await self.client.drecv()
            #self.glog.debug(f'route:{route} - earth: {earthling} - sent: {raw}')

def nostorage_process(kcfg):
    kcfg['base_dir'] = os.path.dirname(__file__)
    # FIXME -> get uplink info from config!!!
    kcfg['uplink'] = {
            'hostname': 'ggm-gw.local',
            'key_name': 'gateway',
    }

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    kcfg['context'] = Kontext()
    kcfg['loop'] = loop
    
    mongo = KNoStorage(**kcfg)
    mongo.start()
