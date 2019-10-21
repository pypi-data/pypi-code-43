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

from .logging import GLog
from .heart import GHeartt
from .data import GData
from pprint import pprint

from time import sleep

class GK(GData, GHeartt, GLog):
    """
    gilgamesh kernel
    composes logger, heart, and data classes
    adds control coroutine
    """
    def __init__(self, *args, **kwargs):
        self.loop = kwargs['loop']
        self.context = kwargs['context']
        self.dev_id = kwargs['device_id']
        self.name = kwargs['name']
        self.version = kwargs['version']
        # Y U NO WORK???
        #super().__init__()
        GData.__init__(self, *args, **kwargs)
        GHeartt.__init__(self, *args, **kwargs)
        GLog.__init__(self, *args, **kwargs)

        sleep(2)

    async def control(self):
        """
        TODO:
        set log lvl
        stop self?
        extensions via superclass?
        """
        sname = "ipc:///tmp/ctrl_{0}".format(self.name)
        rep = self.context.socket(zmq.REP)
        rep.connect(sname)
        while True:
            raw = await rep.precv()
            await rep.psnd(raw)

    def start(self, *args, **kwargs):
        self.loop.create_task(self.start_heart())
        self.loop.run_forever()

    def stop(self, *args, **kwargs):
        """
        TODO
        do a nice termination...
        """
        self.glog.info('Stopping Kernel {0} gracefully.'.format(self.name))
        self.loop.stop()
        sys.exit(0)
