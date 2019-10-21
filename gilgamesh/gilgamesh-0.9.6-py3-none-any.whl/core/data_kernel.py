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
import zmq
import random
import json
import time
import asyncio
from zmq.utils.strtypes import asbytes

from ..lib.kernel import GK
from ..lib.kontext import Kontext

from datetime import datetime as dt
from datetime import timedelta as td
from pprint import pprint
from collections import defaultdict

class GData(GK):
    def __init__(self, *args, **kwargs):
        self.loop = kwargs['loop']
        self.context = kwargs['context']
        self.name = kwargs['name']

        self.BUFFER_MAX_AGE = td(seconds=kwargs['buffer_max_age'])
        self.BUFFER_MAX_SIZE = kwargs['buffer_max_size']
        self.VACUUM_INTERVAL = kwargs['vacuum_interval']
        self.buffer_map = defaultdict(dict)

        self.DIN = 'ipc:///tmp/data_in'
        self.PUB = f'tcp://0.0.0.0:{kwargs["port"]}'

        self.FRO = "ipc:///tmp/frontend"
        self.fro = self.context.socket(zmq.DEALER)
        self.fro.connect(self.FRO)

        self.DOUT = 'ipc:///tmp/data_out'
        self.outbound = self.context.socket(zmq.PUSH)
        self.outbound.bind(self.DOUT)

        GK.__init__(self, *args, **kwargs)

        self.loop.create_task(self.relay())
        self.loop.create_task(self.vacuum())

    async def relay(self):
        """doc
        """
        inbound = self.context.socket(zmq.PULL)
        inbound.bind(self.DIN)

        pub = self.context.socket(zmq.PUB)
        pub.bind(self.PUB)
        pub.setsockopt(zmq.CONFLATE, 1)

        while True:
            # zerocopy without pub
            #msg = await inbound.recv(copy=False)
            #await outbound.send(msg, copy=False)

            msg = await inbound.precv()
            #self.glog.debug(f'Got data: {msg}')

            # single points get published
            # data blocks > buffer size get redirected to database immediately
            if len(msg[-1]) == 1:
                pub.send_string(f'{msg[0]} {msg[1]} {json.dumps(msg[-1][0])}')
                # CAVEAT FIXME subscribers need to filter with `["` as prefix
                # no multipart message possible with conflate
                # TESTME maybe it is?!
            elif len(msg[-1]) >= self.BUFFER_MAX_SIZE:
                await self.outbound.psnd(msg)
                continue
            else:
                pass

            db, tb = (msg[0], msg[1])

            # create mapping for new data
            if not db in self.buffer_map:
                self.buffer_map[db] = {}
            if not tb in self.buffer_map[db]:
                self.buffer_map[db][tb] = {}

            # new data needs a data map created
            # if data is empty a new era begins
            if not 'data' in self.buffer_map[db][tb]:
                self.buffer_map[db][tb]['data'] = []
                self.buffer_map[db][tb]['age'] = dt.utcnow()
            elif not len(self.buffer_map[db][tb]['data']):
                self.buffer_map[db][tb]['age'] = dt.utcnow()
            else:
                pass

            # FIXME this should not have to be done here!
            if isinstance(msg[-1], dict):
                msg[-1] = [msg[-1]]

            # change and save tags only on change
            if not 'tags' in self.buffer_map[db][tb]:
                if not 'tags' in msg[-1][-1]:
                    self.buffer_map[db][tb]['tags'] = {}
                else:
                    self.buffer_map[db][tb]['tags'] = msg[-1][-1]['tags']
            elif self.buffer_map[db][tb]['tags'] == msg[-1][-1]['tags']:
                msg[-1][-1]['tags'] = dict.fromkeys(msg[-1][-1]['tags'], None)
            else:
                self.buffer_map[db][tb]['tags'] = msg[-1][-1]['tags']

            #if len(self.buffer_map[db][tb]['data']) >= self.BUFFER_MAX_SIZE:
            #    await self.outbound.psnd([ db, tb, self.buffer_map[db][tb]['data']])
            #    self.buffer_map[db][tb]['data'] = msg[-1]
            #    continue
            #else:
            self.buffer_map[db][tb]['data'].extend(msg[-1])

    async def vacuum(self):
        """doc
        empty buffer map periodically
        """
        while True:
            await asyncio.sleep(self.VACUUM_INTERVAL)
            for db in self.buffer_map.keys():
                for tb in self.buffer_map[db].keys():
                    if ( (dt.utcnow() - self.buffer_map[db][tb]['age']) > self.BUFFER_MAX_AGE
                            or len(self.buffer_map[db][tb]['data']) >= self.BUFFER_MAX_SIZE
                            and len(self.buffer_map[db][tb]['data']) > 0 ):
                        await self.outbound.psnd([db, tb, self.buffer_map[db][tb]['data']])
                        self.buffer_map[db][tb]['data'] = []
                        self.buffer_map[db][tb]['age'] = dt.utcnow()
                    else:
                        pass


def data_kernel_process(kcfg):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    kcfg['context'] = Kontext()
    kcfg['loop'] = loop
    
    data = GData(**kcfg)
    data.start()
