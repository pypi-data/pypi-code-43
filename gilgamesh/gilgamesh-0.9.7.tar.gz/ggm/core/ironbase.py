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
from zmq.asyncio import Poller
from zmq.utils.strtypes import asbytes

from ..lib.kernel import GK
from ..lib.kontext import Kontext
from ..lib.auth import GAuthServer

class GIronBase(GAuthServer, GK):
    def __init__(self, *args, **kwargs):
        GK.__init__(self, *args, **kwargs)
        GAuthServer.__init__(self, *args, **kwargs)

        self.fro = self.context.socket(zmq.DEALER)
        self.fro.setsockopt(zmq.IDENTITY, asbytes(self.name))
        self.fro.connect("ipc:///tmp/frontend")

        # Initialize poll set
        self.poller = Poller()

        self.poller.register(self.fro, zmq.POLLIN)
        self.poller.register(self.server, zmq.POLLIN)

    async def recv_data(self):
        while True:
            socks = dict(await self.poller.poll())

            if socks.get(self.server) == zmq.POLLIN:
                message = await self.server.recv_multipart()
                #print(f'coming in: {message}')
                """
                FIXME: This should be protocol code! (e.g. flatbuffers?)
                FIXME: Should this be protocol code? (e.g. flatbuffers?)
                if "greetings" in message[-1].decode():
                    await self.fro.send_multipart(message)
                else:
                    await self.fro.send_multipart(message)
                """
                await self.fro.send_multipart(message)

            if socks.get(self.fro) == zmq.POLLIN:
                message = await self.fro.recv_multipart()
                #print(f'coming out: {message}')
                await self.server.send_multipart(message)


def ironbase_process(kcfg):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    kcfg['context'] = Kontext()
    kcfg['loop'] = loop

    irn = GIronBase(**kcfg)
    loop.create_task(irn.recv_data())
    irn.start()
