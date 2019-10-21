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
from multiprocessing import Process

import sys
import zmq
import json
import syslog
import logging
from datetime import datetime

import asyncio
from zmq.asyncio import Poller
from zmq.utils.strtypes import asbytes
from zmq.devices import ProcessDevice

from ..lib.data import GData
from ..lib.logging import GLog
from ..lib.heart import GHeartt

from pprint import pprint

class GResourceManager(GHeartt, GLog, GData):
    def __init__(self, kernel_map, name="ResourceManager", *args, **kwargs):
        self.loop = kwargs['loop']
        self.context = kwargs['context']
        self.dev_id = kwargs['device_id']
        self.version = kwargs['version']

        self.kernel_map = kernel_map
        self.name = name

        # whyyyy
        #super().__init__()
        GHeartt.__init__(self, *args, **kwargs)
        GData.__init__(self, *args, **kwargs)
        GLog.__init__(self, *args, **kwargs)

        # 'frontend' <-> 'backend' proxy (polled)
        self.FRO = "ipc:///tmp/frontend"
        self.BAC = "ipc:///tmp/backend"
        #self.fro = self.context.socket(zmq.ROUTER)
        #self.fro.bind(self.FRO)
        #self.bac = self.context.socket(zmq.DEALER)
        #self.bac.bind(self.BAC)
        ## Initialize poll set
        #self.poller = Poller()
        #self.poller.register(self.fro, zmq.POLLIN)
        #self.poller.register(self.bac, zmq.POLLIN)
        # FIXME/TESTME
        # split relay off of resource manager as process device?
        # or own kernel?
        # 'frontend' <-> 'backend' proxy process device
        devx = ProcessDevice(zmq.QUEUE, zmq.ROUTER, zmq.DEALER)
        devx.bind_in(self.FRO)
        devx.bind_out(self.BAC)
        devx.start()

        # resource_worker <-> database proxy for storage workers
        for res_type in kwargs['resource_types']:
            sdev = ProcessDevice(zmq.QUEUE, zmq.ROUTER, zmq.DEALER)
            sdev.bind_in(f'ipc:///tmp/{res_type}_in')
            sdev.bind_out(f'ipc:///tmp/{res_type}_out')
            sdev.start()

    async def resource_task(self):
        """
        pipeline for resource requests to resource workers
        FIXME implement inter broker routing here?
        FIXME tight now a process device is used. this is dead code?
        """
        while True:
            socks = dict(await self.poller.poll())

            if socks.get(self.fro) == zmq.POLLIN:
                message = await self.fro.recv_multipart(copy=False)
                #self.glog.debug("frontend in: {0}".format(message))
                await self.bac.send_multipart(message, copy=False)

            if socks.get(self.bac) == zmq.POLLIN:
                message = await self.bac.recv_multipart(copy=False)
                #self.glog.debug("frontend out: {0}".format(message))
                await self.fro.send_multipart(message, copy=False)

    async def start_kernels(self):
        # start delayed wait for logger etc...
        await asyncio.sleep(1)
        for n, kernel in enumerate(self.kernel_map):
            self.init_kernel(kernel, n)
            self.config_kernel(kernel, n)
        return

    def init_kernel(self, kernel, n):
        self.kernel_map[n]['proc'] = Process(target=kernel['function'], args=(kernel['config'],))
        self.kernel_map[n]['proc'].start()
        self.glog.info(f'Starting Kernel {kernel["name"]} with PID {self.kernel_map[n]["proc"].pid}')

    # TODO
    # MAYBE???
    def config_kernel(self, kernel, n):
        """
        set log level
        set logging True/False
        pause kernel?
        """
        pass

    async def logger_task(self):
        """TODO: Fix logger formatting and message handling!!!!"""
        """TODO: filter logging for kernels (self.kernel_map) OR control kernel logging behavior!!!!"""
        s = self.context.socket(zmq.SUB)
        s.bind(self.LOG_DEST)
        s.subscribe(b'')
        while True:
            msg = await s.recv_multipart()
            #print(msg)
            level, message = msg
            message = message.decode('ascii')
            if message.endswith('\n'):
                message = message[:-1]
            log = getattr(logging, level.lower().decode('ascii'))
            syslog.syslog(message)

    def start(self):
        # try me!
        #self.loop.create_task(self.resource_task())
        self.loop.create_task(self.logger_task())
        self.loop.create_task(self.heartbeater())
        self.loop.create_task(self.handle_pong())
        self.loop.create_task(self.start_kernels())

    def terminate(self):
        return
